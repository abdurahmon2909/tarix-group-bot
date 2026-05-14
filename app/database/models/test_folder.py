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


class TestFolder(Base):

    __tablename__ = "test_folders"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "test_folders.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )