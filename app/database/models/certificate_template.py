from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class CertificateTemplate(Base):

    __tablename__ = (
        "certificate_templates"
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    background_image_file_id: Mapped[str] = mapped_column(
        String(500)
    )

    signature_image_file_id: Mapped[str] = mapped_column(
        String(500)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )