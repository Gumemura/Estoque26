from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.infrastructure.database.base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    manufacturer_part_number: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    internal_code: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )

    external_code: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    image: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    supplier: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    primary_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    secondary_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    barcode: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    stock_location: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )