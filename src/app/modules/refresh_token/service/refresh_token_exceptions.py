class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is malformed, expired, revoked, or unknown."""
