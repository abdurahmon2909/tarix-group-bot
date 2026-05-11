from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class Group(Base):

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    telegram_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )