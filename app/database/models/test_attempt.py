from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Integer,
    Float,
    Boolean,
    DateTime,
    JSON,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class TestAttempt(Base):

    __tablename__ = "test_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        )
    )

    test_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tests.id",
            ondelete="CASCADE",
        )
    )

    submitted_answers: Mapped[dict] = mapped_column(
        JSON
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer
    )

    wrong_answers: Mapped[int] = mapped_column(
        Integer
    )

    score_percent: Mapped[float] = mapped_column(
        Float
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer
    )

    certificate_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )