from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv

from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.schemas.user import UserCreate, UserRead
from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.token import TokenManager

r = router = APIRouter(prefix="/auth", tags=["auth"])


@cbv(router)
class Authentication:
    user_manager: UserManager = Depends(get_user_manager)

    def __init__(self):
        self.token_manager = TokenManager()

    @r.post("/login", status_code=status.HTTP_200_OK)
    async def login(self, credentials: OAuth2PasswordRequestForm = Depends()):
        user = await self.user_manager.authenticate(credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": ErrorCode.INVALID_LOGIN_CREDENTIALS,
                    "messages": ["Incorrect username or password"],
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = self.token_manager.create_access_token(user)
        refresh_token = self.token_manager.create_refresh_token(access_token)

        return JSONResponse(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

    @r.post("/register", status_code=status.HTTP_200_OK)
    async def register(self, user_create: UserCreate):
        try:
            user = await self.user_manager.create(user_create, safe=True)
        except exceptions.UserAlreadyExistsError as e:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                e.dump(),
            ) from e

        except exceptions.ValidationError as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                e.dump(),
            ) from e
        return UserRead.model_validate(user)
