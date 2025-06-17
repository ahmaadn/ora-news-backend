from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.db.models.user import User
from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.token import TokenManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
    token_manager: TokenManager = Depends(TokenManager),
) -> User:
    """
    Dependency to get the current user.
    """

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": ErrorCode.NOT_AUTHENTICATED,
                "messages": ["Not authenticated"],
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": ErrorCode.INVALID_TOKEN_CREDENTIALS,
            "messages": ["Could not validate credentials"],
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if the token is valid
    try:
        payload = token_manager.decode_token(
            token, token_manager.JWT_SECRET_KEY, [token_manager.JWT_AUDIENCE]
        )
    except exceptions.InvalidVerifyTokenError as e:
        raise credentials_exception from e

    # Check if the user_id is valid
    user_id = payload.get("sub", None)
    if user_id is None:
        raise credentials_exception
    try:
        parser_id = user_manager.parse_id(user_id)
    except exceptions.InvalidIDError as e:
        raise credentials_exception from e

    # get the user by id from the database
    user = await user_manager.get_by_id(parser_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.USER_NOT_ACTIVE,
                "messages": ["Inactive user"],
            },
        )
    return user


async def get_current_verified_user(user: User = Depends(get_current_active_user)):
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.USER_NOT_VERIFIED,
                "messages": ["User not verified"],
            },
        )
    return user
