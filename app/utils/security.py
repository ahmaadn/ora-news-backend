import secrets
from typing import Optional, Union

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class PasswordHelper:
    """A helper class for password hashing and verification."""

    def __init__(self, password_hash: Optional[PasswordHash] = None) -> None:
        self.password_hash = (
            PasswordHash([Argon2Hasher()]) if password_hash is None else password_hash
        )

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Union[str, None]]:
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def generate(self) -> str:
        return secrets.token_urlsafe()

    def verify(self, plain_password: str, hashed_password: str):
        return self.password_hash.verify(plain_password, hashed_password)
