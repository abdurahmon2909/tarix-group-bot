from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class Certificate(Base):

    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey(
            "test_attempts.id",
            ondelete="CASCADE",
        )
    )

    certificate_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    telegram_file_id: Mapped[str] = mapped_column(
        String(1000)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )