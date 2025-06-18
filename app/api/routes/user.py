from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_utils.cbv import cbv
from fastcrud import FastCRUD
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies.authentication import get_current_active_user
from app.api.dependencies.sessions import get_async_session
from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.db.models.news import News
from app.db.models.user import User
from app.schemas.news import (
    UserNewsCreate,
    UserNewsRead,
    UserNewsRequestCreate,
    UserNewsUpdate,
)
from app.schemas.pagination import PaginationSchema
from app.schemas.user import UserRead, UserUpdate
from app.utils import exceptions
from app.utils.cloudinary import upload_image_to_cloudinary
from app.utils.common import ErrorCode
from app.utils.pagination import paginate
from app.utils.validator import validate_file_image

r = router = APIRouter(tags=["user"])

news_crud = FastCRUD(News)


@cbv(r)
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


@cbv(r)
class _MeNews:
    user_manager: UserManager = Depends(get_user_manager)
    db: AsyncSession = Depends(get_async_session)
    current_user: User = Depends(get_current_active_user)

    @r.get(
        "/me/news",
        status_code=status.HTTP_200_OK,
        response_model=PaginationSchema[UserNewsRead],
    )
    async def get_all_user_news(
        self,
        page: int = 1,
        per_page: int = 20,
        categoy_id: UUID | None = None,
        search: str | None = None,
    ):
        query = (
            select(News)
            .options(selectinload(News.category), selectinload(News.user))
            .where(News.user_id == self.current_user.id)
        )

        if categoy_id:
            query = query.where(News.category_id == categoy_id)

        if search:
            query = query.where(News.title.like(f"%{search}%"))

        return await paginate(self.db, query, page, per_page)

    @r.post("/me/news", status_code=status.HTTP_200_OK, response_model=UserNewsRead)
    async def create_news(self, data: UserNewsRequestCreate):
        news = UserNewsCreate(user_id=self.current_user.id, **data.model_dump())

        news = await news_crud.create(self.db, news)

        return (
            await self.db.execute(
                select(News).where(News.id == news.id).options(selectinload(News.category))
            )
        ).scalar_one()

    @r.patch(
        "/me/news/{news_id}", status_code=status.HTTP_202_ACCEPTED, response_model=UserNewsRead
    )
    async def update_news(self, news_id: UUID, data: UserNewsUpdate):
        news = await news_crud.get(
            self.db,
            one_or_none=True,
            id=news_id,
        )

        if not news:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                exceptions.NewsNotFoundError(
                    "News not found", error_code=ErrorCode.NEWS_NOT_FOUND
                ).dump(),
            )

        if news["user_id"] != self.current_user.id:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                exceptions.UserNotHavePermission(
                    "User not have permission", error_code=ErrorCode.USER_NOT_HAVE_PERMISSION
                ).dump(),
            )

        await news_crud.update(
            self.db,
            data.model_dump(exclude_unset=True, exclude_none=True),
            id=news_id,
        )
        return (
            await self.db.execute(
                select(News).where(News.id == news_id).options(selectinload(News.category))
            )
        ).scalar_one()

    @r.delete("/me/news/{news_id}", status_code=status.HTTP_202_ACCEPTED)
    async def delete_news(self, news_id: UUID):
        news = (
            await self.db.execute(
                select(News).where(News.id == news_id, News.user_id == self.current_user.id)
            )
        ).scalar_one_or_none()

        if not news:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                exceptions.NewsNotFoundError(
                    "News not found", error_code=ErrorCode.NEWS_NOT_FOUND
                ).dump(),
            )

        await self.db.delete(news)
        await self.db.commit()

    @r.post("/me/news/{news_id}/upload-image", status_code=status.HTTP_202_ACCEPTED)
    async def upload_image(self, news_id: UUID, file: UploadFile = File(...)):
        news = await news_crud.get(self.db, one_or_none=True, id=news_id)
        if news is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                exceptions.NewsNotFoundError(
                    "News not found", error_code=ErrorCode.NEWS_NOT_FOUND
                ).dump(),
            )

        if news["user_id"] != self.current_user.id:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                exceptions.UserNotHavePermission(
                    "User not have permission", error_code=ErrorCode.USER_NOT_HAVE_PERMISSION
                ).dump(),
            )
        # Validate image
        validate_file_image(file)

        try:
            result = await upload_image_to_cloudinary(file.file, news_id)
            await news_crud.update(
                self.db,
                {"image_url": result["secure_url"]},
                id=news_id,
            )
        except Exception as e:
            return HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e.args))
        finally:
            file.file.close()
