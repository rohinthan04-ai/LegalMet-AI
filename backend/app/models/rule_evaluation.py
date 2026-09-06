from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RuleEvaluation(Base):
    __tablename__ = "rule_evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("evaluations.id"),
        nullable=False
    )

    rule_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    evidence: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    details: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    evaluation = relationship(
        "Evaluation",
        back_populates="rule_evaluations"
    )