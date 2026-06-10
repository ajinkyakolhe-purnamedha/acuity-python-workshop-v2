"""Catalog model — Day 2 Lab 4: @dataclass -> Pydantic.

Yesterday `Product` was a `@dataclass` (free `__init__`/`__repr__`, but NO
validation). Today it becomes a Pydantic `BaseModel` — same fields, **validated
on construction** — and the FastAPI server gets automatic 422s + a rich `/docs`.

Fill every `# TODO`. Done-signal: pytest tests/test_lab04.py -v goes green.
Concepts: codealong/module-4.ipynb (BaseModel, Field, model_validate/model_dump).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id)."""


class Product(BaseModel):
    # TODO: typed fields WITH constraints (module-4, §"Validation rules"):
    #   id: int = Field(ge=1)
    #   name: str = Field(min_length=1)
    #   category: str = Field(min_length=1)
    #   price: float = Field(ge=0)        # ge allows 0 (free items); negative is rejected
    #   in_stock: bool = True
    #   tags: list[str] = Field(default_factory=list)
    ...


class ProductCatalog:
    """In-memory catalog keyed by id — same class as Day 1, now holding Pydantic Products."""

    def __init__(self, products: list[Product] | None = None) -> None:
        self._items: dict[int, Product] = {}
        for p in products or []:
            self.add(p)

    def add(self, product: Product) -> Product:
        # NOTE: the Product model already rejected a bad price/name on construction —
        #       the catalog only needs the duplicate-id rule now.
        # TODO: raise CatalogError on duplicate id, else store + logger.info(...) + return
        ...

    def get(self, product_id: int) -> Product:
        # TODO: raise CatalogError("...not found...") if missing, else return it
        ...

    def delete(self, product_id: int) -> Product:
        # TODO: raise CatalogError if missing, else pop and return the removed product
        ...

    def search_by_name(self, term: str) -> list[Product]:
        # TODO: comprehension over self._items.values(), case-insensitive name match
        ...

    def filter_by_price(self, max_price: float) -> list[Product]:
        # TODO: comprehension, keep where p.price <= max_price
        ...

    def list_all(self) -> list[Product]:
        # TODO: a list of the stored products
        ...

    def __len__(self) -> int:
        # TODO
        ...

    def save_json(self, path: str | Path) -> None:
        # TODO: write [p.model_dump() for p in self.list_all()] as JSON, indent=2
        ...


def load_json(path: str | Path) -> ProductCatalog:
    """Build a catalog from JSON (missing file -> empty). Each row -> Product.model_validate."""
    # TODO: if not Path(path).exists(): return ProductCatalog()
    #       rows = json.loads(Path(path).read_text())
    #       return ProductCatalog([Product.model_validate(r) for r in rows])
    ...
