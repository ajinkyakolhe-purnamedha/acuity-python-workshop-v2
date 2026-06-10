# Lab 7 — Unit Tests for the Catalog Core

**~80 min · Day 3 · pytest basics + fixtures**

## Goal
Write the first real test suite for the catalog — the Pydantic **models** and the **ProductCatalog** class. Use fixtures for setup, `pytest.raises` for errors. Done when `pytest -q` → **21 passed**.

## Start with
Your Lab 6 folder (`my-catalog/`), or `project/checkpoints/day-3-start/`.

## Get the starter tests
```bash
cp -r ../labs/lab-07-unit-tests/starter/tests .   # run from my-catalog/
```
| File | What |
|---|---|
| `tests/conftest.py` | **provided** fixtures (`sample_product`, `seeded_catalog`) — use, don't edit |
| `tests/test_models.py` | stubs to fill — model validation + dict round-trip |
| `tests/test_catalog.py` | stubs to fill — add/get/delete/queries + `pytest.raises` |

Each stub fails with a `# TODO` message until you implement it.

## What to implement
- **test_models.py** — a valid payload passes; each bad field raises `ValidationError` (parametrize the rules); CSV strings coerce (`"true"`→bool, `"a|b|c"`→list); `to_dict`↔`from_dict` round-trips.
- **test_catalog.py** — add+get; duplicate-id and missing-id raise `CatalogError`; delete shrinks; search / filter / group; partial update changes only supplied fields.

## Steps
1. Copy the starter `tests/` into your `my-catalog/` (command above) — `tests/__init__.py` is included, keep it.
2. Fill `test_models.py`, replacing each `pytest.fail(...)` with real asserts. Run `pytest tests/test_models.py -q`; watch reds go green.
3. Do the same for `test_catalog.py` — ask for the `seeded_catalog` fixture by naming it as a test parameter (fresh each test).
4. Run the whole suite: `pytest -q` → **21 passed**.

## Watch out
- Use the **narrowest** exception in `pytest.raises` (`CatalogError`, not `Exception`).
- One behavior per test — a precise failure name beats one test asserting five things.
