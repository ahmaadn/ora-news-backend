import datetime
from uuid import UUID, uuid4

from fastapi_utils.guid_type import GUID
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.mixin import TimeStampMixin


class User(TimeStampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        GUID(), primary_key=True, nullable=False, unique=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(150), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pending_password_hash: Mapped[str] = mapped_column(String, nullable=True)
    password_change_token: Mapped[str] = mapped_column(String, nullable=True)
    password_change_token_expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=True
    )
