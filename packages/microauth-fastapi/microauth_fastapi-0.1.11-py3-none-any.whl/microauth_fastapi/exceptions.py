class JWKSFetchError(Exception):
    """Raised when we can't fetch or parse the JWKS for a tenant."""
    pass


class TokenValidationError(Exception):
    """Raised when token or claims verification fails."""
    pass
