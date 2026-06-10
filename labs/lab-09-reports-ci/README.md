# Lab 9 — Reports + GitHub Actions

**Duration:** ~45 min · **Day:** 3 · **Module:** 3 (Reporting + CI/CD)

## Goal
Make the suite *visible* and *automatic*: add coverage, generate an HTML
report, and wire a CI workflow that runs across Python 3.10/3.11/3.12. By the
end, the suite runs in CI and goes green — you'll see it on the shared repo.

## You start with
- Lab 8 end-state — 31 mocked tests green locally, plus the provided integration class (33 with `pytest`).

## Starter files
```bash
cp -r ../labs/lab-09-reports-ci/starter/.github .          # into my-catalog/
cat ../labs/lab-09-reports-ci/starter/pyproject-additions.toml   # blocks to paste into pyproject.toml
```
| File | What |
|---|---|
| `pyproject-additions.toml` | two config blocks to fill + paste into your `pyproject.toml` |
| `.github/workflows/tests.yml` | a CI workflow skeleton — fill every `# TODO` |

## You'll end with
- `pytest --cov --html=report.html` producing a self-contained HTML report
- `.github/workflows/tests.yml` complete (matrix · coverage · artifact upload)
- the shared repo's Actions tab green across 3.10/3.11/3.12 (pushing your own = stretch)

## What to implement (read the TODOs)
- **`pyproject.toml`** — register the `integration` marker (so `--strict-markers` accepts it); point coverage at `source = ["catalog"]` with `branch = true`.
- **`tests.yml`** — triggers (`push` to main · `pull_request` · `workflow_dispatch`); the `python-version` matrix; the install step (`pip install -e ".[dev]"`); the pytest-with-coverage command; the list of artifacts to upload.

## Steps
1. Paste the two blocks from `pyproject-additions.toml` into your `pyproject.toml` and fill their TODOs.
2. Generate the report locally and open it:
   ```bash
   pytest --cov --cov-report=term-missing --html=report.html --self-contained-html
   open report.html        # xdg-open on Linux · start on Windows
   ```
   Read the `Missing` column — that's the lines no test reached.
3. Fill the `# TODO`s in `.github/workflows/tests.yml`.
4. **Code-along:** your instructor pushes the shared repo and you watch the matrix go green in the Actions tab (no per-person GitHub auth). Want your own badge? See **Stretch**.

## Expected output
```
$ pytest --cov --cov-report=term-missing --html=report.html --self-contained-html
=================================== coverage ===================================
Name                    Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
catalog/client.py          ..     ..     ..     ..    ~85%   ...
catalog/models.py          ..      0     ..      0    100%
...
33 passed in 1.0s
```
GitHub Actions: `✓ test (3.10) · ✓ test (3.11) · ✓ test (3.12)` — report + coverage uploaded as artifacts.

## Common pitfalls
- No `--strict-markers` — a typo'd marker (`@pytest.mark.integraton`) silently runs nothing.
- `fail-fast: true` (the default) cancels 3.11/3.12 the moment 3.10 fails — you lose the signal. Set it `false`.
- Uploading the report only on success — the failing run is when you need it most. Use `if: always()`.
- Committing `catalog.json` / `import_report.json` — your `.gitignore` should cover them.

## Stretch (optional)
- **Push to your own GitHub account** and get a real green badge on your `README.md`.
- Add a **coverage gate**: `pytest --cov --cov-fail-under=80` fails CI if coverage drops.
- Add a `lint` job running `ruff check` and `mypy catalog/`.
