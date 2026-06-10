# Code-along beat — Push to CI, watch it go green (M9, §2–3)

**Instructor live-demo · ~10 min · on ONE shared repo** (not 20 people doing `gh auth` at once — that desyncs the room). Students **watch**; their own push is a lab Stretch. Pre-reqs below; rehearse once before class.

## Pre-flight (do before the room, or have ready)
- A throwaway GitHub account/org for the demo, `gh` already authed (`gh auth status`).
- The project at Lab-9 end-state: suite green locally + `.github/workflows/tests.yml` + `pyproject.toml` cov config already written (that was the lab).
- `.gitignore` covers `catalog.json`, `import_report.json`, `report.html`, `.coverage`.

## Frame (say this first)
"Your suite is green — **on your laptop**. The moment a teammate pushes a change and forgets to run it, that green is worthless. CI runs the suite **for you, on every push**. Watch."

## Do it — type live
```bash
git init && git add . && git commit -m "Day 3 — tests + CI"
gh repo create acuity-catalog-demo --private --source=. --push
```
Then open the repo's **Actions** tab in the browser (`gh repo view --web`).

## Narrate the run (this is the payoff — point at the screen)
- The workflow starts on the push, **3 jobs** fan out: `test (3.10)`, `(3.11)`, `(3.12)` — the **matrix**, in parallel.
- Each: checkout → setup-python → `pip install -e ".[dev]"` → `pytest --cov …`.
- Predict-before-reveal: *"All three green? Any version-specific break?"* → watch the ✓s land.
- Click a job → the **Coverage** line in the run summary (the `$GITHUB_STEP_SUMMARY` block).
- Show **Artifacts** → `pytest-report-3.10/report.html` downloads and opens — the browsable report, now produced by a machine, not you.

## Optional — make the gate real (productive failure, ~2 min)
Break one line, push, watch CI go **red**, then fix and watch it recover:
```bash
# comment out a `raise CatalogError(...)` in catalog/models.py
git commit -am "break a guard" && git push        # → ✗ on the PR/commit
git revert --no-edit HEAD && git push              # → ✓ back to green
```
"That red ✗ is the point — wire 'require this check to pass before merge' and **red can't reach `main`**. Your suite stopped being tests that *exist* and became a **gate**."

## Land it
"Local = you trust your machine. CI = the team trusts the `main` branch. Same `pytest` command — now it runs where it counts, on every change, forever."

> Students who want their own green badge: the lab **Stretch** has them repeat this on their own account + add the `badge.svg` to their README.
