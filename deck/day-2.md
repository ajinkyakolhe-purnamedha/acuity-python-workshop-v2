---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 2 · Automate It — Validation & a Typed Client"
footer: "Acuity Training · Day 2 of 4"
---

<!-- _class: title -->

# Day 2
## JSON & API Automation
## **against your Day-1 API**

6 hours · 3 modules · 3 labs · same repo as yesterday

---

# Where we left off

Day 1 ended with a **FastAPI server** serving an `@dataclass` catalog. But a dataclass trusts you — `price=-50` sails through silently.

Today:
- **M4** — validate every payload with **Pydantic** (clean 422s)
- **M5** — drive the server from Python with an **APIClient**
- **M6** — bulk-import a CSV → API, with a report

Same project, typed end to end.

---

<!-- _class: title -->

# Module 4
## JSON & Pydantic
**4 sections · ~40 min** — each builds on the last; we code each one live
1 dataclass → Pydantic · 2 Validation rules · 3 validate / dump · 4 Pydantic in FastAPI

---

<!-- _class: section -->

# Section 1 · From @dataclass to Pydantic
## the problem → BaseModel → validated on construction

---

# 1.1 · The problem — a dataclass trusts you

Yesterday's `@dataclass` stores whatever you pass — including nonsense. Nothing checks it.

```python
BankAccount(id=1, owner="", balance=-50)   # accepted silently: empty owner, negative balance
```

---

# 1.2 · Pydantic — same fields, one base class

Subclass `BaseModel` and list the **same typed fields**. That's the only structural change.

```python
from pydantic import BaseModel
class BankAccount(BaseModel):
    id: int
    owner: str
    balance: float
```

---

# 1.3 · Validated on construction

A `BaseModel` checks types **when you build it** — good data becomes an object; bad data raises `ValidationError` immediately, at the boundary.

```python
BankAccount(id=1, owner="Ada", balance=1500.0)    # ok
BankAccount(id="x", owner="Ada", balance=1500.0)  # ValidationError: id is not an int
```

<div class="code-along">▶ Code-along now → notebook Section 1 — dataclass vs BaseModel; watch bad data raise</div>

---

<!-- _class: section -->

# Section 2 · Validation rules
## Field constraints → reading a ValidationError

---

# 2.1 · `Field` — rules beyond the type

A type says "a float"; `Field` says "a float **≥ 0**". Constraints live on the field and run on construction.

```python
from pydantic import Field
class BankAccount(BaseModel):
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0)        # ge = "greater than or equal to"
```

---

# 2.2 · Reading a ValidationError

The error is **structured** — for every bad field it tells you *where*, *what*, and *why*.

```python
try:
    BankAccount(id=1, owner="", balance=-5)
except ValidationError as e:
    e.errors()   # [{'loc': ('owner',), 'msg': '...', 'type': 'string_too_short'}, ...]
```

<div class="code-along">▶ Code-along now → notebook Section 2 — add Field constraints; read e.errors()</div>

---

<!-- _class: section -->

# Section 3 · model_validate / model_dump
## dict → model → dict, with coercion

---

# 3.1 · `model_validate` — a dict becomes a model

An HTTP body or a file row arrives as a plain `dict`. `model_validate` turns it into a validated object (or raises).

```python
BankAccount.model_validate({"id": 2, "owner": "Lin", "balance": 800.0})   # dict → model
```

---

# 3.2 · `model_dump` — a model becomes a dict

The other direction — back to a plain dict, ready for JSON / the wire.

```python
acct.model_dump()   # {'id': 2, 'owner': 'Lin', 'balance': 800.0}
```

These two are on **every line** of Modules 5–6.

---

# 3.3 · Coercion — strings just work

Pydantic is lax by default: `"800.0"` → `float`, `"true"` → `bool`, `"2"` → `int`. This is **why a CSV of strings can feed the API with no manual parsing** — the Module 6 through-line.

```python
BankAccount.model_validate({"id": "2", "owner": "Lin", "balance": "800.0"})  # strings coerced ✓
```

<div class="code-along">▶ Code-along now → notebook Section 3 — validate a dict, dump it back, coerce a string row</div>

---

<!-- _class: section -->

# Section 4 · Pydantic in FastAPI
## typed body → 422 → response_model → docs

---

# 4.1 · A typed body validates itself

Type the route parameter as your model. FastAPI validates the incoming JSON — bad data returns an automatic **422** with field errors, *before* your code runs.

```python
@app.post("/accounts")
def create(account: BankAccount):   # FastAPI validates the body into a BankAccount
    ...
```

---

# 4.2 · `response_model` — typed output

Declare what a route returns; FastAPI serialises the model to JSON and documents the shape.

```python
@app.get("/accounts/{id}", response_model=BankAccount)
def get_account(id: int):
    ...
```

---

# 4.3 · /docs, from the schema

The model **is** the schema. FastAPI's `/docs` now shows every field, type, and constraint — and lets you try the API in the browser. No extra work.

<div class="code-along">▶ Code-along now → notebook Section 4 — a Pydantic-typed route; a bad body returns 422</div>

---

<!-- _class: lab -->

# 🧪 Lab 4 — Pydantic Models for the Catalog

**80 min** · open `labs/lab-04-pydantic-models/README.md`

You'll do (on `Product`, not `BankAccount`):
- migrate `Product` from `@dataclass` → Pydantic `BaseModel` (with `Field` constraints)
- wire `response_model=Product` into the Day-1 server routes
- a bad POST → **422** with structured field errors

---

<!-- _class: title -->

# Module 5
## REST API Client — automate & validate
**3 sections · ~40 min** — each builds on the last; we code each one live
1 HTTP with requests · 2 Decorators · 3 The APIClient

---

# Drive the server from Python

M4 gave us **validated Pydantic models** and a **typed server**. Now we write the Python program that calls it — an `APIClient` — and **validate every response** back into those models.

```python
client = AccountClient(base_url="http://localhost:8000")
accounts = client.list_accounts()   # list[BankAccount] — parsed & validated
```

Along the way we write the `@retry` decorator (the module split out of M3) for resilient calls.

---

<!-- _class: section -->

# Section 1 · HTTP with requests
## verbs → status codes → Session + timeout → auth

---

# 1.1 · Verbs — which are safe to retry

A retry **re-sends the identical request** — so the only question is: *does sending it twice do harm?* **Idempotent** = same end state no matter how many sends.

```text
DELETE /accounts/5   ×2  → still just "deleted"     (idempotent → safe to retry)
POST   /accounts {…} ×2  → TWO accounts created     (not idempotent → retry double-creates)
```

`GET`/`PUT`/`DELETE` are idempotent; `POST` isn't — which is why §3 retries only safe calls.

---

# 1.2 · Status codes — why retry hinges on them

A **4xx** means the server *understood you and refused* — your request is wrong, so sending it again gets the **same** refusal. A **5xx** (or dropped connection) is the server *stumbling* — the same request might work a moment later.

```text
POST {bad json} → 422 → retry → 422 → 422 …   (never recovers — don't retry)
GET  /accounts  → 503 → retry → 200           (server recovered — retry won)
```

So: **retry 5xx + network errors, never 4xx.**

---

# 1.3 · A Session, with a timeout

Each bare `requests.get(...)` opens a **new** TCP connection and forgets your headers. A `Session` keeps one connection alive and carries them across every call. And **`timeout` is not optional** — omit it and a server that never replies blocks your thread *forever*.

```python
s = requests.Session()       # one connection, reused; headers remembered
s.get(url)                   # ⚠️ no timeout → hangs forever if the server stalls
s.get(url, timeout=5)        # ✓ raises after 5s instead of hanging
```

<div class="code-along">▶ Code-along now → notebook Section 1 — a Session with timeout + auth; read a status code</div>

---

# 1.4 · Auth — a token in a header, from the environment

Auth is just a header you set **once** on the session; every later call carries it. The trap is *where* the secret lives — a token in the URL lands in server logs and browser history (leaked forever); a token in source lands in git.

```python
# ❌ token in the URL → logged everywhere it travels
s.get(f"{url}?api_key={TOKEN}")
# ✓ token in a header, value from an env var → never logged, never committed
s.headers["Authorization"] = f"Bearer {os.environ['TOKEN']}"
```

---

<!-- _class: section -->

# Section 2 · Decorators — write your own
## what it is → @log_calls → @retry(times=3)

---

# 2.1 · What a decorator is

A decorator is a function that **takes a function and returns a new one** wrapping it. The `@` is pure sugar — these two are identical:

```python
@log_calls
def withdraw(acct, amt): ...
# …is exactly:
def withdraw(acct, amt): ...
withdraw = log_calls(withdraw)      # the line the @ writes for you
```

That's the whole trick: add behavior (logging, retry) **around** a function without touching its body.

---

# 2.2 · Write `@log_calls`

The wrapper takes `*args, **kwargs` so it forwards **any** call unchanged, logs around it, and returns the real result. `functools.wraps` copies the original's name over — without it, every decorated function would report as `wrapper`.

```python
def log_calls(func):
    @functools.wraps(func)                  # keep func's real __name__
    def wrapper(*args, **kwargs):
        logger.info("call %s", func.__name__)
        return func(*args, **kwargs)
    return wrapper

add = log_calls(add);  add.__name__         # "add", not "wrapper"
```

---

# 2.3 · `@retry(times=3)` — a decorator that takes config

It needs settings, so there's one extra layer: `retry(times=3)` **returns** the decorator. The wrapper loops, but catches **only the exceptions you list** — that tuple *is* the policy.

```python
@retry(times=3, exceptions=(ConnectionError, Timeout))
def fetch(): ...
# ConnectionError on try 1, 2 → retried;  success on try 3 → returned
# a 400 raises HTTPError (not in the tuple) → not retried, raised at once
```

<div class="code-along">▶ Code-along now → notebook Section 2 — write @log_calls; @retry a flaky call</div>

---

<!-- _class: section -->

# Section 3 · The APIClient
## _request funnel → @retry → typed/validated returns

---

# 3.1 · One `_request` funnel

Five CRUD methods each repeating url-join + timeout + error-check = five places to get wrong (and one route quietly missing a timeout). Funnel it: write that **once**, and every public method becomes a one-liner that *can't* forget the timeout.

```python
def _request(self, method, path, **kw):
    resp = self._session.request(method, self.base_url + path, timeout=5, **kw)
    if not resp.ok:
        raise APIError(resp.status_code, resp.text)   # non-2xx → a clean error
    return resp

def delete_account(self, id):  self._request("DELETE", f"/accounts/{id}")   # one line
```

---

# 3.2 · `@retry` on the funnel — resilience for free

Decorate `_request` once and **every** method inherits the retry. Scope it to transient errors only — and notice it's automatically safe: a 4xx raises `APIError`, never `ConnectionError`, so the policy *can't* retry a bad request (§1.2).

```python
@retry(times=3, exceptions=(ConnectionError, Timeout))
def _request(self, ...): ...
# list_accounts(), create_account() … all retry dropped connections;
# none ever retry a 422 — the exception tuple enforces it
```

---

# 3.3 · Typed returns — validate at the boundary

Return the raw dict and a server that drops `balance` blows up *three functions later*, mysteriously. Parse into the **M4 model** right here instead — a bad response fails **now**, with a field-level error, and callers get real `BankAccount` objects (types, autocomplete).

```python
def list_accounts(self) -> list[BankAccount]:
    data = self._request("GET", "/accounts").json()       # list of dicts off the wire
    return [BankAccount.model_validate(r) for r in data]  # validated → fails here if malformed
```

This is what **"validating API responses"** means in practice.

<div class="code-along">▶ Code-along now → notebook Section 3 — build AccountClient: _request, @retry, Pydantic returns</div>

---

<!-- _class: lab -->

# 🧪 Lab 5 — Build the `APIClient`

**80 min** · open `labs/lab-05-api-client/README.md`

You'll build (on `Product`, not `BankAccount`):
- `catalog/decorators.py` — `@retry` and `@log_calls`
- `catalog/client.py` — `APIClient` + `APIError`, one `_request` funnel
- full typed CRUD: `list` / `get` / `create` / `delete` → `list[Product]` / `Product` (validated)

End state: `APIClient().list_products()` returns `list[Product]`.

---

> **Where the *testing* comes:** Day 3 / M8 wraps this client in a pytest suite — mocking `requests` so tests don't need a live server, and parametrizing across status codes. M5 builds & validates; Day 3 tests systematically.

---

<!-- _class: title -->

# Module 6
## Data-Driven Automation
**4 sections · ~60 min** — concept first, then build it in Python
1 The pattern · 2 CSV validation · 3 JSON validation · 4 Drive the API + report

---

# The capstone: a file becomes API actions

M2 gave us **files**, M4 gave us **validation**, M5 gave us the **client**. M6 wires them into **one workflow** — a data file in, API calls out, a report to show for it.

```text
products.csv  →  validate each row  →  POST via APIClient  →  import_report.json
```

This *is* what "automate API workflows" means on the job.

---

<!-- _class: section -->

# Section 1 · The pattern
## **Data-driven** = the data lives *outside* the code; the logic stays *fixed*.
## Write the workflow once — run it over 1 row or 10,000. That's the whole idea.

---

# 1.1 · What "data-driven" means

The **logic is fixed**; the **data lives outside** it — a file, a spreadsheet, a table. You don't edit code to add a record; you add a row.

```text
code (fixed):   for each record →  validate  →  send  →  record the result
data (varies):  products.csv  →  10 rows today, 10,000 tomorrow — same code
```

---

# 1.2 · Why it's the automation workhorse

- **Scale** — one row or ten thousand, the code is identical.
- **Separation** — ops hands you a CSV; no developer needed to "add the data".
- **One place to maintain** — the workflow is written once.

QA engineers know this as **data-driven testing**: one test, many input rows.

---

# 1.3 · The shape — source → process → report

Every data-driven job is the same three parts:

```text
SOURCE          PROCESS (per record)        SINK
a CSV / JSON  →  validate → act (API)   →   a report of what happened
```

The **report is the deliverable** — the input file is just the input.

<div class="code-along">▶ Code-along now → notebook Section 1 — the shape, in code: one loop over records</div>

---

<!-- _class: section -->

# Section 2 · CSV validation
## A CSV is **all strings** — so "validate" also means **coerce**.
## Pydantic does both at once: bad rows raise, good rows come back typed.

---

# 2.1 · Read the CSV — every cell is a string

`csv.DictReader` gives one dict per row, keyed by the header — but every value is **text**, even numbers and booleans.

```python
for row in csv.DictReader(open("products.csv")):
    row    # {'id': '1', 'price': '499.0', 'in_stock': 'true'} — all str
```

---

# 2.2 · Validate = coerce + check, in one step

Hand the string-dict straight to your Pydantic model. It **coerces** `"499.0"`→float, `"true"`→bool, **and** enforces the constraints — a bad row raises `ValidationError`.

```python
Product.model_validate({"id":"1","name":"Cable","category":"Elec","price":"499.0"})  # typed ✓
Product.model_validate({"id":"1","name":"Cable","category":"Elec","price":"-5"})     # ValidationError
```

<div class="code-along">▶ Code-along now → notebook Section 2 — DictReader → model_validate each row; a bad row raises</div>

---

<!-- _class: section -->

# Section 3 · JSON validation
## JSON already has types — but **not the right shape or limits**.
## The same model validates structure + constraints, not just coercion.

---

# 3.1 · JSON has types — but no guarantees

Unlike CSV, JSON carries real types (`499.0` is already a float). What it *doesn't* guarantee: the fields you need are present, named right, and within limits.

```json
{"id": 1, "name": "", "price": -5}    // valid JSON, invalid product
```

---

# 3.2 · The same model checks structure + limits

`model_validate` on the parsed JSON catches the **missing field**, the **wrong type**, and the **out-of-range value** — the "JSON schema & validation" step.

```python
import json
data = json.loads(raw)
Product.model_validate(data)   # missing name → error; price < 0 → error
```

<div class="code-along">▶ Code-along now → notebook Section 3 — validate JSON records; catch a bad shape</div>

---

<!-- _class: section -->

# Section 4 · Drive the API + report
## One bad row must **not** kill the batch.
## Keep the two failure kinds apart, and hand back a report of exactly what happened.

---

# 4.1 · A row fails in two different ways

Keep them apart — they need different fixes, and collapsing them lies to the operator.

| Failure | Where | Fix |
|---|---|---|
| **bad data** | never reaches the API (`ValidationError`) | fix the row |
| **server says no** | well-formed, rejected (409 duplicate) | fix the conflict |

---

# 4.2 · The loop — validate, send, bucket

`try` each step; on failure, drop the row into the right bucket and `continue`. One bad row never stops the batch.

```python
for n, row in enumerate(rows):
    try:    product = Product.model_validate(row)
    except ValidationError as e: bad_data.append({"row": n, "errors": e.errors()}); continue
    try:    client.create_product(product); created.append(product.id)
    except APIError as e:        rejected.append({"row": n, "status": e.status_code})
```

---

# 4.3 · The report is the product

The CSV/JSON was the input; this is what you hand back — and what Day 3 tests.

```python
report = {"created": created, "validation_errors": bad_data, "api_errors": rejected}
json.dump(report, open("import_report.json", "w"), indent=2)
```

<div class="code-along">▶ Code-along now → notebook Section 4 — the bulk-import loop + write import_report.json</div>

---

<!-- _class: lab -->

# 🧪 Lab 6 — Bulk-Import Workflow

**~60 min** · open `labs/lab-06-bulk-import/README.md`

You'll build (on `Product`):
- `data/products.csv` with some deliberately bad rows
- `catalog/import_csv.py` — read → validate → `POST` via `APIClient` → `import_report.json`
- the report: `{created, validation_errors, api_errors}`

End of Day 2 → your repo matches `checkpoints/day-3-start/`.
