---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 3 · Test It — pytest, Mocking, Coverage & CI"
footer: "Acuity Training · Day 3 of 4"
---

<!-- _class: title -->

# Day 3
## Automation Testing
## **lock down everything you built**

6 hours · 3 modules · 3 labs · same repo

---

# Two days of code. Zero proof it still works.

You have a server, a client, and a bulk importer. Change one line tomorrow — did you break `withdraw`? `search`? the import report? **You don't know.**

Today: a **test suite** — saved checks that re-run in seconds and tell you.

- **M7** — pytest + fixtures, testing the catalog core
- **M8** — mock the client, parametrize across status codes
- **M9** — coverage + CI (green on every push)

---

<!-- _class: title -->

# Module 7
## pytest Fundamentals & Testing the Catalog
**3 sections · ~40 min** — fundamentals → pytest → test the catalog
1 Testing fundamentals · 2 pytest basics · 3 Testing the catalog

---

<!-- _class: section -->

# Section 1 · Testing fundamentals
## A test is a **saved check that re-runs** — so you change code without fear.
## First the shared map: why, the pyramid, the kinds of test.

---

# 1.1 · Why test — the regression net

You test by hand once; a **test** saves that check so it runs **every time**, in seconds. The payoff isn't catching today's bug — it's **changing code tomorrow and knowing instantly if you broke something.**

```text
manual:  run it, eyeball the output, hope     (once)
test:    assert the result, re-run forever     (every change)
```

---

# 1.2 · The test pyramid — where effort goes

```text
        /\    e2e          few   — slow, the whole system
       /  \   integration        — some, real parts wired together
      /____\  unit         many  — fast, one piece, no I/O
```

**Most of your tests are unit tests** — fast, isolated, no server or network. That's where M7 lives.

---

# 1.3 · Unit vs integration vs API — what each pins

| Kind | Tests… | Needs a server? |
|---|---|---|
| **unit** | one piece in isolation (the catalog) | no |
| **integration** | real parts wired together | yes |
| **API** | the client against the API | mocked (M8) or live |

M7 writes **unit** tests for the catalog core; M8 does the API/mocked tests.

---

<!-- _class: section -->

# Section 2 · pytest basics
## A test is just a function with `assert`. pytest finds it and runs it.
## The one new idea: **fixtures** give every test a clean slate.

---

# 2.1 · A test is a function + a plain `assert`

No special API — name a function `test_…`, call your code, and `assert` what you expect. pytest reads a plain `assert` and shows you **both sides** on failure (no `assertEqual` ceremony).

```python
def test_deposit_increases_balance():
    acct = BankAccount(id=1, owner="Ada", balance=100.0)
    acct.deposit(50)
    assert acct.balance == 150.0
```

---

# 2.2 · Discovery + running

`pytest` auto-discovers files named `test_*.py` and functions named `test_*` — no registration. Run it, read the dots (pass) and `F` (fail); a failure prints the exact line and **both values**.

```bash
pytest                                         # run everything
pytest tests/test_models.py::test_deposit...   # run one test
```

---

# 2.3 · Fixtures — a clean slate every test

Tests that share state **contaminate** each other — one test's leftover data fails the next. A `@pytest.fixture` builds **fresh** state; a test gets it by **naming it as a parameter**, and pytest re-runs the fixture for each test.

```python
@pytest.fixture
def account():
    return BankAccount(id=1, owner="Ada", balance=100.0)

def test_deposit(account):     # asks for it by name → a fresh account
    account.deposit(50)
    assert account.balance == 150.0
```

<div class="code-along">▶ Code-along now — write your first test + a fixture, then run <code>pytest</code></div>

---

<!-- _class: section -->

# Section 3 · Testing the catalog
## Pin the behavior **and** the error paths — both are promises your code makes.
## Every test: Arrange → Act → Assert.

---

# 3.1 · Arrange → Act → Assert

Every test has the same three beats: set up the inputs, run the **one** thing under test, assert on what it did. One behavior per test — when it fails, the *name* tells you what broke.

```python
def test_add_then_get_returns_it(catalog):
    acct = BankAccount(id=9, owner="Sam", balance=40.0)   # Arrange
    catalog.add(acct)                                     # Act
    assert catalog.get(9).owner == "Sam"                  # Assert
```

---

# 3.2 · Happy paths, off a fixture

A `catalog` fixture gives each test a clean, seeded catalog; assert on the **behavior** — the count grows, queries return the right rows.

```python
def test_search_finds_by_name(catalog):
    assert {a.id for a in catalog.search_by_name("ada")} == {1}

def test_len_counts(catalog):
    assert len(catalog) == 3
```

---

# 3.3 · Error paths — assert it raises

A rule your code enforces is a promise — so **test that it fires.** `pytest.raises(...)` passes only if the exception is raised: a duplicate id, a missing id, a negative balance.

```python
def test_duplicate_id_raises(catalog):
    with pytest.raises(CatalogError):
        catalog.add(BankAccount(id=1, owner="dup", balance=0.0))
```

<div class="code-along">▶ Code-along now — test the catalog: a fixture, happy paths, and <code>pytest.raises</code></div>

---

<!-- _class: lab -->

# 🧪 Lab 7 — Unit Tests for the Catalog Core

**80 min** · open `labs/lab-07-unit-tests.md`

You'll write (testing your `Product` catalog):
- `tests/conftest.py` — a `catalog` fixture (fresh, seeded `ProductCatalog`)
- `tests/test_models.py` — `Product` validation (the `Field` constraints)
- `tests/test_catalog.py` — add / get / search / filter + `pytest.raises(CatalogError)`

Run `pytest -v` → your first **green suite**.

---

<!-- _class: title -->

# Module 8
## Mocking & Parametrize — Testing the APIClient
**5 sections · ~60 min** — doubles → mock → parametrize → unhappy path → workflow
1 Test doubles · 2 Mock the session · 3 Parametrize · 4 Unhappy path · 5 Import workflow

---

# M7 tested code with no dependencies. The client has one: a server.

The catalog was easy — pure logic, no I/O. But the `APIClient` **talks to a server**, and a unit test can't depend on a live server being up, seeded, and fast.

The fix is the seam you already built: the client takes its `session` by **injection** (M5). In a test, hand it a **fake** one.

---

<!-- _class: section -->

# Section 1 · Test doubles
## Don't test against the real server — swap it for a **stand-in you control.**
## The client's injected `session` is the seam that lets you.

---

# 1.1 · Why not hit the real server

A real server in a unit test is **slow** (network), **flaky** (down, or the data shifted), and **stateful** (your POST test leaves junk for the next run). Unit tests must be **fast and isolated** — same result every time, no setup.

```text
real server:  needs uvicorn up + seeded + reachable + reset between runs
test double:  answers instantly, the same way, every time
```

---

# 1.2 · A test double — a stand-in you control

You don't need the real session — only its *behavior*: a `.request()` that returns a response. Swap in a **double** through the injection seam from M5.

```python
client = AccountClient(session=FakeSession(...))   # no network — you decide the answers
```

---

# 1.3 · Stub vs mock vs fake

| Double | What it does | You use it to… |
|---|---|---|
| **stub** | returns canned answers | feed the code an input |
| **mock** | records how it was called | **assert** the code called it right |
| **fake** | a real-but-lightweight impl | stand in for a heavy dependency |

Same idea — swap the real thing — a different question each one answers.

---

<!-- _class: section -->

# Section 2 · Mock the session
## Give the client a canned response → test its logic with no network.
## `unittest.mock` builds the double for you **and records the call.**

---

# 2.1 · A hand-written fake session

The simplest double: a small object with the `.request()` the client calls, returning a canned response. Inject it; the client never knows it isn't real.

```python
class FakeSession:
    def __init__(self, status, payload): self.status, self.payload = status, payload
    def request(self, method, url, **kw):
        return FakeResponse(self.status, self.payload)

AccountClient(session=FakeSession(200, [{"id": 1, "owner": "Ada", "balance": 1500.0}])).list_accounts()
```

---

# 2.2 · `unittest.mock` — the double, built for you

`Mock()` fakes any object; set `.return_value` for what a call returns. No class to write — and it **remembers every call.**

```python
from unittest.mock import Mock
session = Mock()
session.request.return_value = Mock(ok=True, status_code=200,
    json=lambda: [{"id": 1, "owner": "Ada", "balance": 1500.0}])
AccountClient(session=session).list_accounts()
```

---

# 2.3 · A mock lets you assert *how* it was called

Beyond the return value, the mock recorded the call — so you can assert the client sent the **right request** (the GET to the right path), not just that it returned something.

```python
session.request.assert_called_with("GET", "http://server/accounts", timeout=5)
```

That's the **mock** question: not just "what came back" but "did my code call it correctly".

---

<!-- _class: section -->

# Section 3 · Parametrize
## One test body, a **table** of cases — data-driven testing.
## Run the client against every status code without copy-pasting the test.

---

# 3.1 · `@pytest.mark.parametrize` — one test, many cases

Instead of five near-identical tests, write **one** and feed it a table of inputs. pytest runs it once per row and reports each separately.

```python
@pytest.mark.parametrize("amount, expected", [(50, 150.0), (0, 100.0)])
def test_deposit(amount, expected):
    acct = BankAccount(1, "Ada", 100.0); acct.deposit(amount)
    assert acct.balance == expected
```

---

# 3.2 · Parametrize the status codes

The real payoff: drive the mocked client across every response code in **one** test — a 2xx returns a model, a 4xx raises `APIError`.

```python
@pytest.mark.parametrize("status", [400, 404, 409])
def test_4xx_raises_apierror(status):
    client = AccountClient(session=FakeSession(status, {"detail": "no"}))
    with pytest.raises(APIError):
        client.list_accounts()
```

---

# 3.3 · The one that *does* hit a server

Keep a few **integration** tests that drive a live server — but **mark** them, so the fast unit run skips them.

```python
@pytest.mark.integration
def test_against_live_server():
    client = AccountClient(base_url="http://localhost:8000")   # a real session
    assert isinstance(client.list_accounts(), list)
```

`pytest -m "not integration"` runs the fast suite; CI runs both.

<div class="code-along">▶ Code-along now — mock the client, assert the call, parametrize the status codes</div>

---

<!-- _class: section -->

# Section 4 · Testing the unhappy path
## Mocks let you trigger failures you **can't** reproduce live — a dropped
## connection, a timeout — and prove the client recovers (or doesn't).

---

# 4.1 · Force a transient failure — prove `@retry` recovers

You can't make a real server blip on cue; a mock can — **fail twice, then succeed.** Assert the client **retried**: the call happened 3 times.

```python
def test_retry_recovers():
    session = Mock()
    session.request.side_effect = [ConnectionError(), ConnectionError(),
                                   Mock(ok=True, json=lambda: ACCOUNTS)]
    AccountClient(session=session).list_accounts()
    assert session.request.call_count == 3      # 2 fails + 1 success
```

---

# 4.2 · A 4xx is *never* retried — the policy, proven

A 404 raises `APIError`, not a network error — so `@retry`'s exception tuple never catches it. The mock proves it: called exactly **once**.

```python
def test_4xx_not_retried():
    session = Mock()
    session.request.return_value = Mock(ok=False, status_code=404, text="x")
    with pytest.raises(APIError):
        AccountClient(session=session).list_accounts()
    assert session.request.call_count == 1      # no retry on a 4xx
```

---

<!-- _class: section -->

# Section 5 · Testing the import workflow
## Mock the client, feed the importer a tricky CSV, and assert the **report** —
## the three buckets M6 promised. That report is the day's real deliverable.

---

# 5.1 · Mock the client, run the importer

The importer takes the client by **injection** too — so a test passes a fake that creates accounts but raises `APIError` on a duplicate id. Feed it rows with a bad one and a dup.

```python
client = FakeClient(dup_ids={1})        # a fake that 409s on id 1
report = import_accounts(rows, client)  # rows: one good, one dup, one invalid
```

---

# 5.2 · Assert the report — the three buckets stay apart

The report *is* the contract: a bad row lands in `validation_errors`, a duplicate in `api_errors`, the rest in `created`. Pinning this shape is what Day 3 exists for.

```python
assert report["summary"]["created"] == 1
assert report["summary"]["validation_errors"] == 1
assert report["summary"]["api_errors"] == 1
```

<div class="code-along">▶ Code-along now — test `@retry` recovery + the import report's three buckets</div>

---

<!-- _class: lab -->

# 🧪 Lab 8 — Test the `APIClient` (mocked + integration)

**~60 min** · open `labs/lab-08-test-apiclient.md`

You'll write (testing your `Product` `APIClient` + importer):
- `tests/test_client.py` — mock the session; typed returns + `APIError`; `parametrize` `200/400/404/500`; **`@retry` recovery + no-retry-on-4xx**
- `tests/test_import.py` — mock the client, run `import_csv`, assert the **report's 3 buckets**
- a `TestIntegration` class marked `@pytest.mark.integration` (live server)

**The same mocking pattern returns on Day 4 to mock the LLM.**

---

<!-- _class: title -->

# Module 9
## Coverage, CI & the Quality Gate
**3 sections · ~40 min** — measure → automate → enforce
1 Coverage · 2 CI with GitHub Actions · 3 Make it a gate

---

# You have tests. Two questions left.

M7–M8 gave you a green suite. But:

- **How much** of your code does it actually exercise? *(you don't know)*
- Does it run **without you remembering** to? *(it doesn't)*

M9 answers both — **coverage** (measure) and **CI** (automate) — and turns the suite into a **gate** nothing red can pass.

---

<!-- _class: section -->

# Section 1 · Coverage
## Green tests ≠ tested code.
## Coverage shows what your suite **never touches.**

---

# 1.1 · Green ≠ tested

A suite can pass with whole functions **never called**. "All green" tells you the tests you *wrote* pass — not that the code is *covered*.

```text
20 tests, all green ✓   …but withdraw() and delete() were never run by any of them
```

You can't see that gap by reading pass/fail — you **measure** it.

---

# 1.2 · `pytest-cov` — the %, and the missing lines

`pytest --cov` reports how much of each file ran; `term-missing` names the **exact lines** no test reached.

```bash
pytest --cov=catalog --cov-report=term-missing
# catalog/models.py   94%   Missing: 47-49    ← those lines never ran
```

---

# 1.3 · Coverage is a floor, not a target

100% means every line **ran** — not that it's **correct** (a line can run and still be wrong). Use it to find the **untested branch that matters**, not to chase a number.

```python
def withdraw(self, amt):
    if amt > self.balance: raise BankError(...)   # is THIS branch tested? coverage tells you
    self.balance -= amt
```

Aim for the risky paths covered — not 100% for its own sake.

---

<!-- _class: section -->

# Section 2 · CI with GitHub Actions
## A suite you forget to run protects nothing.
## CI runs it on **every push.**

---

# 2.1 · Tests only help if they run

A green suite on *your* laptop helps no one when a teammate pushes a breaking change and never runs it. **CI** runs the suite automatically on every push and pull request — nobody has to remember.

---

# 2.2 · The workflow file

A YAML file in `.github/workflows/` tells GitHub: on a push, set up Python, install, run pytest.

```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest
```

---

# 2.3 · The matrix + the green check

A **matrix** runs the suite across several Python versions at once — catch a 3.10-only break before users do. The result is a ✓ or ✗ **on the pull request itself.**

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

---

<!-- _class: section -->

# Section 3 · Make it a gate
## Turn "tests exist" into "**red can't merge.**"
## Artifacts, a threshold, a gate.

---

# 3.1 · Reports — artifacts you can open

CI's console scrolls away. Produce **files**: an HTML report (browsable) + JUnit XML (other tools read it), uploaded as build **artifacts**.

```yaml
- run: pytest --cov --html=report.html --junitxml=results.xml
- uses: actions/upload-artifact@v4
  with: { path: report.html }
```

---

# 3.2 · Fail under a threshold

Make coverage a **rule**, not a vibe. `--cov-fail-under` fails the build if coverage drops below the line — so a new untested feature can't sneak in.

```bash
pytest --cov=catalog --cov-fail-under=85     # exit 1 if below 85%
```

---

# 3.3 · The payoff — a quality gate

Require the check to pass before merge, and **red can't reach `main`.** Your suite stopped being "tests that exist" and became a **gate**.

```text
push → CI runs pytest + coverage → ✓ merge allowed   /   ✗ blocked
```

End of Day 3: server + client + importer — **tested, measured, and gated.**

<div class="code-along">▶ Code-along now — run <code>pytest --cov</code> locally, read the workflow file, set a threshold</div>

---

<!-- _class: lab -->

# 🧪 Lab 9 — Reports + GitHub Actions

**80 min** · open `labs/lab-09-reports-ci.md`

You'll add (to your repo):
- coverage + HTML report config in `pyproject.toml`
- `.github/workflows/tests.yml` — install, run `pytest` with coverage, upload the report
- push to GitHub → watch the check go **green**

End of Day 3 → your repo matches `checkpoints/day-4-start/` (tested + CI green).
