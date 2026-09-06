from datetime import datetime

from sqlalchemy import DateTime, BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    category_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    category_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    category_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    mappings = relationship(
        "CategoryRuleMapping",
        back_populates="category"
    )