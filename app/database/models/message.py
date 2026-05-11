from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Text,
    DateTime,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class Message(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
    )

    telegram_message_id: Mapped[int] = mapped_column(
        BigInteger
    )

    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        Text,
        default="Ism kiritilmagan",
    )

    username: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index(
            "idx_chat_sent_at",
            "chat_id",
            "sent_at",
        ),
    )