# Lab 8 — Test the `APIClient` (Mocked)

**Duration:** ~60 min · **Day:** 3 · **Module:** 2 (Parametrize + Mocking)

## Goal
Lock the Day-2 `APIClient` under tests **without** a real server. Mock
`requests.Session`, parametrize across status codes, and prove `@retry` — all
with no network. This is the exact pattern Day 4 uses to mock the LLM.

> The `live_server` fixture and the `@pytest.mark.integration TestLiveServer`
> class are **provided** — your instructor builds them with you in the
> code-along and you paste them in. You **run** them; you don't write them.
> Your work below is the **mocked** tests.

## You start with
- Lab 7 end-state — `tests/conftest.py`, `test_models.py`, `test_catalog.py` green (21 tests).

## Starter files
```bash
cp ../labs/lab-08-test-apiclient/starter/tests/test_client.py tests/   # into my-catalog/tests/
```
| In `test_client.py` | What |
|---|---|
| `_mock_response`, `client_with_mock_session` | **provided** helpers — the mock seam (use them) |
| `TestSuccessfulCalls`, `TestErrorMapping` | stubs to fill — typed returns, error mapping, retry |

Each stub **fails** with a `# TODO` until you implement it. Run `pytest -m "not integration" -q`.

## You'll end with
- mocked tests implemented · `pytest -m "not integration"` → **31 passed** in <1s
- the provided integration class still passing under `pytest -m integration`

## What to implement (read the TODO in each stub)
- **Success path** — a 200 list comes back as `Product` objects (not dicts); `create_product` POSTs the JSON body to `/products`; a partial update sends **only** the changed field.
- **Error mapping** — parametrize the non-2xx codes (`400/404/409/422/500`); each raises `APIError` carrying that `status_code`.
- **Retry** — two `ConnectionError`s then success → 3 calls, no raise; a `409` is raised at once (called exactly **once** — 4xx isn't retried).

## Steps
1. Copy `starter/tests/test_client.py` into your `tests/`.
2. Fill the `TestSuccessfulCalls` TODOs; run `pytest -m "not integration" -q`.
3. Fill `TestErrorMapping` — add the status-code rows to the `parametrize`, then the retry tests (`side_effect` is your friend).
4. Watch your instructor add the integration class in the code-along, then run `pytest -m integration`.

## Expected output
```
$ pytest -m "not integration" -q
...............................                                          [100%]
31 passed in 0.5s

$ pytest -m integration -q          # the provided integration class
..                                                                       [100%]
2 passed in 1.2s
```

## Common pitfalls
- Mocking `requests.get` — the client uses `self._session.request`, not `requests.get`. Patch *where it's looked up* (that's why we inject the session).
- `MagicMock()` without `spec=requests.Session` — a typo like `session.requst(...)` won't fail. Always pass `spec=`.
- Asserting `call_count == 3` *without* also asserting the result — your retry might be silently returning `None`.
- Expecting a dict where the client returns a `Product` — assert `isinstance(result, Product)`.

## Stretch (optional)
- **Write the integration class yourself** instead of using the provided one: a `@pytest.mark.integration TestLiveServer` driving the real `live_server` end-to-end (create → get → update → delete).
- Swap the `MagicMock` session for the [`responses`](https://github.com/getsentry/responses) library — declarative HTTP mocking.
