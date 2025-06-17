import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.category import CategoryRead


class UserNewsRead(BaseSchema):
    id: UUID
    title: str
    content: str
    image_url: str | None = None
    category: CategoryRead
    published_at: datetime.datetime


class UserNewsRequestCreate(BaseSchema):
    title: str
    content: str
    category_id: UUID


class UserNewsUpdate(BaseSchema):
    title: str | None = None
    content: str | None = None
    category_id: UUID | None = None


class UserNewsCreate(BaseSchema):
    title: str
    content: str
    category_id: UUID
    user_id: UUID
    published_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    image_url: str | None = None
