"""Password hashing using bcrypt directly. Bcrypt accepts max 72 bytes; we truncate before calling."""
import bcrypt

# Bcrypt limit (raises ValueError if password > 72 bytes)
BCRYPT_MAX_BYTES = 72


def truncate_password_72_bytes(plain: str) -> bytes:
    """Return password as bytes, truncated to 72 bytes. Use this before hash/verify."""
    if plain is None:
        return b""
    text = str(plain)
    encoded = text.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return encoded
    return encoded[:BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    """Hash password with bcrypt. Long passwords are truncated to 72 bytes."""
    secret = truncate_password_72_bytes(plain)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(secret, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash. Long passwords are truncated to 72 bytes."""
    secret = truncate_password_72_bytes(plain)
    return bcrypt.checkpw(secret, hashed.encode("utf-8"))
