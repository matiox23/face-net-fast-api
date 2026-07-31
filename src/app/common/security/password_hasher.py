from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against an Argon2 hash."""
    return password_hash.verify(plain_password, hashed_password)
