"""Typed HTTP client for the catalog API — Day 2 Lab 5.

Drives the FastAPI server from Python. Every method returns a Pydantic
`Product` (or a list of them) — no raw dicts leak out. One private
`_request` funnel wears M5's `@retry` so a network blip doesn't kill a
bulk-import run. On Day 4, the agent's tools will literally *be* these methods.

You write THREE bodies: `_request`, `list_products`, `create_product`.
Everything else (`APIError`, `__init__`, `_extract_detail`, and the
`health`/`get_product`/`delete_product` worked examples) is already filled —
read them, they show the exact pattern you repeat.

Done-signal: `APIClient().list_products()` returns `list[Product]`, and a
duplicate POST raises `APIError` (README → Expected output).
Concepts: codealong/module-5.ipynb (requests.Session, the _request funnel,
@retry, typed returns). `@retry` itself is built in this module's code-along.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from .decorators import retry
from .models import Product

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0
DEFAULT_BASE_URL = "http://localhost:8000"


class APIError(Exception):
    """Raised when the catalog API returns a non-2xx response.

    A plain Exception on purpose: callers catch APIError without importing
    `requests` (module-5, §"Wrap it in AccountClient").
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class APIClient:
    """CRUD client for the catalog API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # session is injected for tests (Day 3) — defaults to a real pooled Session.
        self._session = session or requests.Session()

    # ---- low-level: every call funnels through here ----

    @retry(times=3, delay=0.2, exceptions=(requests.ConnectionError, requests.Timeout))
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        # TODO (module-5, §"requests — one good pattern") — the funnel:
        #   1. default the timeout:       kwargs.setdefault("timeout", self.timeout)
        #   2. send via the SESSION:      resp = self._session.request(method, f"{self.base_url}{path}", **kwargs)
        #   3. on a non-2xx, raise:       raise APIError(resp.status_code, self._extract_detail(resp))
        #   4. otherwise return resp
        # NOTE: always go through self._session (NOT requests.get) so the retry
        #       + session headers apply. Only retry network errors, never 4xx.
        ...

    @staticmethod
    def _extract_detail(response: requests.Response) -> str:
        # GIVEN: pull the server's JSON "detail" if present, else the raw text.
        try:
            return response.json().get("detail", response.text)
        except ValueError:
            return response.text or response.reason

    # ---- typed CRUD: each is two lines (call _request, validate into a model) ----

    # GIVEN — worked example. Notice the shape: _request(...).json() → model_validate.
    # Your list_products / create_product repeat exactly this move.
    def get_product(self, product_id: int) -> Product:
        data = self._request("GET", f"/products/{product_id}").json()
        return Product.model_validate(data)

    def health(self) -> dict:
        # GIVEN — same funnel, but /health returns a plain dict (no model to validate).
        return self._request("GET", "/health").json()

    def delete_product(self, product_id: int) -> None:
        # GIVEN — fires the request for its side effect; nothing to validate or return.
        self._request("DELETE", f"/products/{product_id}")

    def list_products(self) -> list[Product]:
        # TODO: GET "/products", then model_validate EACH row in the JSON list.
        #   data = self._request("GET", "/products").json()
        #   return [Product.model_validate(row) for row in data]
        ...

    def create_product(self, payload: Product) -> Product:
        # TODO: POST "/products" with json=payload.model_dump(), validate the result.
        #   data = self._request("POST", "/products", json=payload.model_dump()).json()
        #   return Product.model_validate(data)
        ...

    # --- Stretch (optional): PATCH ---
    # Lab 4 deferred PATCH on the server; this is its client side. Add an
    # update endpoint to server.py, then uncomment. (Needs ProductUpdate —
    # import it inside the method to keep the top of this file import-clean.)
    #
    # def update_product(self, product_id: int, patch) -> Product:
    #     from .models import ProductUpdate  # patch: ProductUpdate
    #     data = self._request(
    #         "PATCH",
    #         f"/products/{product_id}",
    #         json=patch.model_dump(exclude_unset=True),
    #     ).json()
    #     return Product.model_validate(data)


# =====================================================================
# LAB HELPERS — given to you, you do NOT write or edit these.
# Let you drive APIClient with NO server running (no uvicorn). Inject a
# FakeSession and it answers like the real API. Same dependency-injection
# seam Day 3 turns into real mocking.
#
#   from catalog.client import APIClient, FakeSession, FakeResponse, SAMPLE_PRODUCTS
#   c = APIClient(session=FakeSession([FakeResponse(200, SAMPLE_PRODUCTS)]))
#   print(c.list_products())          # -> list[Product], no server needed
# =====================================================================


class FakeResponse:
    """Lab helper. Mimics the bits of requests.Response APIClient touches."""

    def __init__(self, status_code: int, json_body) -> None:
        self.status_code = status_code
        self._json = json_body
        self.text = str(json_body)
        self.reason = "fake"

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def json(self):
        return self._json


class FakeSession:
    """Lab helper. Returns queued outcomes in order; an Exception in the queue
    is raised instead (simulates a network blip, so you can see @retry work).
    Once one item is left, it's reused for every further call."""

    def __init__(self, outcomes) -> None:
        self._outcomes = list(outcomes)
        self.headers = {}      # APIClient may set auth headers here
        self.calls = 0         # count requests — proves @retry actually retried

    def request(self, method, url, **kwargs):
        self.calls += 1
        item = self._outcomes.pop(0) if len(self._outcomes) > 1 else self._outcomes[0]
        if isinstance(item, Exception):
            raise item
        return item


# Sample data so the example above runs as-is.
SAMPLE_PRODUCTS = [
    {"id": 1, "name": "USB-C Cable", "category": "Electronics",
     "price": 499.0, "in_stock": True, "tags": ["cable", "usb-c"]},
    {"id": 2, "name": "Mechanical Keyboard", "category": "Electronics",
     "price": 5499.0, "in_stock": True, "tags": ["mech"]},
]
