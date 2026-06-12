---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 4 · Add AI to the Catalog, then Test the AI"
footer: "Acuity Training · Day 4 of 4"
---

<!-- _class: title -->

# Day 4
## Add AI to the Catalog,
## **then test the AI**

6 hours · 3 modules · 3 labs · the day Day 3 was secretly setting up

---

# Three days of Python. Today, one new idea: the LLM.

You have a tested, CI-green catalog with a typed client. Today you bolt an **LLM agent** onto it — and lock it under the **same** testing discipline.

- **M10** — the LLM as a *task engine*; structured output + the improvement ladder
- **M11** — tools = functions; the plan→act→observe loop
- **M12** ⭐ — test the AI: shape & behaviour, not prose

The agent's tools **are** the `APIClient` you built Day 2. The LLM is injected like the `Session` was Day 3.

Catch-up: `cp -r ../project/checkpoints/day-4-start/. .`

---

# Today's arc

| Module | ~40 min teach | 80 min lab |
|---|---|---|
| M10 | LLM as task engine + structured output | Lab 10: NL query → `CatalogQuery` |
| M11 | Tools as functions + agent loop | Lab 11: build `CatalogAgent` |
| M12 ⭐ | **Testing AI tools & outputs** | Lab 12: test the agent |

End-of-day: an agentic, **tested** Python system on your laptop — no new framework.

---

<!-- _class: title -->

# Module 10
## The LLM as a Task Engine
**~40 min · then 80 min lab** — aim a text-in/text-out engine at a task, then improve it up a ladder

---

# 10.1 · AI → ML → GenAI → Agentic

```text
AI           any system that "appears intelligent"
ML           systems that learn patterns from data
GenAI        ML that produces novel text / images / code
Agentic AI   GenAI + tools + a loop + a goal
```

The **agent is the loop around the LLM**, not the LLM itself. The LLM is a stateless string-to-string machine; the state — **tools, memory, goals — lives in *your* code.** That's why Day 1–3 Python matters: you write the loop.

---

# 10.2 · The LLM is a task engine

Text in → text out, **aimed at a task.** Every useful call is one of a handful of tasks:

| Task | "Given text, produce…" |
|---|---|
| **classify** | a label (priority = high/low) |
| **extract** | structured fields (a `CatalogQuery`) |
| **summarize** | a shorter text |
| **generate** | new text (a reply draft) |
| **transform** | reshaped text (NL → JSON) |
| **reason** | a decision + which tool to call next |

Each is **spec'able**: define the input, the output shape, the constraints. M11's tools are just "reason → pick a task."

---

# 10.3 · Tokens · context · cost · latency

| | what it is | rule of thumb |
|---|---|---|
| Token | piece of a word | ≈ ¾ of an English word |
| Context | tokens visible at once | 128k for `gpt-4o-mini` |
| Input cost | ₹/$ per M input tokens | ~$0.15 / M in |
| Output cost | ₹/$ per M output tokens | ~$0.60 / M out |
| Latency | time to first token | ~500 ms TTFT + ~50 tok/s |

One agent step ≈ **500–2000 in + 100–300 out** tokens. A multi-step agent multiplies that — budget per call, cap the steps.

---

# 10.4 · Specifying a task = the prompt

The prompt is the spec. Three parts carry 80% of the result:

1. **Role** — who the model is ("assistant for a product catalog")
2. **Constraints** — what it must / must not do ("prefer one accurate tool call")
3. **Output shape** — JSON? prose? a single label?

```python
SYSTEM_PROMPT = (
    "You answer questions about a product catalog using the given tools. "
    "Prefer a single accurate tool call over several speculative ones."
)
```

Skip the "you are a world-class expert" theatre — it buys nothing.

---

# 10.5 · Structured output = the extraction task, rigorously

The "extract" task, done so the answer is **machine-readable, not English you re-parse.** Declare the shape as Pydantic (Day 2 returns), ask for JSON mode:

```python
class CatalogQuery(BaseModel):
    category: str | None = Field(None, description="Restrict to this category.")
    max_price: float | None = Field(None, ge=0)
    in_stock_only: bool = False
```

```python
resp = client.chat.completions.create(model="gpt-4o-mini", messages=[...],
    response_format={"type": "json_object"})   # JSON mode
```

`Field(description=...)` is the spec the model reads. **Make the LLM speak your schema.**

---

# 10.6 · Always validate the output

The LLM *promised* JSON in your shape — don't take its word. Parse through Pydantic, exactly like a request body Day 2:

```python
raw = resp.choices[0].message.content
query = CatalogQuery.model_validate_json(raw)   # raises on bad shape
```

Same **boundary discipline** as Day 2: the LLM is just another **untrusted source**. Validate at the edge; the rest of your code gets a clean, typed object.

<div class="code-along">▶ Code-along now → notebook: module-10 cells 2→6 — start at cell 2 (classify ticket priority), then extract a TicketQuery in JSON mode + validate it</div>

---

# 10.7 · The improvement ladder

Output not good enough? Climb — **only as far as the task needs:**

| Rung | Fix it by… | Reach for it when… |
|---|---|---|
| **Prompt** | clearer role / constraints / examples-in-prompt | first thing, always |
| **Few-shot** | 2–5 examples in the prompt | format keeps drifting |
| **RAG** | retrieve facts, inject as context | model lacks *your* knowledge |
| **Fine-tune** | retrain weights on labeled data | one narrow task, high volume |

Most tasks never leave rung 1. Don't fine-tune what a better prompt fixes.

---

# 10.8 · Fine-tuning — what & when

Adjust the model's **weights** on labeled examples → **better / cheaper / more consistent** at **one narrow task**.

| Worth it | Not worth it |
|---|---|
| high-volume, repetitive task | low volume (prompt is fine) |
| fixed, narrow output format | task still changing |
| cut latency / cost at scale | injecting **knowledge** → use **RAG** |

It teaches a **skill / format**, not facts. A task that's still moving is a moving target — don't tune it yet.

---

# 10.9 · Fine-tuning workflow (shown, not run)

```python
# 1. data: JSONL of examples — NL query → CatalogQuery, the same pairs Lab 10 produces
# {"messages": [{"role":"user","content":"electronics under 5000"},
#               {"role":"assistant","content":"{\"category\":\"Electronics\",...}"}]}

job = client.fine_tuning.jobs.create(
    training_file=file_id, model="gpt-4o-mini")   # 2. train
```

3. **Eval the tuned model vs the base model on a held-out set** — keep it only if it wins.
4. Deploy by **swapping the model id string** — one line.

Data lives **outside** the code (Day 2 / M6 CSV). And that held-out eval **is exactly the golden-eval you build in M12.**

---

# 10.10 · Responsible AI — the minimum

- **PII** — don't send personal data to a third-party LLM without consent + a DPA
- **Hallucination** — the model can invent numbers; **verify with a tool before acting**
- **Cost / runaway** — cap `max_steps` on every agent (M11), so a confused loop fails loudly

Not a course on responsible AI — but your boss *will* ask these three.

---

<!-- _class: lab -->

# 🧪 Lab 10 — NL Query → Catalog Filter

**80 min** · open `labs/lab-10-nl-query-filter/README.md`

You'll build (on your `Product` catalog):
- `CatalogQuery` — Pydantic schema with `Field(description=...)`
- `parse_nl_query(prompt)` — one LLM call, JSON mode, Pydantic validation
- `apply_query(query, api)` — pure-Python filter over the `APIClient`

End state: typing **"electronics under 5000 in stock"** returns the right rows.
**Stretch:** generate a fine-tuning JSONL from the catalog + a held-out eval harness.

---

<!-- _class: title -->

# Module 11
## Tools as Python Functions + the Agent Loop
**~40 min · then 80 min lab** — a "tool" is a function the LLM may call; plan → act → observe

---

# 11.1 · The big idea

> In GenAI, a **"tool"** is just a Python function the LLM is allowed to call.

No magic. No framework required. You hand the LLM:
- A list of function **signatures** (as JSON schemas)
- The user's question

The LLM returns: *"Call `search_products` with `{"term": "keyboard"}`."*
Your code: looks it up, calls it, sends the result back, lets the LLM decide what's next.

---

# 11.2 · A tool is the M5 decorator, reimagined

```python
@registry.tool(
    name="search_products",
    description="Find products whose name contains the given substring.",
    parameters={"type": "object",
                "properties": {"term": {"type": "string"}},
                "required": ["term"]})
def search_products(term: str) -> list[dict]:
    return [p.model_dump() for p in self.api.list_products()
            if term.lower() in p.name.lower()]
```

The decorator stamps metadata on the function and registers it — **the Day-1 / Day-2 M5 decorators return**, now describing tools to an LLM.

---

# 11.3 · Tool schema — what the LLM sees

```json
{ "type": "function",
  "function": {
    "name": "search_products",
    "description": "Find products whose name contains the given substring.",
    "parameters": {
      "type": "object",
      "properties": {"term": {"type": "string"}},
      "required": ["term"] } } }
```

The few words of `description=` are the **most important text in your codebase** for an agent — the LLM picks tools by reading them. Write them like API docs.

---

# 11.4 · The agent loop

```text
┌────────────────────────────────────┐
│   user prompt                       │
│   ┌──────────────────────────┐      │
│   │  LLM(messages, tools)    │      │
│   └────────────┬─────────────┘      │
│        tool_calls?                  │
│       /         \                   │
│   yes /           \ no              │
│      ▼             ▼                │
│  run tools     return answer        │
│      │                              │
│  append obs ─── loop (max_steps) ┐  │
└──────────────────────────────────┘  │
```

Plan (LLM) → act (your code runs the tool) → observe (feed the result back) → repeat.

---

# 11.5 · Chaining the tool result back (`tool_call_id`)

**The #1 lab-breakage point.** When the LLM asks for a tool, you append **two kinds** of message before the next call:

```python
messages.append(msg)                       # 1. the assistant msg carrying .tool_calls
for call in msg.tool_calls:                 # 2. one tool msg PER call
    messages.append({"role": "tool",
                     "tool_call_id": call.id,        # must match the call's id
                     "content": json.dumps(result)})
```

Each `tool` message **must** carry the matching `tool_call_id`. Miss it, or skip the assistant message, and the next API call 400s.

---

# 11.6 · The agent loop, in code

```python
def ask(self, user_prompt: str) -> AgentResult:
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt}]
    for step in range(1, self.max_steps + 1):
        resp = self.llm.chat.completions.create(
            model=self.model, messages=messages,
            tools=self.registry.openai_schemas())
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return AgentResult(answer=msg.content, steps=step)
        messages.append(msg)
        for call in msg.tool_calls:
            result = self._invoke_tool(call.function.name, call.function.arguments)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    raise AgentError("did not converge")
```

About 30 lines. That's the whole "agent".

---

# 11.7 · Always cap `max_steps`

```python
def ask(self, prompt):
    for step in range(1, self.max_steps + 1):   # default 5
        ...
    raise AgentError(f"did not converge in {self.max_steps} steps")
```

Without a cap, a confused model loops forever, burning tokens. With a cap, you **fail loudly**. M12's tests will *assert* this raises — that's how you prove the safety net holds.

<div class="code-along">▶ Code-along now → notebook: module-11 cell 8 — register a tool, run ask() through one plan→act→observe step, watch the tool messages chain</div>

---

# 11.8 · Memory & context, briefly

- It's **more Python around the LLM** — a session-keyed DB, a RAG retriever — **not more LLM magic.**

We're not building memory today; the pattern is identical to everything else: your code holds the state, the LLM just reads and writes strings.

---

<!-- _class: lab -->

# 🧪 Lab 11 — Build the `CatalogAgent`

**80 min** · open `labs/lab-11-catalog-agent.md`

You'll build:
- `ToolSpec` + `ToolRegistry` + `@registry.tool(...)` decorator
- `CatalogAgent.ask()` running plan → act → observe, with `tool_call_id` chaining
- Four tools wrapping the Day-2 `APIClient`; `max_steps` cap + `AgentError`
- A demo: *"what's our most expensive product?"* → tool call → answer

---

<!-- _class: title -->

# Module 12 ⭐
## Testing & Validating AI Tools and Outputs
**~40 min · then 80 min lab** — the spine module: Day-3 patterns applied to AI

---

# 12.1 · Why AI needs a different testing strategy

```text
traditional:  same input → same output → assertEqual()
AI:           same input → distribution of outputs → ?
```

You can't `assertEqual` on prose. You **can** assert on:
- **Shape** — validates against the Pydantic schema
- **Behaviour** — which tools got called, in what order
- **Substrings** — the answer mentions the key fact
- **Bounds** — ≤ N tool calls, ≤ M steps

Stop testing prose. Start testing shape and behaviour.

---

# 12.2 · Four classes of tests for an AI system

```text
1. Tool tests     ─ each tool is plain Python
2. Schema tests   ─ LLM JSON validates against Pydantic
3. Loop tests     ─ mock the LLM, verify the orchestration
4. Golden evals   ─ a file of cases that lock behaviour
```

**Three of the four need no API key** — CI never pays OpenAI. Only the optional live eval does.

---

# 12.3 · Tool tests — deterministic Python

```python
class TestTools:
    def test_search_is_case_insensitive(self):
        agent = _make_agent()
        out = agent.registry.get("search_products").fn(term="KEYBOARD")
        assert out[0]["id"] == 2
```

The tools are **not magic** — they're the functions you tested all Day 3. Same Arrange → Act → Assert. No LLM involved.

---

# 12.4 · Schema tests — Pydantic validation

```python
def test_rejects_negative_price(self):
    with pytest.raises(ValidationError):
        CatalogQuery(max_price=-5.0)

def test_apply_query_filters(self):
    api = _fake_api(SAMPLE_PRODUCTS)
    q = CatalogQuery(category="Electronics", max_price=1000.0)
    assert {p["id"] for p in apply_query(q, api)} == {1}
```

Pure Pydantic + pure Python — the constraints from M10. The LLM is not in the loop.

---

# 12.5 · Loop tests — mock the LLM (Day-3 déjà vu)

```python
def test_single_tool_call_then_answer(self):
    agent = _make_agent()
    agent.llm.chat.completions.create.side_effect = [
        _llm_response(_llm_message(tool_calls=[_tool_call("c1", "count_by_category")])),
        _llm_response(_llm_message(content="We have 3 Electronics.")),
    ]
    r = agent.ask("how many electronics?")
    assert [c.tool for c in r.tool_calls] == ["count_by_category"]
```

`side_effect=[...]` scripts the LLM's replies — **the same mock pattern as Day 3's `requests` retry test.** No network, no key, deterministic.

---

# 12.6 · Loop tests — runaway protection

```python
def test_max_steps_hit_raises(self):
    agent = _make_agent()
    agent.llm.chat.completions.create.return_value = _llm_response(
        _llm_message(tool_calls=[_tool_call("c1", "count_by_category")]))
    with pytest.raises(AgentError, match="did not converge"):
        agent.ask("loop forever")
```

The `max_steps` net you wrote in Lab 11 now has a test. A future refactor that drops the cap → CI goes red.

---

# 12.7 · Golden evals — a file of cases

```json
[
  { "id": "eval-01",
    "prompt": "How many products are in Electronics?",
    "expected_tool_calls": ["count_by_category"],
    "expected_answer_contains": ["Electronics"] },
  { "id": "eval-02",
    "prompt": "What's the most expensive product?",
    "expected_tool_calls": ["list_products"],
    "expected_answer_contains": ["Mechanical Keyboard"] }
]
```

Cases live **outside** the code (Day 2 / M6). Add a row every time a real bug ships — the file becomes your **regression suite for behaviour**. This is M10's held-out eval, made permanent.

---

# 12.8 · Parametrize over the golden file

```python
@pytest.mark.eval
class TestGoldenQueries:
    @pytest.mark.parametrize("case", _golden_cases(),
                             ids=[c["id"] for c in _golden_cases()])
    def test_case(self, case):
        agent = _make_agent()
        agent.llm.chat.completions.create.side_effect = _scripted(case)
        result = agent.ask(case["prompt"])
        assert [c.tool for c in result.tool_calls] == case["expected_tool_calls"]
        for needle in case["expected_answer_contains"]:
            assert needle in result.answer
```

`@pytest.mark.eval` (a Day-3 custom marker) lets you run *just* these: `pytest -m eval`.

<div class="code-along">▶ Code-along now → notebook: module-12 cell 10 — mock the LLM with side_effect, assert the tool sequence, then parametrize the golden file</div>

---

# 12.9 · Same CI, one green check

```yaml
# .github/workflows/tests.yml — already in place from Day 3
- run: pytest --cov --html=report.html
```

**No new workflow.** Agent tests live under `tests/` alongside model + client tests, so the **same Day-3 CI matrix** runs them all.

```text
✓ test (3.10)   ✓ test (3.11)   ✓ test (3.12)   53 tests incl. agent
```

One green check covers the whole stack — Python, API, and AI.

---

<!-- _class: lab -->

# 🧪 Lab 12 — Test the Agent ⭐

**80 min** · open `labs/lab-12-test-the-agent.md`

You'll write:
1. Tool tests (deterministic Python)
2. Schema tests (Pydantic validation)
3. Loop tests with a mocked LLM (`side_effect`)
4. Golden evals from `tests/evals/golden_queries.json` (`@pytest.mark.eval`)

End state: `pytest -q` green, **no `OPENAI_API_KEY` needed**, ~53 tests. Your repo matches `project/solution/`.

---

<!-- _class: title -->

# End of Day 4 ✅

**Your `my-catalog/` project:**

- Python catalog + decorators + type hints (Day 1)
- FastAPI + Pydantic + `APIClient` + bulk-import (Days 1–2)
- pytest + mocks + parametrize + HTML reports + CI (Day 3)
- LLM-powered `CatalogAgent` with **its own test suite** (Day 4)

**One project. Four days. Tested. Agentic. Done.**

---

<!-- _class: title -->

# Where to next

- Swap OpenAI for Anthropic / Azure / a local model — the injection seam means **one file changes**
- Climb the M10 ladder for real: few-shot → RAG when the catalog outgrows the context window
- Add memory: persist `messages` per `session_id`
- Fine-tune `parse_nl_query` once volume justifies it — you already have the eval
- Take the patterns home: every one works on your real production code
