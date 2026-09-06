from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CategoryRuleMapping(Base):
    __tablename__ = "category_rule_mapping"

    mapping_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("product_categories.category_id"),
        nullable=False
    )

    rule_id: Mapped[int] = mapped_column(
        ForeignKey("rules.rule_id"),
        nullable=False
    )

    applicability: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    category = relationship(
        "ProductCategory",
        back_populates="mappings"
    )

    rule = relationship(
        "Rule",
        back_populates="mappings"
    )