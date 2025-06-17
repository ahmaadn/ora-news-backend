import datetime
from uuid import UUID, uuid4

from fastapi_utils.guid_type import GUID
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixin import TimeStampMixin


class News(TimeStampMixin, Base):
    __tablename__ = "news"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    category_id: Mapped[UUID] = mapped_column(
        GUID, ForeignKey("categories.id"), nullable=False
    )

    category = relationship("Category", back_populates="news")
    user = relationship("User", back_populates="news")
