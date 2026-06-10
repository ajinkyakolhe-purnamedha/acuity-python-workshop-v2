# Code-along beat — Integration test against a real server (M8, §3.3)

**Instructor live-build · ~8 min · on the real `catalog/` project** (not BankAccount — there's no BankAccount server; integration needs the actual app). Students **follow along and paste**; they don't derive this. It seeds the `live_server` fixture + `TestLiveServer` so the lab's `pytest -m integration` passes. The lab itself stays mocked-only.

## Frame (say this first)
"Every test so far is mocked — fast, but it never proves the client and the **real** server agree. We add **one** integration test that boots the actual FastAPI app and drives it end-to-end. We **mark** it so the fast suite still skips it."

## Build 1 — the `live_server` fixture → `tests/conftest.py`
Type it part by part; name each part as you go.

```python
import socket, subprocess, sys, time
from contextlib import closing
import requests

def _free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def live_server():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn",
         "catalog.server:app", "--port", str(port), "--log-level", "warning"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 10                       # wait for it to come up
    while time.time() < deadline:
        try:
            if requests.get(f"{base_url}/health", timeout=0.5).ok:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        proc.terminate(); proc.wait(timeout=5)
        pytest.fail("live_server did not become ready within 10 s")
    yield base_url                                    # tests run here
    proc.terminate()                                  # always tear down
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
```

Three beats to name aloud: **free port** (no clashes if 8000 is busy) · **wait-for-`/health`** (or you race uvicorn's startup and get `ConnectionRefused` flakes) · **`yield` then terminate** (the test runs in the middle; teardown always fires, even on failure — no zombie servers). `scope="session"` = one server for the whole run, not per-test.

## Build 2 — the integration class → `tests/test_client.py`
```python
@pytest.mark.integration
class TestLiveServer:
    def test_health(self, live_server):
        client = APIClient(base_url=live_server)
        assert client.health()["status"] == "ok"

    def test_full_crud_roundtrip(self, live_server):
        client = APIClient(base_url=live_server)
        created = client.create_product(
            ProductCreate(id=9001, name="IntegTest", category="QA", price=42.0))
        assert created.id == 9001
        assert client.update_product(9001, ProductUpdate(price=99.0)).price == 99.0
        client.delete_product(9001)
        with pytest.raises(APIError) as exc:
            client.get_product(9001)
        assert exc.value.status_code == 404
```
No mocks — a **real** `APIClient` against the **real** app: create → update → delete → confirm 404. This is the one test that would catch a route the mocks got wrong.

## Register the marker → `pyproject.toml`
```toml
[tool.pytest.ini_options]
markers = ["integration: tests that hit a live FastAPI server (slow)"]
```

## Run it — predict first
Ask the room: *"`pytest -m integration` — how many pass, and how long vs the mocked run?"* Then:
```bash
pytest -m "not integration" -q   # the fast mocked suite — skips this
pytest -m integration       -q   # 2 passed in ~1.2s — boots uvicorn
```

## Payoff (say this last)
"Keep these **few** and **marked**. Day-to-day you run `-m 'not integration'` — milliseconds. CI runs everything. That mark is the whole trick: real confidence without slowing the loop."
