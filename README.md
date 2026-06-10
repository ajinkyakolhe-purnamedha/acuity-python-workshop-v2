# Acuity Workshop — Python, Automation Testing, JSON & Generative AI

Delivery kit for the 4-day workshop. One connected project — a **Product Catalog** — grows day by day from a plain Python class to a tested, CI-gated, LLM-ready service. No throwaway demos.

**Status:** Days 1–3 complete (decks · code-along · labs · project). Day 4 (M10–12, GenAI + agent) lands next.

## The spine — each day feeds the next
**Build it** (D1) → **Automate it** (D2: a typed `APIClient` drives the server) → **Test it** (D3: a suite + CI lock it down) → **AI-enable it** (D4: an agent whose tools *are* the client methods). The dependency-injection seam (`requests.Session` → `llm_client`) is the through-line.

## Layout
| Path | What |
|---|---|
| `deck/day-N.md` | Marp slides, one deck per day (render to PDF) |
| `codealong/module-N.ipynb` | M1–M6: instructor types the **BankAccount** story live, room follows |
| `codealong/module-N/` | M7–M9: file-based test scripts (run `pytest`) + two instructor **live-build** beats |
| `labs/lab-NN-*/` | all 9 labs: a `README.md` guide + a `starter/` scaffold (skeleton + `# TODO`s) students fill |
| `project/start-here/` | Day-1 baseline students copy to `my-catalog/` + the self-check graders (`test_lab01..06`) |
| `project/checkpoints/day-N-start/` | Catch-up baselines — the project at the **start** of Days 2–4 |
| `project/solution/` | Reference solution = Day-4 end state |

**Teaching model:** concepts are taught on **BankAccount** (code-along); labs build **Product** (the firewall). Same patterns, different domain — so a lab never hands over its own answer.

## Quick start
```bash
# Slides (Marp CLI — npm i -g @marp-team/marp-cli)
marp deck/day-1.md --theme-set deck/theme.css --pdf -o day-1.pdf
marp deck/day-1.md --preview                      # live

# Project (run inside any checkpoint or the solution)
cd project/solution
pip install -e ".[dev]"                            # or: uv sync
uvicorn catalog.server:app --reload                # the API
pytest                                             # all
pytest -m "not integration"                        # fast suite (no live server)
pytest --cov --cov-report=term-missing             # coverage, as CI runs it
```

## Day by day
| Day | Theme | Modules | Labs |
|---|---|---|---|
| **1 · Build It** | clean Python → objects → a local API | M1 core · M2 data/files · M3 OOP + dataclass + FastAPI | L1 foundation · L2 persistence · L3 API server |
| **2 · Automate It** | validation → a typed client → bulk import | M4 Pydantic · M5 REST + decorators · M6 CSV import | L4 Pydantic · L5 `APIClient` · L6 bulk import |
| **3 · Test It** | pytest → mocking → coverage + CI | M7 pytest + fixtures · M8 mock + parametrize · M9 coverage + CI | L7 unit tests · L8 mocked client · L9 coverage + CI |
| **4 · AI-enable It** | *(forthcoming)* structured output · tools + agent loop · testing AI | M10–M12 | L10–L12 |

## Self-check graders (Days 1–2)
`project/start-here/tests/test_lab01..06.py` — students **run** these to check a lab: they **skip** until the lab is built, then go red → green, and **retire in sequence** as later labs supersede earlier ones. Day-3 labs ship no grader — instead the `starter/` test stubs **fail with a `# TODO`** (red) until students implement them (`test_models` / `test_catalog` / `test_client`); turning each green, plus CI passing, is the check.

> Verify graders in an isolated dir — an editable install of the solution shadows `catalog.*`, so an in-repo run can report a false "passed" instead of "skipped".
