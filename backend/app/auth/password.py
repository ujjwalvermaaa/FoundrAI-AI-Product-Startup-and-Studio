"""
Password hashing and verification using bcrypt via passlib.
Never store plain-text passwords anywhere.
"""

from passlib.context import CryptContext

# bcrypt with 12 rounds — good balance of security and speed
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash, False otherwise."""
    return _pwd_context.verify(plain, hashed)
