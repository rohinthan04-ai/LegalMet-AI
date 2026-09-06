from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Rule(Base):
    __tablename__ = "rules"

    rule_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    rule_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    rule_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    rule_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    legal_source: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    source_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    effective_from: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    effective_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    mappings = relationship(
        "CategoryRuleMapping",
        back_populates="rule"
    )