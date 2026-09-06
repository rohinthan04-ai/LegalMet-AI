from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StructuredData(Base):
    __tablename__ = "structured_data"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id"),
        nullable=False,
        unique=True
    )

    ocr_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    inspection = relationship(
        "Inspection",
        back_populates="structured_data"
    )