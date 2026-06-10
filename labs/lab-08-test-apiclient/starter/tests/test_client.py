"""Lab 8 — test the APIClient with a MOCKED session (no real server).

The seam: APIClient takes its `session` by injection (Lab 5). Hand it a
MagicMock and you decide every response. Two helpers below are PROVIDED —
`_mock_response` and `client_with_mock_session`. Your job is the test bodies:
fill every `# TODO` and turn each red test green with `pytest -m "not integration" -q`.

The `live_server` fixture + the `@pytest.mark.integration TestLiveServer`
class are PROVIDED by your instructor in the code-along (they boot a real
uvicorn) — you run them, you don't write them here.

Concepts: codealong/module-8, deck §"Mock the session" + §"Parametrize".
"""

from unittest.mock import MagicMock

import pytest
import requests

from catalog.client import APIClient, APIError
from catalog.models import Product, ProductCreate, ProductUpdate


# ---- PROVIDED helpers (use these, don't edit) ----

@pytest.fixture
def client_with_mock_session():
    """An APIClient whose session is a mock you control. Returns (client, session)."""
    session = MagicMock(spec=requests.Session)
    client = APIClient(base_url="http://test.local", session=session)
    return client, session


def _mock_response(status, payload):
    """Build a fake requests.Response with the status + JSON body you pass."""
    resp = MagicMock(spec=requests.Response)
    resp.ok = 200 <= status < 300
    resp.status_code = status
    resp.json.return_value = payload
    resp.text = str(payload)
    resp.reason = "OK" if resp.ok else "ERR"
    return resp


# ---- YOUR TESTS ----

class TestSuccessfulCalls:
    def test_list_products_returns_typed_objects(self, client_with_mock_session):
        """A 200 with a list of dicts comes back as Product objects, not dicts."""
        client, session = client_with_mock_session
        # TODO: session.request.return_value = _mock_response(200, [ {one product dict} ])
        #       result = client.list_products(); assert isinstance(result[0], Product)
        pytest.fail("TODO: implement test_list_products_returns_typed_objects")

    def test_create_product_sends_json_body(self, client_with_mock_session):
        """create_product POSTs to /products with the product as the JSON body."""
        client, session = client_with_mock_session
        # TODO: stub a 201 response; call client.create_product(ProductCreate(...))
        #       inspect session.request.call_args: verb is "POST", path ends "/products",
        #       kwargs["json"]["id"] is the id you sent
        pytest.fail("TODO: implement test_create_product_sends_json_body")

    def test_update_product_only_sends_set_fields(self, client_with_mock_session):
        """A partial update sends ONLY the fields you changed."""
        client, session = client_with_mock_session
        # TODO: stub a 200; client.update_product(5, ProductUpdate(price=12.0))
        #       assert session.request.call_args.kwargs["json"] == {"price": 12.0}
        pytest.fail("TODO: implement test_update_product_only_sends_set_fields")


class TestErrorMapping:
    @pytest.mark.parametrize("status", [
        # TODO: list the non-2xx codes that must raise APIError, e.g. 400, 404, 409, 422, 500
    ])
    def test_non_2xx_raises_api_error(self, client_with_mock_session, status):
        """Every non-2xx response raises APIError carrying that status_code."""
        client, session = client_with_mock_session
        # TODO: stub _mock_response(status, {"detail": "boom"})
        #       with pytest.raises(APIError) as exc: client.list_products()
        #       assert exc.value.status_code == status
        pytest.fail("TODO: implement test_non_2xx_raises_api_error")

    def test_retries_then_succeeds_on_network_blip(self, client_with_mock_session):
        """@retry recovers: two ConnectionErrors then a success → 3 calls, no raise."""
        client, session = client_with_mock_session
        # TODO: session.request.side_effect = [ConnectionError, ConnectionError, success_response]
        #       call list_products(); assert it returned, and session.request.call_count == 3
        pytest.fail("TODO: implement test_retries_then_succeeds_on_network_blip")

    def test_does_not_retry_on_4xx(self, client_with_mock_session):
        """A 4xx is NOT a network error, so it's raised at once — called exactly once."""
        client, session = client_with_mock_session
        # TODO: stub a 409; assert it raises APIError AND session.request.call_count == 1
        pytest.fail("TODO: implement test_does_not_retry_on_4xx")
