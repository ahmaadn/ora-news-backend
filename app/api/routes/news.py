from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies.sessions import get_async_session
from app.db.models.news import News
from app.schemas.news import NewsPublicRead
from app.schemas.pagination import PaginationSchema
from app.utils import exceptions
from app.utils.common import ErrorCode
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
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=20, ge=1, le=100),
        author: str | None = None,
        category: UUID | None = None,
        search: str | None = None,
        latest: bool = True,
    ):
        query = (
            select(News)
            .options(selectinload(News.category), selectinload(News.user))
            .order_by(News.published_at.desc() if latest else News.published_at.asc())
        )

        if search:
            query = query.where(News.title.ilike(f"%{search}%"))

        if category:
            query = query.where(News.category_id == category)

        if author:
            query = query.join(News.user).where(News.user.has(username=author.lower()))

        return await paginate(self.db, query, page, per_page)

    @r.get(
        "/news{news_id}",
        status_code=status.HTTP_200_OK,
        response_model=NewsPublicRead,
    )
    async def get_news_by_id(self, news_id: UUID):
        query = (
            select(News)
            .options(selectinload(News.category), selectinload(News.user))
            .where(News.id == news_id)
        )
        news = (await self.db.execute(query)).scalar_one_or_none()
        if not news:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                exceptions.NewsNotFoundError(
                    "News not found", error_code=ErrorCode.NEWS_NOT_FOUND
                ).dump(),
            )
        return news
