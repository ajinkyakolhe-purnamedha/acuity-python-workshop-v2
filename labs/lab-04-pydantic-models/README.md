# Lab 4 — Pydantic Models for the Catalog

**Duration:** ~80 min · **Day:** 2 · **Module:** 4 (JSON & Pydantic)

> **Concepts used:** `BaseModel`, `Field` constraints, `model_validate`/`model_dump`, typed FastAPI → `codealong/module-4.ipynb`.
> Applies Module 4's `BankAccount` concepts to `Product`. The migration: Lab 3's `@dataclass Product` becomes a Pydantic `BaseModel` — same fields, now **validated**.

## Goal
Turn `Product` into a Pydantic model so bad data is rejected **at the boundary**, then make the FastAPI server typed — a bad `POST` returns an automatic **422** with field-level errors, and `/docs` is generated from the model.

## You start with
- Your Lab 3 working folder (`@dataclass Product` + `ProductCatalog` class + `server.py`).

## You'll end with
- `catalog/models.py` — `Product(BaseModel)` with `Field` constraints; `ProductCatalog` (unchanged class, now holding Pydantic Products)
- `catalog/storage.py` — `save_json`/`load_json` updated to use `model_dump()` / `model_validate()`
- `catalog/server.py` — routes typed with `Product` + `response_model`; bad `POST` → 422

## Starter files
```bash
cp ../labs/lab-04-pydantic-models/starter/*.py catalog/   # run from my-catalog/
```

## Steps

1. **`@dataclass` → `BaseModel`.** Replace the dataclass with `class Product(BaseModel)` and add `Field` constraints:
   ```python
   class Product(BaseModel):
       id: int = Field(ge=1)
       name: str = Field(min_length=1)
       category: str = Field(min_length=1)
       price: float = Field(ge=0)          # ge allows 0 (free items); negative is rejected
       in_stock: bool = True
       tags: list[str] = Field(default_factory=list)
   ```

2. **The catalog barely changes.** `ProductCatalog` is the same class — it now holds Pydantic Products. Drop the manual negative-price check from `add` (the **model** enforces it now); keep the duplicate-id rule. In `storage.py`, `save_json` now uses `p.model_dump()` and `load_json` rebuilds with `Product.model_validate(row)`.

3. **Type the server.** Body parameter `product: Product` makes FastAPI validate the JSON — a bad body returns **422** automatically (delete the old manual 400). Add `response_model=Product` (and `list[Product]`) so output is typed and documented. Keep `CatalogError` → 404 (missing) / 409 (duplicate).

4. **Run it & break it.**
   ```bash
   uvicorn catalog.server:app --reload
   curl -X POST localhost:8000/products \
        -H 'Content-Type: application/json' \
        -d '{"id":51,"name":"","category":"x","price":-1}'      # 422 with field errors
   ```
   Then open `/docs` — every field, type, and constraint is there.

## Expected output

```
$ curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8000/products \
       -d '{"id":51,"name":"","category":"x","price":-1}'
422
```

## Make it pass

```bash
pytest tests/test_lab04.py -v
```

Skips until `Product` is a Pydantic model, then red → green. Target: `TestModel` + `TestCatalog` + `TestServer` green.

> Lab 1–3 graders now **skip** — `Product` is no longer a dict or a dataclass. `test_lab04.py` is the live spec.

## Common pitfalls
- Pydantic v2 uses `model_dump()` / `model_validate()` — not v1's `.dict()` / `.parse_obj()`.
- Leaving the manual `price < 0` check in `catalog.add` — redundant now (the model rejects it first), and it raises the wrong error type.
- `price: float = Field(gt=0)` forbids free (`0.0`) items — use `ge=0`.
- Returning `model_dump()` from a route that has `response_model=Product` — just return the `Product`; FastAPI serialises it.

## Stretch (optional)
- Add a `ProductUpdate` model (all fields optional, `ConfigDict(extra="forbid")`) and a `PATCH /products/{id}` that merges via `model_copy(update=patch.model_dump(exclude_unset=True))`.
