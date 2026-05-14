from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Boolean,
    DateTime,
    JSON,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class Test(Base):

    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    folder_id: Mapped[int] = mapped_column(
        ForeignKey(
            "test_folders.id",
            ondelete="CASCADE",
        )
    )

    certificate_template_id: Mapped[int] = mapped_column(
        ForeignKey(
            "certificate_templates.id"
        )
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    telegram_file_id: Mapped[str] = mapped_column(
        String(1000)
    )

    answer_key_json: Mapped[dict] = mapped_column(
        JSON
    )

    question_count: Mapped[int] = mapped_column()

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )