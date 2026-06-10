# Lab 8 — Test the `APIClient` (Mocked)

**~60 min · Day 3 · parametrize + mocking**

## Goal
Lock the Day-2 `APIClient` under tests **without a real server**. Mock `requests.Session`, parametrize across status codes, and prove `@retry` — all with no network. This is the exact pattern Day 4 uses to mock the LLM. Done when `pytest -q` → **31 passed** in <1s.

## Start with
Lab 7 end-state — `tests/` green (21 tests).

## Get the starter test
```bash
cp ../labs/lab-08-test-apiclient/starter/tests/test_client.py tests/   # into my-catalog/tests/
```
| In `test_client.py` | What |
|---|---|
| `_mock_response`, `client_with_mock_session` | **provided** helpers — the mock seam (use them) |
| `TestSuccessfulCalls`, `TestErrorMapping` | stubs to fill |

Each stub fails with a `# TODO` message until you implement it.

## What to implement
- **Success** — a 200 list returns `Product` objects (not dicts); `create_product` POSTs the body to `/products`; a partial update sends **only** the changed field.
- **Errors** — parametrize the non-2xx codes (`400/404/409/422/500`); each raises `APIError` carrying that `status_code`.
- **Retry** — two `ConnectionError`s then success → 3 calls, no raise; a `409` raises at once (called exactly **once** — 4xx isn't retried).

## Steps
1. Copy the starter `test_client.py` into your `tests/` (command above).
2. Fill the `TestSuccessfulCalls` TODOs; run `pytest tests/test_client.py -q`.
3. Fill `TestErrorMapping` — add the status-code rows to the `parametrize`, then the retry tests (`side_effect` is your friend).
4. Run the whole suite: `pytest -q` → **31 passed**.

## Watch out
- The client uses `self._session.request` — mock **that**, not `requests.get`.
- Pass `spec=requests.Session` to the mock so a typo'd method (`requst`) fails loudly.
- Assert the **result type** too (`isinstance(r, Product)`), not just `call_count`.
