from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

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

    result: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    inspection = relationship(
        "Inspection",
        back_populates="evaluation"
    )

    rule_evaluations = relationship(
    "RuleEvaluation",
    back_populates="evaluation",
    cascade="all, delete-orphan"
    )