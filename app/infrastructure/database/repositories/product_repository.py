from sqlalchemy.orm import Session

from app.infrastructure.database.models.product_model import ProductModel


class ProductRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, product: ProductModel) -> ProductModel:
        self._session.add(product)
        self._session.commit()
        self._session.refresh(product)
        return product

    def get_by_internal_code(self, internal_code: str) -> ProductModel | None:
        return (
            self._session.query(ProductModel)
            .filter(ProductModel.internal_code == internal_code)
            .first()
        )

    def get_all(self) -> list[ProductModel]:
        return self._session.query(ProductModel).all()