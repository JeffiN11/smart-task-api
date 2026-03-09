import os
import base64
import hashlib
import hmac
import secrets


_ITERATIONS = 100_000
_SALT_SIZE = 16


def hash_password(password: str) -> str:
    """
    Hash password using PBKDF2-HMAC-SHA256.
    Stored format:
    pbkdf2_sha256$iterations$salt$hash
    """
    salt = secrets.token_bytes(_SALT_SIZE)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _ITERATIONS
    )
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(derived_key).decode("utf-8")
    return f"pbkdf2_sha256${_ITERATIONS}${salt_b64}${hash_b64}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = hashed_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_b64.encode("utf-8"))
        original_hash = base64.b64decode(hash_b64.encode("utf-8"))

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations)
        )

        return hmac.compare_digest(original_hash, new_hash)
    except (ValueError, TypeError):
        return False