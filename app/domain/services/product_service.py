from dataclasses import dataclass

from app.domain.repositories.product_repository_protocol import ProductRepositoryProtocol
from app.infrastructure.database.models.product_model import ProductModel


@dataclass
class CreateProductDto:
    manufacturer_part_number: str
    internal_code: str
    primary_type: str
    secondary_type: str
    barcode: str
    external_code: str | None = None
    description: str | None = None
    image: str | None = None
    supplier: str | None = None
    stock_location: str | None = None


class DuplicateInternalCodeError(Exception):
    pass


class ProductService:
    def __init__(self, repository: ProductRepositoryProtocol):
        self._repository = repository

    def create_product(self, dto: CreateProductDto) -> ProductModel:
        existing = self._repository.get_by_internal_code(dto.internal_code)
        if existing:
            raise DuplicateInternalCodeError(
                f"Internal code '{dto.internal_code}' is already in use."
            )

        product = ProductModel(
            manufacturer_part_number=dto.manufacturer_part_number,
            internal_code=dto.internal_code,
            external_code=dto.external_code,
            description=dto.description,
            image=dto.image,
            supplier=dto.supplier,
            primary_type=dto.primary_type,
            secondary_type=dto.secondary_type,
            barcode=dto.barcode,
            stock_location=dto.stock_location,
        )

        return self._repository.create(product)