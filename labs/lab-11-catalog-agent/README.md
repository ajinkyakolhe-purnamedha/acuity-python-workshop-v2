# Lab 11 — Build the `CatalogAgent`

**~80 min · Day 4 · Module 11** — wrap your `APIClient` methods as LLM-callable **tools** and run the *plan → act → observe* loop.

Concepts → `codealong/module-11.ipynb`. Tools are Python functions registered with a decorator (the M5 decorators return); the injected `llm_client` is the same seam Day-3 used for `requests.Session`.

## Prereqs — local LLM, no API key

Same as Lab 10 — a lightweight model on your laptop via [Ollama](https://ollama.com):

```bash
ollama pull qwen2.5:3b     # ~1.9 GB, supports tool-calling
ollama serve               # http://localhost:11434
```
Real OpenAI → `export OPENAI_API_KEY=sk-…`. Stronger model → `export LLM_MODEL=qwen2.5:7b`.

## Goal

An LLM that **calls your `APIClient` methods as tools**: it proposes a call, your code runs it, feeds the result back, and the LLM calls again or answers. By the end, `agent.ask("what's our most expensive product?")` makes the model call `list_products`, reason over the data, and answer in plain language.

## You start with → you'll end with

| Start | End |
|---|---|
| Lab 10 done (`CatalogQuery` + `parse_nl_query`) | `CatalogAgent`: `_build_registry` (4 tools), `ask()` loop, `_invoke_tool` |
| `starter/catalog/agent.py` — **all plumbing given** (`ToolSpec`, `ToolRegistry`, `@registry.tool`, result types, injected `llm_client`) | tools: `list_products`, `search_products`, `count_by_category`, `update_price` |

```bash
cp ../labs/lab-11-catalog-agent/starter/catalog/agent.py catalog/   # from my-catalog/
```
You fill **three method bodies**; everything else is given.

## Steps

1. **Read the plumbing** — `ToolSpec` + `ToolRegistry` + `@registry.tool`. Same three-layer decorator as Day-1/2 `@retry`. `registry.openai_schemas()` renders OpenAI's `tools=[...]`. Don't rewrite it.
2. **`_build_registry` — register four tools.** Each is a nested fn closing over `self.api`, returning **JSON-friendly** values (`model_dump()` every `Product`):
   ```python
   @registry.tool(name="search_products",
       description="Find products whose name contains a substring (case-insensitive).",
       parameters={"type":"object","properties":{"term":{"type":"string"}},
                   "required":["term"],"additionalProperties":False})
   def search_products(term: str) -> list[dict]:
       return [p.model_dump() for p in self.api.list_products()
               if term.lower() in p.name.lower()]
   ```
   Same for `list_products` (no params), `count_by_category` (no params), `update_price(product_id, new_price)`. End `return registry`.
3. **`ask` — the loop, with `tool_call_id` chaining** (the #1 breakage). Seed `messages` with `SYSTEM_PROMPT` + the user turn, loop to `max_steps`: call the LLM with `tools=…`; no `tool_calls` → return `AgentResult`. Else append the **assistant message with its `tool_calls`**, then **one `{"role":"tool","tool_call_id":call.id,…}` message per call**. Mismatch the id → the next call 400s. (Same loop as `module-11.ipynb` cell 7.)
4. **`_invoke_tool` — run one tool, never crash.** `registry.get(name)` in try/except `KeyError` → `{"error":…}`; `_parse_args` the JSON; call `spec.fn(**kwargs)` in try/except → `{"error":…}`. The model reads the error and recovers.
5. **Demo it** (Ollama + `uvicorn catalog.server:app` running):
   ```python
   from catalog.agent import CatalogAgent
   from catalog.client import APIClient
   r = CatalogAgent(APIClient()).ask("what's our most expensive product?")
   print(r.answer); print([(c.tool, c.arguments) for c in r.tool_calls])
   ```

## Expected output

```
The most expensive product is the Mechanical Keyboard, at ₹5,499.
[('list_products', {})]
```
The model called `list_products` once, read the data, then answered. Both "answer directly" and "call another tool" are valid loop outcomes.

## Pitfalls

- Returning a Pydantic `Product` from a tool — the tool-message body must be a string. `model_dump()` then `json.dumps(...)`.
- Missing/mismatched `tool_call_id` on the tool message → the next LLM call rejects the conversation. **The most common break.**
- Re-creating the client every `ask()` — build it once in `__init__` (the injected `self.llm`).
- Swallowing errors as `{}` in `_invoke_tool` → the model loops confused. Return `{"error":…}`.
- **Small models fumble tool-calling.** `qwen2.5:3b` mostly works but may skip a tool or malformat args. If it won't call a tool, `export LLM_MODEL=qwen2.5:7b` — the loop code is identical.

## Stretch

- Add a `delete_product` tool + a **confirmation step**: the LLM proposes, your code asks y/n, executes only on yes.
- You already swapped OpenAI → **Ollama** through the injection seam (only `default_openai_client()` changed). Swapping to Anthropic is the same move — registry + loop stay identical.
