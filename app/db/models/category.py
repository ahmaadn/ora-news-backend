from uuid import UUID, uuid4

from fastapi_utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        GUID(), primary_key=True, nullable=False, unique=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
