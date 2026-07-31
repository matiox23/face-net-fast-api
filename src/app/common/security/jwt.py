import enum
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from src.app.common.setting import base_config


class TokenType(str, enum.Enum):
    """Kind of JWT issued by the API, stored in the `type` claim."""

    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(Exception):
    """Raised when a token's signature, format, or claims are invalid."""


class ExpiredTokenError(Exception):
    """Raised when a token's signature is valid but it has expired."""


def create_access_token(user_id: int, roles: list[str]) -> str:
    """Issue a short-lived access token carrying the user's id and role codes."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": TokenType.ACCESS.value,
        "iat": now,
        "exp": now + timedelta(minutes=base_config.jwt_access_token_expires_minutes),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, base_config.jwt_secret_key, algorithm=base_config.jwt_algorithm)


def create_refresh_token(user_id: int, jti: str, expires_at: datetime) -> str:
    """Issue a refresh token whose `jti` matches the row persisted for revocation checks."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": TokenType.REFRESH.value,
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    return jwt.encode(payload, base_config.jwt_secret_key, algorithm=base_config.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType) -> dict:
    """Decode and validate a JWT, enforcing signature, expiration, and the `type` claim."""
    try:
        payload = jwt.decode(token, base_config.jwt_secret_key, algorithms=[base_config.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise ExpiredTokenError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError("Token is invalid") from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(f"Expected a {expected_type.value} token")

    return payload
