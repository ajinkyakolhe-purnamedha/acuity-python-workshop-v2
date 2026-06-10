# Lab 9 — Coverage + CI

**~45 min · Day 3 · reporting + CI/CD**

## Goal
Make the suite **visible** and **automatic**: add coverage, generate an HTML report, and write a GitHub Actions workflow that runs the tests across Python 3.10/3.11/3.12.

## Start with
Lab 8 end-state — 31 tests green locally.

## Get the starter files
```bash
cp -r ../labs/lab-09-reports-ci/starter/.github .                 # into my-catalog/
cat ../labs/lab-09-reports-ci/starter/pyproject-additions.toml    # blocks to paste
```
| File | What |
|---|---|
| `pyproject-additions.toml` | coverage config to fill + paste into `pyproject.toml` |
| `.github/workflows/tests.yml` | CI workflow skeleton — fill every `# TODO` |

## What to implement
- **pyproject.toml** — point coverage at `source = ["catalog"]`, `branch = true`.
- **tests.yml** — triggers (`push` · `pull_request` · `workflow_dispatch`); the `python-version` matrix; install (`pip install -e ".[dev]"`); the pytest+coverage command; upload the HTML report as an artifact.

## Steps
1. Copy `.github/` into `my-catalog/` and paste the `pyproject-additions.toml` blocks into your `pyproject.toml`; fill their TODOs.
2. Generate the report locally and open it:
   ```bash
   pytest --cov --cov-report=term-missing --html=report.html --self-contained-html
   open report.html        # xdg-open on Linux · start on Windows
   ```
   Read the `Missing` column — those are the lines no test reached.
3. Fill every `# TODO` in `.github/workflows/tests.yml`.

## Watch out
- `fail-fast: false` — otherwise one failing Python version cancels the others, and you lose the signal.
- Upload the report with `if: always()` — the failing run is when you need it most.

## Stretch
Push to your own GitHub for a green badge; add `--cov-fail-under=80` to gate CI.
