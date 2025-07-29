from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings for MicroAuth integration.
    Reads from environment variables prefixed with MICROAUTH_.
    """
    tenant_domain: str = Field(..., description='Your MicroAuth tenant domain, e.g. auth.microauth.com')
    client_id: str = Field(..., description='Your MicroAuth OAuth client ID.')
    algorithms: list[str] = ['RS256']
    jwks_url: str | None = Field(
        None, description='JWKs URL. If not provided, it will be constructed from the tenant domain.'
    )

    class Config:
        env_prefix = 'MICROAUTH_'
        env_file = '.env'


_override: Settings | None = None


def _override_settings(s: 'Settings') -> None:
    global _override
    _override = s


def _clear_override() -> None:
    global _override
    _override = None


@lru_cache()
def get_settings() -> Settings:
    if _override:
        return _override
    s = Settings()
    return s
