# Lab 7 — Unit Tests for the Catalog Core

**Duration:** ~80 min · **Day:** 3 · **Module:** 1 (pytest basics + fixtures)

## Goal
Write the first real test suite for the catalog — the Pydantic **models** *and*
the **ProductCatalog** class. Use fixtures for setup, classes to group tests,
`pytest.raises` for errors. Done-signal: `pytest -q` is green at 21 tests.

## You start with
- `project/checkpoints/day-3-start/` (Day 2 end-state) OR your own Lab 6 folder

## Starter files
```bash
cp -r ../labs/lab-07-unit-tests/starter/tests .      # run from my-catalog/
```
| File | What |
|---|---|
| `tests/conftest.py` | **provided** — `sample_product` + `seeded_catalog` fixtures (use them, don't edit) |
| `tests/test_models.py` | stubs to fill — model validation + dict round-trip |
| `tests/test_catalog.py` | stubs to fill — add/get/delete/queries/update + `pytest.raises` |

Each stub **fails** with a `# TODO` message until you implement it. Run pytest, turn each red test green.

## You'll end with
- every `# TODO` implemented · `pytest -q` → **21 passed**

## What to implement (read the TODO in each stub)
- **`test_models.py`** — a valid payload survives; each bad field raises `ValidationError` (parametrize the rules); CSV-style strings coerce (`"true"`→bool, `"a|b|c"`→list); `to_dict`↔`from_dict` round-trip; `ProductUpdate` is all-optional, rejects extras, dumps only what you set.
- **`test_catalog.py`** — empty start; add+get; duplicate-id and missing-id raise `CatalogError`; delete shrinks; the three queries (search / filter / group); partial update changes only supplied fields.

## Steps
1. Copy the starter `tests/` folder into your `my-catalog/` (command above). `tests/__init__.py` is included.
2. Open `tests/test_models.py`; fill each `# TODO`, replacing the `pytest.fail(...)` line with real asserts. Run `pytest tests/test_models.py -q` and watch reds go green.
3. Do the same for `tests/test_catalog.py` — ask for the `seeded_catalog` fixture by naming it as a test parameter (you get a fresh one each test).
4. Run the whole suite: `pytest -q`.

## Expected output
```
$ pytest -q
.....................                                                    [100%]
21 passed in 0.5s
```

## Common pitfalls
- `tests/__init__.py` missing — pytest discovery breaks on some setups. It's in the starter; keep it.
- `pytest.raises(Exception)` catches *everything* (even `AssertionError`). Use the narrowest type (`CatalogError`, `ValidationError`).
- Forgetting `match=` on `pytest.raises` — the test passes even when the *wrong* error fires.
- One test asserting five things — split them; one behavior per test gives a precise failure name.

## Stretch (optional)
- Add `pytest-randomly` and re-run — any order-dependent test surfaces immediately.
- Add a `test_storage.py` that round-trips a catalog through JSON (`save_json`/`load_json`) and asserts equality.
