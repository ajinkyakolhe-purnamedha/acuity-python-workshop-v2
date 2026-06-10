# Lab 5 — Build the `APIClient`

**Duration:** ~80 min · **Day:** 2 · **Module:** 5 (REST APIs with `requests` + Decorators)

> **Concepts used:** `requests.Session`, write-your-own decorators (`@retry`/`@log_calls`), the `_request` funnel, typed returns → `codealong/module-5.ipynb`.
> Applies the module's `AccountClient` concepts to `Product` — same patterns, different domain. **This is the module where decorators are built** (moved here from the older M3 draft to their point of use).

## Goal
Write the two reusable decorators (`@retry`, `@log_calls`), then a typed `APIClient`: one `_request` funnel that wraps `requests`, `@retry` on it for resilience, and methods that return Pydantic `Product` objects — **not raw dicts**. This client becomes the **toolbelt the agent uses on Day 4**.

## You start with
- Lab 4 end-state — Pydantic-typed `Product` + FastAPI server.
- `starter/decorators.py` — `functools.wraps` given; you fill the two wrapper bodies.
- `starter/client.py` — `APIError`, `__init__`, `_extract_detail`, and `health`/`get_product`/`delete_product` **already written** as worked examples; you fill three `# TODO` bodies.

## You'll end with
- `catalog/decorators.py` — `@retry(times, delay, exceptions)` and `@log_calls`
- `catalog/client.py` — `APIClient` + `APIError`, typed `list_products() -> list[Product]` and `create_product(...) -> Product`, with `@retry` on every call

## Starter files
```bash
cp ../labs/lab-05-api-client/starter/*.py catalog/   # run from my-catalog/
```

| File | You write |
|---|---|
| `starter/decorators.py` | the `log_calls` + `retry` wrapper bodies (`functools.wraps` is given) |
| `starter/client.py` | bodies of `_request`, `list_products`, `create_product`. The `FakeSession`/`FakeResponse` helpers at the bottom are **given** — they let you run with no server. |

## Steps

1. **`decorators.py` — write the two.** `log_calls`: log `func.__name__`, then `return func(*args, **kwargs)`. `retry`: it takes config, so it's three layers (`retry(...) → decorator(func) → wrapper`); the wrapper loops `for attempt in range(1, times+1)`, `try`s the call, and on a listed exception re-raises **only on the last attempt** (else `time.sleep(delay)` and loop).

2. **`_request` — the funnel.** Default the timeout (`kwargs.setdefault("timeout", self.timeout)`), send via **`self._session.request(method, f"{self.base_url}{path}", **kwargs)`** (the session — *not* `requests.get` — so `@retry` + headers apply), `raise APIError(resp.status_code, self._extract_detail(resp))` on a non-2xx, else return `resp`. `@retry` above it retries only network errors, so a 4xx surfaces at once.

   The given `get_product` is the template every typed method repeats:
   ```python
   def get_product(self, product_id: int) -> Product:
       data = self._request("GET", f"/products/{product_id}").json()   # the funnel
       return Product.model_validate(data)                             # dict → model
   ```

3. **`list_products` — looped.** GET `/products`, then `model_validate` **each** row: `[Product.model_validate(row) for row in data]`.

4. **`create_product` — POSTing.** Send `json=payload.model_dump()`, then `model_validate` the `Product` the server echoes back. (`payload` is a `Product`.)

5. **Drive it — no server needed.** Inject the given `FakeSession`:
   ```python
   from catalog.client import APIClient, FakeSession, FakeResponse, SAMPLE_PRODUCTS
   c = APIClient(session=FakeSession([FakeResponse(200, SAMPLE_PRODUCTS)]))
   print(c.list_products())   # → list[Product], straight from the fake
   ```

## Make it pass

```bash
pytest tests/test_lab05.py -v
```

Skips until `decorators.py` / `client.py` exist, then red → green. Target: `TestDecorators` (retry + `@log_calls` name) **and** `TestAPIClient` (typed returns, `APIError` on non-2xx, `@retry` recovering from a transient failure — an injected fake session stands in for the server).

## Common pitfalls
- Calling `requests.get(...)` instead of `self._session.request(...)` skips the session + the retry. **Always** go through `_request`.
- Returning the raw dict from `.json()` instead of `model_validate`-ing it — the typed return is the whole point.
- `@retry` that catches *all* exceptions retries a 4xx too — scope it to `(requests.ConnectionError, requests.Timeout)`.
- Forgetting `timeout` — a hung server hangs your script forever.

## Stretch (optional)
- Add `auth_token: Optional[str] = None` to `__init__` and inject `Authorization: Bearer …` on every request.
- Decorate a public method with `@log_calls` and watch each call show up in the logs.
