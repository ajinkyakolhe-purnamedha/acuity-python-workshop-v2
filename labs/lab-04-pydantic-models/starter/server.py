"""FastAPI server — Day 2 Lab 4 (Pydantic-typed).

The route body is now a `Product`, so FastAPI validates incoming JSON and returns
an automatic **422** on bad data — no manual checks. `response_model` types the
output and feeds `/docs`. Only `CatalogError` (duplicate/missing) needs mapping.

Run:  uvicorn catalog.server:app --reload
Done-signal: the TestServer class in tests/test_lab04.py.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from .models import CatalogError, Product, ProductCatalog

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

SEED = [
    Product(id=1, name="USB-C Cable", category="Electronics", price=499.0, tags=["cable"]),
    Product(id=2, name="Mechanical Keyboard", category="Electronics", price=5499.0, tags=["kb"]),
    Product(id=3, name="Steel Water Bottle", category="Home", price=899.0),
    Product(id=4, name="Yoga Mat", category="Fitness", price=1299.0, in_stock=False),
    Product(id=5, name="Bluetooth Speaker", category="Electronics", price=2499.0),
]

app = FastAPI(title="Product Catalog", version="0.2.0")
catalog = ProductCatalog(list(SEED))


@app.get("/products", response_model=list[Product])
def list_products():
    # TODO: return catalog.list_all()
    ...


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    # TODO: try: return catalog.get(product_id)
    #       except CatalogError as e: raise HTTPException(404, str(e))
    ...


@app.post("/products", response_model=Product, status_code=201)
def create_product(product: Product):   # FastAPI validates the body -> 422 on bad data
    # TODO: try: return catalog.add(product)
    #       except CatalogError as e: raise HTTPException(409, str(e))
    ...


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    # TODO: catalog.delete(product_id); on CatalogError -> HTTPException(404, ...)
    ...
