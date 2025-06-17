from app.schemas.base import BaseSchema


class CategoryRead(BaseSchema):
    id: str
    name: str


class CategoryCreate(BaseSchema):
    name: str


class CategoryUpdate(BaseSchema):
    name: str | None = None
