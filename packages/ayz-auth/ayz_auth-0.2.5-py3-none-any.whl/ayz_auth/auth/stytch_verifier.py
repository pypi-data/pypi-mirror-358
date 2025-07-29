"""
Stytch B2B session token verification.

Handles verification of session tokens with the Stytch B2B API, including
caching, error handling, and session data extraction.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import stytch

from ..cache.redis_client import redis_client
from ..models.context import StytchContext
from ..utils.config import settings
from ..utils.exceptions import StytchAPIError, TokenVerificationError
from ..utils.logger import logger


class StytchVerifier:
    """
    Handles Stytch B2B session token verification with Redis caching.

    Provides a two-tier verification system:
    1. Check Redis cache for previously verified tokens
    2. Fall back to Stytch API for fresh verification
    """

    def __init__(self) -> None:
        self._client: Optional[stytch.B2BClient] = None

    def _get_client(self) -> stytch.B2BClient:
        """
        Get or create Stytch B2B client.

        Returns:
            Configured Stytch B2B client

        Raises:
            StytchAPIError: If client cannot be configured
        """
        if self._client is None:
            try:
                self._client = stytch.B2BClient(
                    project_id=settings.stytch_project_id,
                    secret=settings.stytch_secret,
                    environment=settings.stytch_environment,
                )
                logger.info("Stytch B2B client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Stytch client: {str(e)}")
                raise StytchAPIError(f"Stytch client initialization failed: {str(e)}")

        return self._client

    def _hash_token(self, token: str) -> str:
        """
        Create a hash of the token for cache key generation.

        Args:
            token: Session token to hash

        Returns:
            SHA256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def verify_session_token(self, token: str) -> StytchContext:
        """
        Verify session token with caching support.

        Args:
            token: Stytch session token to verify

        Returns:
            StytchContext with session data

        Raises:
            TokenVerificationError: If token verification fails
            StytchAPIError: If Stytch API is unreachable
        """
        token_hash = self._hash_token(token)

        # Try cache first
        cached_result = await self._get_cached_verification(token_hash)
        if cached_result:
            return self._build_context_from_cache(cached_result)

        # Fall back to Stytch API
        session_data = await self._verify_with_stytch_api(token)

        # Cache the result
        await self._cache_verification_result(token_hash, session_data)

        return self._build_context_from_stytch_data(session_data)

    async def _get_cached_verification(
        self, token_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached verification result.

        Args:
            token_hash: Hash of the token to look up

        Returns:
            Cached verification data if found and valid
        """
        try:
            cached_data = await redis_client.get_cached_verification(token_hash)
            if cached_data:
                # Check if cached session is still valid
                expires_at_str = cached_data.get("session_expires_at")
                if not expires_at_str or not isinstance(expires_at_str, str):
                    return None
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now(timezone.utc) < expires_at:
                    logger.debug("Using cached verification result")
                    return cached_data
                else:
                    logger.debug("Cached session expired, removing from cache")
                    await redis_client.delete_cached_verification(token_hash)

            return None

        except Exception as e:
            logger.warning(f"Cache lookup failed: {str(e)}")
            return None

    async def _verify_with_stytch_api(self, token: str) -> Dict[str, Any]:
        """
        Verify token directly with Stytch B2B API.

        Args:
            token: Session token to verify

        Returns:
            Raw session data from Stytch API

        Raises:
            TokenVerificationError: If token is invalid
            StytchAPIError: If API call fails
        """
        try:
            client = self._get_client()

            logger.debug("Verifying token with Stytch API")
            response = client.sessions.authenticate(session_token=token)

            # Debug the response type and content
            logger.debug(f"Response type: {type(response)}")
            logger.debug(
                f"Response status_code: {getattr(response, 'status_code', 'N/A')}"
            )

            if hasattr(response, "status_code") and response.status_code != 200:
                logger.warning(
                    f"Stytch API returned error: {response.status_code}",
                    extra={
                        "response": (
                            response.json()
                            if hasattr(response, "json")
                            else str(response)
                        )
                    },
                )
                raise TokenVerificationError(
                    "Invalid or expired session token", token_hint=token[:8] + "..."
                )

            # Handle different response formats from Stytch SDK
            session_data = None

            if hasattr(response, "json") and callable(response.json):
                # Response is an HTTP response object
                session_data = response.json()
                logger.debug("Parsed response using .json() method")
            elif isinstance(response, str):
                # Response is a JSON string - parse it
                try:
                    import json

                    session_data = json.loads(response)
                    logger.debug("Parsed response as JSON string")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON string response: {e}")
                    logger.error(
                        f"Raw response content: {response[:500]}..."
                    )  # First 500 chars
                    raise StytchAPIError(
                        "Invalid JSON response from Stytch API",
                        api_response={"error": f"JSON parse error: {str(e)}"},
                    )
            elif isinstance(response, dict):
                # Response is already a dictionary
                session_data = response
                logger.debug("Response is already a dictionary")
            elif hasattr(response, "__dict__"):
                # Response is a Stytch response object - convert to dict
                # Try to get the response data properly
                if hasattr(response, "member_session") and hasattr(response, "member"):
                    # Modern Stytch response object with direct attributes
                    member_session = getattr(response, "member_session", {})
                    member = getattr(response, "member", {})
                    organization = getattr(response, "organization", {})

                    # Convert objects to dicts if they're not already
                    if hasattr(member_session, "__dict__"):
                        member_session = member_session.__dict__
                    if hasattr(member, "__dict__"):
                        member = member.__dict__
                    if hasattr(organization, "__dict__"):
                        organization = organization.__dict__

                    session_data = {
                        "status_code": getattr(response, "status_code", 200),
                        "request_id": getattr(response, "request_id", ""),
                        "member_session": member_session,
                        "member": member,
                        "organization": organization,
                        "session_token": getattr(response, "session_token", ""),
                        "session_jwt": getattr(response, "session_jwt", ""),
                    }
                    logger.debug(
                        "Converted Stytch response object to dict using direct attributes"
                    )
                else:
                    # Fallback to __dict__
                    session_data = response.__dict__
                    logger.debug("Converted response object to dict using __dict__")
            else:
                # Response is some other format - try to get its attributes
                logger.warning(f"Unexpected response format: {type(response)}")
                logger.debug(
                    f"Response content: {str(response)[:200]}..."
                )  # First 200 chars
                session_data = vars(response) if hasattr(response, "__dict__") else {}

            # Validate we have the expected data structure
            if not isinstance(session_data, dict):
                logger.error(f"Session data is not a dict: {type(session_data)}")
                logger.error(f"Session data content: {str(session_data)[:200]}...")
                raise StytchAPIError(
                    "Invalid response format from Stytch API",
                    api_response={"error": f"Expected dict, got {type(session_data)}"},
                )

            # Check for required fields in the response
            # Stytch B2B API returns member_session instead of separate member/session
            if "member_session" not in session_data or "member" not in session_data:
                logger.error(
                    f"Missing required fields in session data: {list(session_data.keys())}"
                )
                raise StytchAPIError(
                    "Invalid session data format from Stytch API",
                    api_response={"error": "Missing member_session or member data"},
                )

            logger.info("Token verified successfully with Stytch API")
            logger.debug(f"Session data keys: {list(session_data.keys())}")
            return session_data

        except TokenVerificationError:
            # Re-raise token verification errors as-is
            raise

        except Exception as e:
            logger.error(f"Stytch API verification failed: {str(e)}", exc_info=True)
            raise StytchAPIError(
                f"Failed to verify token with Stytch: {str(e)}",
                api_response={"error": str(e)},
            )

    async def _cache_verification_result(
        self, token_hash: str, session_data: Dict[str, Any]
    ) -> None:
        """
        Cache verification result for future use.

        Args:
            token_hash: Hash of the verified token
            session_data: Session data from Stytch API
        """
        try:
            # Extract essential data for caching
            # Handle both dict and object formats from Stytch SDK
            member_data = session_data.get("member", {})
            session_data_inner = session_data.get("member_session", {})
            organization_data = session_data.get("organization", {})

            # Helper function to safely get attribute from object or dict
            def safe_get(obj, attr, default=None):
                if hasattr(obj, attr):
                    return getattr(obj, attr)
                elif isinstance(obj, dict):
                    return obj.get(attr, default)
                return default

            cache_data = {
                "member_id": safe_get(member_data, "member_id")
                or safe_get(session_data_inner, "member_id"),
                "session_id": safe_get(session_data_inner, "member_session_id"),
                "organization_id": safe_get(organization_data, "organization_id")
                or safe_get(session_data_inner, "organization_id"),
                "session_started_at": safe_get(session_data_inner, "started_at"),
                "session_expires_at": safe_get(session_data_inner, "expires_at"),
                "session_last_accessed_at": safe_get(
                    session_data_inner, "last_accessed_at"
                ),
                "member_email": safe_get(member_data, "email_address"),
                "member_name": safe_get(member_data, "name"),
                "session_custom_claims": safe_get(
                    session_data_inner, "custom_claims", {}
                ),
                "authentication_factors": safe_get(
                    session_data_inner, "authentication_factors", []
                ),
                "raw_session_data": session_data,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }

            await redis_client.cache_verification_result(token_hash, cache_data)

        except Exception as e:
            logger.warning(f"Failed to cache verification result: {str(e)}")
            # Don't raise - caching failures should be non-fatal

    def _build_context_from_cache(self, cached_data: Dict[str, Any]) -> StytchContext:
        """
        Build StytchContext from cached verification data.

        Args:
            cached_data: Cached session data

        Returns:
            StytchContext instance
        """
        # Handle datetime fields safely
        started_at = cached_data.get("session_started_at")
        expires_at = cached_data.get("session_expires_at")
        last_accessed_at = cached_data.get("session_last_accessed_at")

        return StytchContext(
            member_id=cached_data["member_id"],
            session_id=cached_data["session_id"],
            organization_id=cached_data["organization_id"],
            session_started_at=(
                datetime.fromisoformat(started_at)
                if started_at
                else datetime.now(timezone.utc)
            ),
            session_expires_at=(
                datetime.fromisoformat(expires_at)
                if expires_at
                else datetime.now(timezone.utc)
            ),
            session_last_accessed_at=(
                datetime.fromisoformat(last_accessed_at)
                if last_accessed_at
                else datetime.now(timezone.utc)
            ),
            member_email=cached_data.get("member_email"),
            member_name=cached_data.get("member_name"),
            session_custom_claims=cached_data.get("session_custom_claims", {}),
            authentication_factors=cached_data.get("authentication_factors", []),
            raw_session_data=cached_data.get("raw_session_data", {}),
        )

    def _build_context_from_stytch_data(
        self, session_data: Dict[str, Any]
    ) -> StytchContext:
        """
        Build StytchContext from fresh Stytch API response.

        Args:
            session_data: Raw session data from Stytch API

        Returns:
            StytchContext instance
        """
        # Handle both dict and object formats from Stytch SDK
        member = session_data.get("member", {})
        session = session_data.get("member_session", {})
        organization = session_data.get("organization", {})

        # Helper function to safely get attribute from object or dict
        def safe_get(obj, attr, default=None):
            if hasattr(obj, attr):
                return getattr(obj, attr)
            elif isinstance(obj, dict):
                return obj.get(attr, default)
            return default

        # Handle datetime fields safely
        started_at = safe_get(session, "started_at")
        expires_at = safe_get(session, "expires_at")
        last_accessed_at = safe_get(session, "last_accessed_at")

        return StytchContext(
            member_id=safe_get(member, "member_id") or safe_get(session, "member_id"),
            session_id=safe_get(session, "member_session_id"),
            organization_id=safe_get(organization, "organization_id")
            or safe_get(session, "organization_id"),
            session_started_at=(
                datetime.fromisoformat(started_at)
                if started_at
                else datetime.now(timezone.utc)
            ),
            session_expires_at=(
                datetime.fromisoformat(expires_at)
                if expires_at
                else datetime.now(timezone.utc)
            ),
            session_last_accessed_at=(
                datetime.fromisoformat(last_accessed_at)
                if last_accessed_at
                else datetime.now(timezone.utc)
            ),
            member_email=safe_get(member, "email_address"),
            member_name=safe_get(member, "name"),
            session_custom_claims=safe_get(session, "custom_claims", {}),
            authentication_factors=safe_get(session, "authentication_factors", []),
            raw_session_data=session_data,
        )


# Global verifier instance
stytch_verifier = StytchVerifier()
