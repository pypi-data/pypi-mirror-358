from .config import Settings, _override_settings, _clear_override, get_settings

__version__ = '0.1.10'


def init(*, jwks_url: str | None = None, tenant_domain: str, client_id: str, algorithms: list[str] | None = None):
    """
    Programmatic initialization (overrides env vars).

    Example:
        import microauth_fastapi
        microauth_fastapi.init(
            tenant_domain='auth.microauth.com',
            client_id='my-backend',
        )
    """
    # Reset any previous override and cached Settings
    _clear_override()
    get_settings.cache_clear()

    # Build override Settings
    override = Settings(
        tenant_domain=tenant_domain,
        client_id=client_id,
        algorithms=algorithms or ['RS256'],
        jwks_url=jwks_url
    )
    _override_settings(override)
