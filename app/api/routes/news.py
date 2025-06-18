from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies.sessions import get_async_session
from app.db.models.news import News
from app.schemas.news import NewsPublicRead
from app.schemas.pagination import PaginationSchema
from app.utils.pagination import paginate

r = router = APIRouter(tags=["news"])


@cbv(r)
class _News:
    db: AsyncSession = Depends(get_async_session)

    @r.get(
        "/news",
        status_code=status.HTTP_200_OK,
        response_model=PaginationSchema[NewsPublicRead],
    )
    async def get_news(
        self,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
        author: str | None = None,
        category: UUID | None = None,
    ):
        query = select(News).options(selectinload(News.category), selectinload(News.user))

        if search:
            query = query.where(News.title.ilike(f"%{search}%"))

        if category:
            query = query.where(News.category_id == category)

        if author:
            query = query.where(News.user.username == author)

        return await paginate(self.db, query, page, per_page)
