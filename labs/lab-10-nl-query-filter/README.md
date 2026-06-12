# Lab 10 — Natural-Language Query → Catalog Filter

**~80 min · Day 4 · Module 10** — make the LLM speak your schema, not English you re-parse.

Concepts → `codealong/module-10.ipynb`. One LLM call — **no agent loop, no tools** (that's Lab 11). Reuses Day-2 `APIClient` + the Day-3 injection seam, except the injected object is now the **LLM client**.

## Prereqs — local LLM, no API key

A lightweight open-source model on your laptop via [Ollama](https://ollama.com). The code is just the OpenAI SDK pointed at Ollama — swapping to real OpenAI later changes nothing in `agent.py` (that's the dependency-injection lesson).

```bash
ollama pull qwen2.5:3b     # ~1.9 GB, one-time
ollama serve               # http://localhost:11434 (often already up)
pip install openai         # the SDK talks to Ollama — no key needed
```
Real OpenAI instead → `export OPENAI_API_KEY=sk-…`. Stronger model → `export LLM_MODEL=qwen2.5:7b`.

## Goal

Turn *"electronics under 5000 in stock"* into a **Pydantic-validated `CatalogQuery`** with one LLM call, then run it as a pure-Python filter over the `APIClient`. Validate everything the model returns — the schema is the contract.

## You start with → you'll end with

| Start | End |
|---|---|
| `project/checkpoints/day-4-start/` (or your Lab 9) | `catalog/agent.py`: `CatalogQuery`, `parse_nl_query`, `apply_query` |
| `starter/catalog/agent.py` — schema + `NL_QUERY_SYSTEM` given; **two bodies are TODO** | a REPL where a question returns the right rows |

```bash
cp ../labs/lab-10-nl-query-filter/starter/catalog/agent.py catalog/   # from my-catalog/
```

## Steps

1. **Sharpen the schema.** The four `CatalogQuery` fields are given — tighten each `Field(description=…)` (the LLM reads it). Say what valid values and `null` mean. Don't rename or retype fields.
2. **`parse_nl_query` — force JSON, then validate.** One call with `response_format={"type":"json_object"}`, then `CatalogQuery.model_validate_json(raw)`. Never trust raw JSON.
3. **`apply_query` — pure Python, no LLM.** Start from `api.list_products()`, narrow by each field that is *set* (skip nulls), `return [p.model_dump() for p in items]`. Guard `max_price is not None` — `0` is a valid bound.
4. **Drive it from a REPL** (Ollama + `uvicorn catalog.server:app` both running).
5. **Prove the schema protects you.** Ask nonsense (*"products that taste like pizza"*) → expect an empty/null `CatalogQuery` or a clean `ValidationError`. Silently lying is the only wrong answer.

## Expected output

```python
>>> q = parse_nl_query("show me electronics under 5000 that are in stock")
>>> print(q)
CatalogQuery(category='Electronics', max_price=5000.0, in_stock_only=True, name_contains=None)
>>> for row in apply_query(q, APIClient()): print(row["id"], row["name"], row["price"])
1   USB-C Cable          499.0
3   Bluetooth Speaker   2499.0
```

## Pitfalls

- Skipping `response_format={"type":"json_object"}` → the model returns prose → `model_validate_json` explodes.
- Vague `description=` → vague queries. State the valid values **and** the null case.
- `if query.max_price:` drops a valid `max_price=0` — use `is not None`.
- **Small models drift on JSON.** `qwen2.5:3b` may add a field or return prose — re-run, or `export LLM_MODEL=qwen2.5:7b`. (This is *why* you validate.)

## Stretch — fine-tuning tie-in

Hand-write ~10–15 `(NL query → CatalogQuery JSON)` pairs as chat-format JSONL, hold out 3–4, and score `parse_nl_query` against them (`correct/total`) — a golden-eval in miniature (M12). That JSONL is the exact OpenAI fine-tuning shape; **running** a tune job needs `OPENAI_API_KEY` (Ollama doesn't fine-tune).
