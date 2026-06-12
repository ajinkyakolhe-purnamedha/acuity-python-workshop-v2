# Lab 10 — Natural-Language Query → Catalog Filter

**Duration:** ~80 min · **Day:** 4 · **Module:** 10 (LLM Fundamentals + Structured Outputs)

> **Concepts used:** OpenAI `chat.completions.create`, JSON mode (`response_format`), Pydantic `model_validate_json`, dependency-injected `llm_client` → `codealong/module-10.ipynb`.
> Reuses Day-2's `APIClient` as the data layer and Day-3's injection-for-testability seam — now the injected object is the **LLM client**, not a `requests.Session`. **No agent loop, no tools yet** — that's Lab 11.

## Goal
Take a free-form question — *"show me electronics under ₹5000 in stock"* — and use **one** LLM call to convert it into a **Pydantic-validated** `CatalogQuery` object your code can execute against the `APIClient`. The lesson: **make the LLM speak your schema, not English you have to re-parse.** Validate everything the model returns through Pydantic — that's the contract.

## You start with
- `project/checkpoints/day-4-start/` (Day 3 end-state — full `APIClient` + Pydantic `Product`) OR your own Lab 9 folder.
- An OpenAI-compatible API key (`export OPENAI_API_KEY=…`).
- `starter/catalog/agent.py` — `NL_QUERY_SYSTEM` and the four `CatalogQuery` fields are **given**; you fill the two function bodies (`parse_nl_query`, `apply_query`).

## You'll end with
- `catalog/agent.py` — `CatalogQuery` (Pydantic), `parse_nl_query(prompt) -> CatalogQuery`, `apply_query(query, api) -> list[dict]`
- A REPL session where typing a question returns the right products (shown in **Expected output**).

## Starter files
```bash
cp ../labs/lab-10-nl-query-filter/starter/catalog/agent.py catalog/   # run from my-catalog/
```

| File | You write |
|---|---|
| `starter/catalog/agent.py` | bodies of `parse_nl_query` and `apply_query`. `NL_QUERY_SYSTEM`, the imports, and the four `CatalogQuery` fields are **given** — sharpen each `Field(description=…)`, but don't rename or retype the fields. |

## Steps

1. **Sharpen the schema.** The four fields (`category`, `max_price`, `in_stock_only`, `name_contains`) are declared for you. Tighten each `description=` — **it is not decorative, the LLM reads it.** Say what valid values look like and what `null` means:
   ```python
   category: Optional[str] = Field(
       default=None,
       description="Restrict to this category (e.g. 'Electronics'), or null for all.")
   ```

2. **Write `parse_nl_query` — force JSON, then validate.** One LLM call; the injected `llm_client` is the mock seam (default to a real client):
   ```python
   def parse_nl_query(prompt, llm_client=None, *, model="gpt-4o-mini") -> CatalogQuery:
       client = llm_client or default_openai_client()
       response = client.chat.completions.create(
           model=model,
           messages=[
               {"role": "system", "content": NL_QUERY_SYSTEM},
               {"role": "user", "content": prompt},
           ],
           response_format={"type": "json_object"},   # <- forces parseable JSON
       )
       raw = response.choices[0].message.content or "{}"
       return CatalogQuery.model_validate_json(raw)    # <- never trust raw JSON
   ```

3. **Write `apply_query` — pure Python, no LLM.** Start from `api.list_products()`, narrow by each field that is *set* (skip the null ones), and dump to dicts:
   ```python
   def apply_query(query, api) -> list[dict]:
       items = api.list_products()
       if query.category:
           items = [p for p in items if p.category.lower() == query.category.lower()]
       if query.max_price is not None:        # guard None — 0 is a valid bound
           items = [p for p in items if p.price <= query.max_price]
       if query.in_stock_only:
           items = [p for p in items if p.in_stock]
       if query.name_contains:
           needle = query.name_contains.lower()
           items = [p for p in items if needle in p.name.lower()]
       return [p.model_dump() for p in items]
   ```

4. **Drive it from a REPL** (with the server running — `uvicorn catalog.server:app`):
   ```python
   from catalog.agent import parse_nl_query, apply_query
   from catalog.client import APIClient

   q = parse_nl_query("show me electronics under 5000 that are in stock")
   print(q)
   for row in apply_query(q, APIClient()):
       print(row["id"], row["name"], row["price"])
   ```

5. **Watch the schema work for you.** Ask a nonsense question (*"give me products that taste like pizza"*) and confirm the parser either returns an empty/null-filled `CatalogQuery` (which then filters to nothing) or raises a clean `ValidationError`. Either is acceptable — **silently lying isn't**. That's exactly what `model_validate_json` buys you.

## Expected output

```python
>>> q = parse_nl_query("show me electronics under 5000 that are in stock")
>>> print(q)
CatalogQuery(category='Electronics', max_price=5000.0, in_stock_only=True, name_contains=None)

>>> for row in apply_query(q, APIClient()):
...     print(row["id"], row["name"], row["price"])
1   USB-C Cable          499.0
3   Bluetooth Speaker   2499.0
```

## Common pitfalls
- Forgetting `response_format={"type": "json_object"}` — the LLM returns prose, `model_validate_json` explodes.
- Vague `description=` fields. *"Filter the category"* doesn't tell the model what valid values look like. Better: *"Restrict to this category (e.g. 'Electronics'), or null for all."*
- Trusting the LLM's JSON without `model_validate_json`. **Always** parse through Pydantic — that's the contract.
- `if query.max_price:` drops a legitimate `max_price=0`. Use `is not None`.
- Using positional examples (`["Electronics"]`) in the prompt — the model quotes you literally. Prefer abstract descriptions.

## Stretch (optional) — the fine-tuning tie-in
Turn the schema discipline into **data**. This is the data-driven habit from Day 2 / M6 (CSV import) plus the golden-eval from M12.

1. **Generate `tuning.jsonl` yourself** — write ~10–15 example pairs by hand, each a chat-format line mapping an NL query to the *correct* `CatalogQuery` JSON. (Don't look for a ready file — building the dataset is the exercise.)
   ```python
   import json
   examples = [
       ("show me electronics under 5000 that are in stock",
        CatalogQuery(category="Electronics", max_price=5000, in_stock_only=True)),
       ("anything with 'cable' in the name", CatalogQuery(name_contains="cable")),
       # … add your own tricky ones (negations, multiple constraints, nonsense)
   ]
   with open("tuning.jsonl", "w") as f:
       for nl, q in examples:
           f.write(json.dumps({"messages": [
               {"role": "system", "content": NL_QUERY_SYSTEM},
               {"role": "user", "content": nl},
               {"role": "assistant", "content": q.model_dump_json()},
           ]}) + "\n")
   ```
2. **Hold out 3–4 pairs** and write a tiny accuracy check: run `parse_nl_query` on each held-out NL query and compare the parsed `CatalogQuery` against the expected one. Print `correct / total`. (This is a golden-eval in miniature — the same idea M12 scales up.)
3. Note what *would* improve with a fine-tuned model: the JSONL you just wrote is exactly the training-file shape OpenAI fine-tuning expects, so the held-out check becomes your **base-vs-tuned** comparison once a tuned model id exists.
