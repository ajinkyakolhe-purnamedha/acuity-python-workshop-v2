"""Catalog data model.

Day 1: dataclass-based `Product` and a `ProductCatalog` collection class.
On Day 2 these get re-declared as Pydantic models so the FastAPI server
gets typed I/O and validation for free.
"""

import logging
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id, etc.)."""


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    in_stock: bool = True
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        # Values may arrive as strings (e.g. from a CSV), so coerce each one.
        raw_stock = str(data.get("in_stock", "True")).lower()
        in_stock = raw_stock in {"true", "1", "yes"}

        raw_tags = str(data.get("tags", ""))
        tags = [tag.strip() for tag in raw_tags.split("|") if tag.strip()]

        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            price=float(data["price"]),
            in_stock=in_stock,
            tags=tags,
        )


class ProductCatalog:
    """In-memory product catalog keyed by product id."""

    def __init__(self, products=None):
        self._items = {}
        for product in products or []:
            self.add(product)

    # ---- mutation ----

    def add(self, product: Product) -> Product:
        if product.id in self._items:
            raise CatalogError(f"Product id {product.id} already exists")
        if product.price < 0:
            raise CatalogError(f"Price must be non-negative (got {product.price})")
        self._items[product.id] = product
        logger.info("added product id=%s name=%r", product.id, product.name)
        return product

    def delete(self, product_id: int) -> Product:
        if product_id not in self._items:
            raise CatalogError(f"Product id {product_id} not found")
        removed = self._items.pop(product_id)
        logger.info("deleted product id=%s", product_id)
        return removed

    # ---- read ----

    def get(self, product_id: int) -> Product:
        if product_id not in self._items:
            raise CatalogError(f"Product id {product_id} not found")
        return self._items[product_id]

    def list_all(self) -> list[Product]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    # ---- comprehension-driven queries (Lab 2) ----

    def search_by_name(self, term: str) -> list[Product]:
        needle = term.lower()
        return [p for p in self._items.values() if needle in p.name.lower()]

    def filter_by_price(self, max_price: float) -> list[Product]:
        return [p for p in self._items.values() if p.price <= max_price]

    def group_by_category(self) -> dict:
        groups = {}
        for product in self._items.values():
            groups.setdefault(product.category, []).append(product)
        return groups
