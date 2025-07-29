from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from .auth import get_default_client, MicroAuthClient
import structlog
from .exceptions import JWKSFetchError, TokenValidationError
from .schemas import User


# Get logger
logger = structlog.get_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    client: MicroAuthClient = Depends(get_default_client)
) -> User:
    """
    FastAPI dependency to retrieve and verify the current user.
    Usage:
        @app.get('/me')
        async def me(user=Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    try:
        payload = await client.verify_token(token)
    except JWKSFetchError as e:
        await logger.aerror(f'JWKS fetch failed with error: {str(e)}')
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Invalid tenant domain.'
        )
    except TokenValidationError as e:
        await logger.aerror(f'Token verification failed with error: {str(e)}')
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f'Invalid or expired token.'
        )
    return User(**payload)
