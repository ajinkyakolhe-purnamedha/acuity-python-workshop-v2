---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 1 · Build It — Clean Python to a Local API"
footer: "Acuity Training · Day 1 of 4"
---

<!-- _class: title -->

# Day 1
## Python Fundamentals
## **+ build the Catalog Foundation**

6 hours · 3 modules · 3 labs · one repo for the week

---

# What we build today

By 6 PM, a **local FastAPI server** running on your laptop, serving a `Product` catalog you wrote from scratch.

- Module 1 → Python core → Lab 1: `Product` foundation
- Module 2 → Data structures, files, modules → Lab 2: Persistent catalog
- Module 3 → OOP, decorators, FastAPI → Lab 3: Local API server

**Same repo carries through Day 2, 3, 4.** No throwaway demos.

---

# The week, in one picture

```
Day 1   Product class + FastAPI server
Day 2   + Pydantic + APIClient + CSV bulk-import
Day 3   + pytest suite + mocks + CI green
Day 4   + LLM-powered CatalogAgent + agent tests
```

Every day extends yesterday's project (your `my-catalog/`).
A catch-up baseline (`day-N-start/`) is provided each morning.

---

<!-- _class: title -->

# Module 1
## Python Core
**6 sections · ~40 min** — each builds on the last; we code each one live
1 Variables · 2 Control flow · 3 Functions · 4 Exceptions · 5 Zen of Python · 6 Revision

---

# Our story for today: bank accounts

Every example today is one **account**. In Python an account is just a `dict` — named fields, no class yet (classes come in Module 3).

```python
acct = {"id": 1, "owner": "Ada", "account_type": "savings",
        "balance": 1500.0, "is_active": True,
        "tags": ["primary", "online"]}
```

Same six fields all day. M2 stores many of these in files; M3 turns them into a class.

---

<!-- _class: section -->

# Section 1 · Variables
## variables & operations → types → hints → list / dict → the account

---

# 1.1 · Variables & operations

A variable is a name pointing at a value; you don't declare a type, Python infers it. Then you **operate** on those values.

```python
owner = "Ada"; balance = 1500.0; rate = 0.04
balance = balance + balance * rate    # arithmetic on numbers
label = "owner: " + owner             # + joins strings
wealthy = balance > 5000              # comparison → a bool
```

---

# 1.2 · Types — one per kind

`type(x)` reveals the kind Python inferred for a value. The account's fields cover Python's core types.

```python
print(type("Ada"))     # <class 'str'>
print(type(1))         # <class 'int'>
print(type(1500.0))    # <class 'float'>
print(type(True))      # <class 'bool'>
print(type(None))      # <class 'NoneType'>
```

---

# 1.3 · Type hints — just a hint

A variable can hold **any** type, and you can rebind it to another at runtime. A **type hint** (`name: type`) documents intent — it is **not enforced**.

```python
balance = 1500.0      # float now...
balance = "frozen"    # ...str later — Python allows it

balance: float = 1500.0   # a hint; it still won't stop balance = "frozen"
```

---

# 1.4 · Advanced variables — list & dict

When one value isn't enough: a **list** holds many in order; a **dict** holds named fields you look up by key.

```python
tags: list[str] = ["primary", "online"]            # ordered, indexable
acct: dict = {"owner": "Ada", "balance": 1500.0}   # look up by key
```

---

# 1.5 · Using list & dict

Read a **list** by index, a **dict** by key — and each carries handy methods.

```python
tags[0]; len(tags)            # "primary" ; 2
acct["owner"]; acct.get("x")  # "Ada" ; None (safe — no KeyError)
acct.keys(); acct.values()    # the field names ; the values
acct.items()                  # (key, value) pairs — great for loops
```

---

# 1.6 · An account = every type, in one dict

Put it together: one bank account is just a `dict` whose fields span all the types we met. **This is our domain object for the whole course.**

```python
acct = {"id": 1, "owner": "Ada", "account_type": "savings",
        "balance": 1500.0, "is_active": True, "tags": ["primary", "online"]}
```

<div class="code-along">▶ Code-along now → notebook Section 1 — variables & ops → types → hints → list/dict → the account</div>

---

<!-- _class: section -->

# Section 2 · Control flow
## truthiness · if / elif / else · for · while

---

# 2.1 · Truthiness — empty things are False

You can test a value straight in `if`. "Empty" / "zero" values are **falsy**: `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False`. Everything else is truthy.

```python
if not acct["tags"]:        # empty list is falsy
    print("no tags yet")
```

---

# 2.2 · Branching — if / elif / else

`if/elif/else` picks exactly one branch. **Indentation** (not braces) marks the block.

```python
if not a["is_active"]:   label = "inactive"
elif a["balance"] < 100: label = "low balance"
else:                    label = "healthy"
```

---

# 2.3 · Loops — for (and while)

`for` walks any sequence — a list, a dict's `.items()`, a counter via `enumerate`, or a numeric `range`. `while` repeats until a condition flips.

```python
for a in accounts: ...                # over a list
for key, value in acct.items(): ...   # over a dict's pairs
for i, a in enumerate(accounts): ...  # i is the counter: 0, 1, 2…
for n in range(3): ...                # 0, 1, 2
while sam["balance"] < 100: ...       # repeat until it clears 100
```

<div class="code-along">▶ Code-along now → notebook Section 2 — branch accounts by status, top up a balance with <code>while</code></div>

---

<!-- _class: section -->

# Section 3 · Functions
## arguments & defaults · return · type hints · *args / **kwargs

---

# 3.1 · Functions — arguments, defaults, return

`def` names reusable logic. **Arguments** feed it; parameters can carry **default values**; `return` hands a result back.

```python
def total_balance(accounts, only_active=True):   # only_active defaults to True
    return sum(a["balance"] for a in accounts if a["is_active"])
```

---

# 3.2 · Type hints on functions

Annotate the parameters and the return type. As with variables, hints **document** the signature — Python does **not** enforce them; a wrong type still runs.

```python
def total_balance(accounts: list[dict], only_active: bool = True) -> float:
    ...
total_balance("oops")   # a type checker complains; Python runs it anyway
```

---

# 3.3 · Flexible args — *args / **kwargs

`*args` collects extra **positional** args into a tuple; `**kwargs` collects extra **keyword** args into a dict — handy for "any number of fields."

```python
def open_account(**fields):      # fields is a dict
    return {"is_active": True, **fields}
open_account(id=2, owner="Lin", balance=800.0)
```

<div class="code-along">▶ Code-along now → notebook Section 3 — <code>total_balance()</code> with hints, then a <code>**kwargs</code> factory</div>

---

<!-- _class: section -->

# Section 4 · Exceptions
## raise · try / except / else / finally

---

# 4.1 · raise — business logic as a readable error

`raise` an error instead of returning a bad value (or a silent `None`). A good error is **business logic made readable** — the type + message say exactly which rule broke.

```python
def find_account(accounts, acct_id):
    for a in accounts:
        if a["id"] == acct_id: return a
    raise LookupError(f"no account with id={acct_id}")
```

---

# 4.2 · try / except / else / finally

`try` the risky code, `except` the failure, `else` runs only on success, `finally` always runs (cleanup).

```python
try:    acct = find_account(accounts, 99)
except LookupError as err: print("not found:", err)
else:   print("found:", acct["owner"])
finally:print("lookup done")
```

<div class="code-along">▶ Code-along now → notebook Section 4 — raise on overdraft & missing id, handle both</div>

---

<!-- _class: section -->

# Section 5 · The Zen of Python
## clean code: easy to read, easy to maintain

---

# 5.1 · Zen of Python — write for the reader

`import this` prints Python's creed. It's really about **clean, maintainable code** — code is read far more often than it's written.

> "If you write code as cleverly as possible, you are *not* clever enough to debug it."

Favour **clear over clever**: explicit > implicit, simple > complex, flat > nested.

---

# 5.2 · Clean code in practice

Say what you mean, the obvious way — the reader (often future-you) should grasp each line at a glance.

```python
if len(tags) == 0: ...   # clever / noisy   →   if not tags: ...   # clear
```

**Flat > nested:** return early (a guard clause) instead of wrapping the body in `if`.

---

# 5.3 · Names & explicit types

The cheapest readability wins: **honest names** and **explicit type hints**. A good name removes the need for a comment.

```python
def calc(x): ...                              # what is x? what comes back?
def total_active_balance(accounts: list[dict]) -> float: ...   # name + hints tell the story
```

<div class="code-along">▶ Code-along now → notebook Section 5 — rename for clarity, add explicit hints, flatten the flow</div>

---

<!-- _class: section -->

# Section 6 · Revision
## the four moves, together

---

# 6.1 · The four moves, one picture

| Move | Tool |
|---|---|
| store one thing with named fields | `dict` |
| choose / repeat | `if / elif / else`, `for`, `while` |
| reuse logic, hand back a result | `def … return` |
| fail clearly, recover | `raise`, `try / except` |

Plus the Zen: clear names, explicit type hints, readable flow.

<div class="code-along">▶ Code-along now → notebook Section 6 — one little bank exercising all four moves</div>

---

<!-- _class: lab -->

# 🧪 Lab 1 — The `Product` Foundation

**80 min** · open `labs/lab-01-product-foundation/README.md` · scaffolds in `starter/`

You'll build (now on `Product`, not `BankAccount`):
- `catalog/models.py` — product dict factory + catalog list functions
- `catalog/cli.py` — `list`, `add` subcommands

End state: `python -m catalog.cli list` prints 5 seeded products.

---

<!-- _class: title -->

# Module 2
## Lists, Dicts & Files
**4 sections · ~40 min** — each builds on the last; we code each one live
1 Lists & CSV · 2 Dicts & JSON · 3 Organizing via functions · 4 Logging

---

# From one account to many

Module 1 left us with **one** account — a `dict`. A bank has many, and they must outlive the program.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0, ...}   # M1: one account, in memory
```

Today: **many** accounts in the two containers that matter — `list` and `dict` — saved to **files** (CSV, JSON). The third, most powerful structure — a **class** — is Module 3.

---

<!-- _class: section -->

# Section 1 · Lists & CSV
## elements → slice → loop → comprehension → CSV → with type hints

---

# 1.1 · List elements — index

A **list** holds many values in order. Build it with `[...]`; read any item by its **index** (0-based; negatives count from the end).

```python
owners = ["Ada", "Lin", "Sam"]
owners[0]    # "Ada"  (first)
owners[-1]   # "Sam"  (last)
```

---

# 1.2 · Slicing

A **slice** `[start:stop]` returns a sub-list — `stop` is excluded. Omit a side to run to the edge.

```python
owners[0:2]   # ['Ada', 'Lin']
owners[1:]    # ['Lin', 'Sam']
```

---

# 1.3 · Length & looping

`len()` counts the items; a `for` loop walks them in order.

```python
len(owners)            # 3
for name in owners:
    print(name)        # Ada / Lin / Sam
```

---

# 1.4 · List comprehension

Build a new list from an old one in one line — say *what*, not *how*. Add an `if` to filter.

```python
upper = [name.upper() for name in owners]          # transform → ['ADA','LIN','SAM']
with_a = [n for n in owners if n.startswith("A")]  # filter   → ['Ada']
```

---

# 1.5 · A CSV row is a list

The most common real-world data is a **CSV**. Read it with `csv.reader` — **each row comes back as a list** of strings.

```python
import csv
for row in csv.reader(open("accounts.csv")):
    row    # ['1', 'Ada', '1500.0']  — a list; every value is a str
```

---

# 1.6 · Reading a CSV file — the ways

The **header** is just the first row. Split it off and loop the rest, or let `DictReader` pair each value with its column name.

```python
rows = list(csv.reader(open("accounts.csv")))
header, data = rows[0], rows[1:]        # header row vs the data rows
# or: csv.DictReader(...) -> each row a dict keyed by header (→ Section 2)
```

---

# 1.7 · Now with type hints — best practice

We introduced lists plainly. **From here on, annotate them.** A hint on a collection (`list[str]`, `list[list[str]]`) and on a function signature lets editors and tools catch mistakes *before* you run — for free.

```python
owners: list[str] = ["Ada", "Lin", "Sam"]
rows: list[list[str]] = list(csv.reader(open("accounts.csv")))

def first_n(owners: list[str], n: int) -> list[str]:
    return owners[:n]
```

<div class="code-along">▶ Code-along now → notebook Section 1 — list ops → comprehension → CSV as lists → with type hints</div>

---

<!-- _class: section -->

# Section 2 · Dicts & JSON
## access → loop → functions → nested → JSON → with type hints

---

# 2.1 · Dict element access

A **dict** stores named fields looked up by **key**, not position. `[key]` raises if missing; `.get(key)` returns `None` safely.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0}
acct["owner"]        # "Ada"
acct.get("phone")    # None — no KeyError
```

---

# 2.2 · Dict looping

Loop the keys, the values, or both together with `.items()`.

```python
for key in acct: ...               # keys
for value in acct.values(): ...    # values
for key, value in acct.items():    # both
    print(key, "=", value)
```

---

# 2.3 · Important dict functions

Add or overwrite by assignment or `update`; test membership with `in`; remove with `pop`.

```python
acct["balance"] = 1600.0           # update one field
acct.update({"tier": "gold"})      # add / merge fields
"owner" in acct                    # True
```

---

# 2.4 · Nested dicts

Values can themselves be lists or dicts — real records **nest**. Reach in by chaining keys.

```python
acct = {"owner": "Ada",
        "address": {"city": "Pune"},
        "tags": ["primary", "online"]}
acct["address"]["city"]   # "Pune"
```

---

# 2.5 · Save & load with JSON

A dict maps exactly to **JSON**. `json.dump` writes it to disk; `json.load` reads it straight back **as a Python dict** — same shape, no parsing.

```python
import json
json.dump(acct, open("acct.json", "w"), indent=2)   # dict → file
back = json.load(open("acct.json"))                  # file → dict again
```

---

# 2.6 · Now with type hints

Type a dict by its **key and value** types. Uniform values type precisely; our account **mixes** types, so the honest hint is `dict[str, object]` — and that vagueness is the signal that a fixed-field record wants a **class** (Module 3).

```python
balances: dict[str, float] = {"Ada": 1500.0, "Lin": 800.0}             # uniform → precise
acct: dict[str, object] = {"id": 1, "owner": "Ada", "balance": 1500.0} # mixed → vague → want a class
```

<div class="code-along">▶ Code-along now → notebook Section 2 — access & loop → nested → JSON round-trip → with type hints</div>

---

<!-- _class: section -->

# Section 3 · Organizing dict access via functions
## a store → insert/update → fetch → the seam → with type hints

---

# 3.1 · A dict as the store

Keep all accounts in one dict keyed by id — **instant (O(1))** lookup by account number.

```python
accounts = {}                       # {id: account}
accounts[1] = {"id": 1, "owner": "Ada", "balance": 1500.0}
accounts[1]                         # lookup by id, no scanning
```

---

# 3.2 · insert & update via functions

Wrap the writes in functions — one place owns "add" and "change", so every caller behaves the same.

```python
def insert(store, acct):           store[acct["id"]] = acct
def update(store, id, **changes):  store[id].update(changes)
```

---

# 3.3 · fetch via a function

A `fetch` function hides the lookup — and gives one place to validate, default, or raise on a missing id.

```python
def fetch(store, id):
    if id not in store:
        raise LookupError(f"no account id={id}")
    return store[id]
```

---

# 3.4 · The seam: JSON today, a database tomorrow

These functions hide **where** the data lives. Today they read/write a JSON file; later the same `insert`/`fetch` talk to a **database or data warehouse** — callers never change.

```python
# today:    store = json.load(open("accounts.json"))
# tomorrow: store = db.query("SELECT ...")   # same insert()/fetch() on top
```

---

# 3.5 · Now with type hints

Typed signatures make the storage layer **self-documenting**: the store is `dict[int, dict]`, an id is `int`, `fetch` returns a `dict`.

```python
def insert(store: dict[int, dict], acct: dict) -> None:
    store[acct["id"]] = acct

def fetch(store: dict[int, dict], id: int) -> dict:
    ...
```

<div class="code-along">▶ Code-along now → notebook Section 3 — store + insert/update/fetch, backed by JSON → with type hints</div>

---

<!-- _class: section -->

# Section 4 · Logging
## levels → applied to the storage

---

# 4.1 · Logging vs print

`print` is for throwaway scripts; real code uses **`logging`** — levels (`DEBUG < INFO < WARNING < ERROR`) dial detail up or down without deleting lines.

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bank")
log.info("started")     # shown · log.debug("...") hidden at INFO
```

---

# 4.2 · Logging the storage

Add one line to each storage op — now every `insert`/`update`/`fetch` and the JSON load leaves an **audit trail**.

```python
def fetch(store, id):
    log.info("fetch id=%s", id)     # %s args, not an f-string
    return store[id]
```

<div class="code-along">▶ Code-along now → notebook Section 4 — add logging to the Section-3 storage functions</div>

---

<!-- _class: lab -->

# 🧪 Lab 2 — Persistent Catalog

**80 min** · open `labs/lab-02-persistent-catalog/README.md` · scaffolds in `starter/`

You'll build (on `Product`, not `BankAccount`):
- `catalog/storage.py` — save/load the catalog as JSON and CSV
- comprehension-powered `search_by_name`, `filter_by_price`
- `search` / `save` / `load` CLI subcommands

End state: your catalog **survives a process restart**.

---

<!-- _class: title -->

# Module 3
## OOP, Dataclasses & FastAPI
**4 sections · ~40 min** — each builds on the last; we code each one live
1 The class by hand · 2 @dataclass · 3 Inheritance · 4 FastAPI

---

# From a dict to a class

Module 2 left an account as a `dict` + loose `insert/update/fetch` functions — and a **mixed-value dict that was hard to type** (§2.6). The fix: a **class** — fields *and* behavior in one typed object.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0}   # M2: a bare dict
ada  = BankAccount(1, "Ada", 1500.0)                   # M3: an object with methods
```

Today: build the class by hand → shortcut it with `@dataclass` → specialize with inheritance → expose it over HTTP.

---

<!-- _class: section -->

# Section 1 · OOP — the class by hand
## why → class/__init__/self → attributes → methods

---

# 1.1 · Why a class

A `dict` holds data but no **behavior** and no **guardrails** — nothing stops `balance = -50` or a typo'd key. A **class** bundles the data *and* the operations that protect it.

```python
acct = {"owner": "Ada", "balance": 1500.0}   # data only — deposit/withdraw live elsewhere
```

---

# 1.2 · `class` + `__init__` + `self`

A **class** is a blueprint; an **object** is one thing built from it. `__init__` runs once when you build an object and sets up its data. `self` is *that* object.

```python
class BankAccount:
    def __init__(self, id, owner, balance):
        self.id = id; self.owner = owner; self.balance = balance

ada = BankAccount(1, "Ada", 1500.0)   # __init__ runs, returns the object
```

---

# 1.3 · Attributes — the data on an object

Attributes are the per-object data set in `__init__`. Read/write them with a **dot** — clearer than a dict's string key, and a typo is an *error*, not a silent `None`.

```python
ada.balance          # 1500.0   (vs d["balance"])
ada.owner = "Ada K." # set with the dot too
```

---

# 1.4 · Methods — behavior, with guardrails

A **method** is a function inside the class; its first parameter is `self`, the object. M2's loose functions become methods — and a method can `raise` to enforce a rule, so the data can't go invalid.

```python
class BankAccount:
    ...
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")   # the rule lives with the data
        self.balance -= amount
```

<div class="code-along">▶ Code-along now → notebook Section 1 — build BankAccount: __init__, attributes, a method with a guardrail</div>

---

<!-- _class: section -->

# Section 2 · @dataclass — the clean record
## boilerplate → @dataclass → the data-structure step → defaults → methods

---

# 2.1 · That's a lot of boilerplate

A real account has six fields. Writing `__init__` (plus a readable print, plus `==`) **by hand** for every field is tedious and easy to get wrong.

```python
def __init__(self, id, owner, account_type, balance, is_active, tags):
    self.id = id; self.owner = owner; ...   # ...repeat for every field
```

---

# 2.2 · `@dataclass` — the boilerplate, for free

Put `@dataclass` on top and just **list the typed fields**. You get `__init__`, a readable `__repr__` (how it prints), and `__eq__` (`==` by value) — written for you.

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float

print(BankAccount(1, "Ada", 1500.0))   # BankAccount(id=1, owner='Ada', balance=1500.0)
```

> The `@` is a **decorator** — *how* it works is its own later module. Here, treat it as a shortcut.

---

# 2.3 · The next data structure

The progression: **variable** (M1) → **list & dict** (M2) → **dataclass** (M3) — a typed, fixed-shape record. Exactly the fix for M2's "mixed-value dict you couldn't type cleanly."

```python
@dataclass
class BankAccount:
    id: int
    owner: str
    balance: float        # each field named AND typed — no more dict[str, object]
```

---

# 2.4 · Defaults & the tags field

Give a field a default after the typed ones. For a **mutable** default (a list), use `field(default_factory=list)` — never `tags: list = []` (one list shared across every account: the M1 trap).

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float
    is_active: bool = True
    tags: list[str] = field(default_factory=list)
```

---

# 2.5 · Behavior still lives on it

A dataclass is still a class — your methods sit right alongside the fields. Clean data **and** behavior, together.

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float = 0.0
    def withdraw(self, amount):
        if amount > self.balance: raise ValueError("insufficient funds")
        self.balance -= amount
```

<div class="code-along">▶ Code-along now → notebook Section 2 — migrate BankAccount to @dataclass: fields, defaults, keep the methods</div>

---

<!-- _class: section -->

# Section 3 · Inheritance
## is-a → inherit → override + super() → Pydantic

---

# 3.1 · Why inherit — *is-a*

A `SavingsAccount` **is a** `BankAccount` that also earns interest. Inheritance lets a new class reuse everything the parent has and add or change just the difference.

```python
@dataclass
class SavingsAccount(BankAccount):
    rate: float = 0.04        # plus everything BankAccount already has
```

---

# 3.2 · A subclass inherits everything

`SavingsAccount(BankAccount)` gets the parent's fields **and** methods for free — `withdraw`, `balance`, all of it — without rewriting them.

```python
s = SavingsAccount(1, "Ada", 1500.0)
s.withdraw(100)        # BankAccount's method, inherited as-is
```

---

# 3.3 · Override + `super()`

Redefine a method to **specialize** it; call `super().<method>()` to reuse the parent's logic and add to it.

```python
class SavingsAccount(BankAccount):
    def withdraw(self, amount):
        super().withdraw(amount)   # reuse the parent's guardrail
        self.balance -= 1          # then apply a savings withdrawal fee
```

---

# 3.4 · You'll see this again — Pydantic

Day 2's models are classes that **inherit** from Pydantic's `BaseModel`:

```python
class Product(BaseModel):   # is-a BaseModel → gets validation for free
    id: int
    name: str
```

Same `is-a` mechanism you just learned — `@dataclass` becomes `BaseModel`, plus runtime validation.

<div class="code-along">▶ Code-along now → notebook Section 3 — SavingsAccount(BankAccount): inherit, override withdraw with super()</div>

---

<!-- _class: section -->

# Section 4 · FastAPI — expose the catalog
## route = @app.get fn → build → run → where it goes

---

# 4.1 · A route is a function with `@app.get` on top

FastAPI turns a function into a web endpoint: put `@app.get("/path")` above it, and it runs when a request hits that path.

```python
app = FastAPI()

@app.get("/accounts")
def list_accounts():
    return ACCOUNTS
```

> That `@` is a decorator again — **use** it now; the Decorators module explains it.

---

# 4.2 · Build the server — GET & POST

One function per route. Return your objects and FastAPI serialises them to JSON; take a **path parameter** to fetch one.

```python
@app.get("/accounts/{id}")
def get_account(id: int):
    return fetch(STORE, id)

@app.post("/accounts")
def create(acct: dict):
    insert(STORE, acct); return acct
```

---

# 4.3 · Run it — `uvicorn` + `/docs`

Start the server, then hit it from a browser or curl. FastAPI generates **interactive docs** for free.

```bash
uvicorn catalog.server:app --reload
curl localhost:8000/accounts/1
# then open http://localhost:8000/docs
```

**This is the end-of-Day-1 artifact:** a running API serving a catalog you built.

---

# 4.4 · Where this goes

The same "register a function" shape returns on **Day 4**: an agent's **tools** are just functions the LLM is allowed to call — exactly like routes.

<div class="code-along">▶ Code-along now → notebook Section 4 — a FastAPI app over the accounts: GET, POST, run it</div>

---

<!-- _class: lab -->

# 🧪 Lab 3 — Local API Server

**80 min** · open `labs/lab-03-local-api-server/README.md` · scaffolds in `starter/`

You'll build (on `Product`, not `BankAccount`):
- `catalog/models.py` — `Product` as a class → `@dataclass` (typed fields, `field(default_factory=list)`)
- `catalog/server.py` — FastAPI app: `GET /products`, `GET /products/{id}`, `POST /products`
- a running server on `localhost:8000` with `/docs`

End of Day 1 → your repo serves a real catalog API.
