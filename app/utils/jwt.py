import datetime
from typing import Dict

import jwt
from pydantic import SecretStr

ALGORITHM = "HS256"


def _get_secret_value(secret: str | SecretStr) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def create_jwt_token(
    data: Dict,
    secret: str | SecretStr,
    expires_in: int = 3600,
    algorithm: str = ALGORITHM,
) -> str:
    """Create a JWT token.

    Args:
        data (Dict): data to encode in the token.
        secret (str | SecretStr): secret key to encode the token.
        expires_in (int, optional): expiration time in seconds. Defaults to 3600.
        algorithm (str, optional): algorithm to use for encoding. Defaults to "HS256".

    Returns:
        str: encoded JWT token.
    """  # noqa: E501
    payload = data.copy()
    payload["exp"] = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(seconds=expires_in)
    return jwt.encode(payload, _get_secret_value(secret), algorithm)


def decode_jwt_token(
    token: str,
    secret: str | SecretStr,
    audience: list[str],
    algorithms: list[str] | None = None,
) -> Dict:
    """Decode a JWT token.

    Args:
        token (str): token to decode.
        secret (str | SecretStr): secret key to decode the token.
        audience (list[str]): expected audience of the token.
        algorithms (list[str] | None, optional): algorithms to use for decoding. Defaults to None.

    Returns:
        Dict: decoded token data.
    """  # noqa: E501
    if algorithms is None:
        algorithms = [ALGORITHM]

    return jwt.decode(
        jwt=token,
        key=_get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
