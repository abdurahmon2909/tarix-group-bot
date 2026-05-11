from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class SupportMessage(Base):

    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    forwarded_message_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )