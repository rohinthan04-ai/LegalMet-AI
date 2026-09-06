from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InspectionImage(Base):
    __tablename__ = "inspection_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id"),
        nullable=False
    )

    image_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    image_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    inspection = relationship(
        "Inspection",
        back_populates="images"
    )