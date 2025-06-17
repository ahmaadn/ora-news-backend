from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from app.api.dependencies.authentication import get_current_active_user
from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.db.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.utils import exceptions

r = router = APIRouter(tags=["user"])


@cbv(router)
class _User:
    user_manager: UserManager = Depends(get_user_manager)
    current_user: User = Depends(get_current_active_user)

    @r.get("/me", status_code=status.HTTP_200_OK, response_model=UserRead)
    async def detail(self):
        return self.current_user

    @r.put("/me", status_code=status.HTTP_200_OK, response_model=UserRead)
    async def update(self, user_update: UserUpdate):
        try:
            return await self.user_manager.update(user_update, self.current_user, safe=True)
        except exceptions.UserAlreadyExistsError as e:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=e.dump()) from e
        except exceptions.ValidationError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.dump()) from e
