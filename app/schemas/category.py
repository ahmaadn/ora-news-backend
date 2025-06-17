from uuid import UUID

from app.schemas.base import BaseSchema


class CategoryRead(BaseSchema):
    id: UUID
    name: str


class CategoryCreate(BaseSchema):
    name: str


class CategoryUpdate(BaseSchema):
    name: str | None = None
