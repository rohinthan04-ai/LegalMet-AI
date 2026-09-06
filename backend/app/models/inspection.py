from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True)

    inspector_id: Mapped[int] = mapped_column(
        ForeignKey("inspectors.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="STARTED",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    images = relationship(
    "InspectionImage",
    back_populates="inspection",
    cascade="all, delete-orphan"
    )

    structured_data = relationship(
    "StructuredData",
    back_populates="inspection",
    uselist=False,
    cascade="all, delete-orphan"
    )

    checklist = relationship(
    "Checklist",
    back_populates="inspection",
    uselist=False,
    cascade="all, delete-orphan"
    )

    evaluation = relationship(
    "Evaluation",
    back_populates="inspection",
    uselist=False,
    cascade="all, delete-orphan"
    )

    report = relationship(
    "Report",
    back_populates="inspection",
    uselist=False,
    cascade="all, delete-orphan"
    )