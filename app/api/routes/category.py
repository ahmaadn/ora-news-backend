from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.sessions import get_async_session
from app.db.models.category import Category
from app.schemas.category import CategoryRead
from app.schemas.pagination import SimplePaginationSchema

category_crud: FastCRUD[
    Category,
    CategoryRead,
    Any,
    Any,
    Any,
    Any,
] = FastCRUD(Category)

r = router = APIRouter(tags=["category"])


@cbv(router)
class _Category:
    db: AsyncSession = Depends(get_async_session)

    @r.get(
        "/category",
        status_code=status.HTTP_200_OK,
        response_model=SimplePaginationSchema[CategoryRead],
    )
    async def get_all_categories(
        self,
    ):  # -> GetMultiResponseModel[Any] | GetMultiResponseDict:
        return await category_crud.get_multi(self.db, schema_to_select=CategoryRead)
