import time
import httpx
from typing import Any, Dict
from .exceptions import JWKSFetchError

# Module‐level cache
_jwks_cache: Dict[str, Any] = {}
_jwks_expiry: float = 0.0


async def get_jwks(jwks_url: str, headers: dict, ttl: int = 3600) -> Dict[str, Any]:
    """
    Fetches and caches the JWKS payload for ttl seconds.
    """
    global _jwks_cache, _jwks_expiry
    now = time.time()
    if not _jwks_cache or now >= _jwks_expiry:
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                response = await client.get(jwks_url, timeout=5.0)
                response.raise_for_status()
                _jwks_cache = response.json()
                _jwks_expiry = now + ttl
            except httpx.HTTPError as e:
                raise JWKSFetchError(f'cannot fetch JWKS at {jwks_url}: {str(e)}')
    return _jwks_cache
