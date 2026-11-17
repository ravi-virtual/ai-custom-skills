---
name: python-project-setup
description: Creates and maintains modern, production-ready Python projects - src layout, a single pyproject.toml, uv for environments and lockfile, ruff for lint and format, pytest, strict mypy, pre-commit and GitHub Actions CI. Use when the user wants to start a new Python project, app, library, CLI or AI/LLM service, standardise or modernise an existing one (requirements.txt, setup.py, black/flake8/pip migration), add tests, linting, typing or CI, or asks how to structure a Python repository. Scaffolds a verified skeleton with one command.
---

# Python Project Setup

Default stack: **uv** (Python and dependency manager, lockfile), **ruff** (lint and format), **pytest**, **mypy** (strict), **pre-commit**, GitHub Actions. All configuration lives in `pyproject.toml`. Source lives under `src/`.

## Workflow

1. **Clarify** only what changes the output: kind (`app`, `lib`, `cli`), minimum Python version (default 3.12), runtime dependencies, and how it ships (container, PyPI, internal script).
2. **Scaffold** (new project): `python scripts/scaffold_python_project.py my-project --kind app|lib|cli [--python 3.12] [--out DIR]`. It writes `pyproject.toml`, `src/<package>/`, `tests/`, `.gitignore`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `README.md` and `.python-version`, using only the standard library.
3. **Install and verify**: `cd my-project && uv sync && uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run mypy`. A fresh scaffold passes all four. If `uv` is missing, install it from the official uv documentation first.
4. **Add dependencies** with `uv add <pkg>` (runtime) or `uv add --dev <pkg>`; never edit the lockfile by hand. Commit `uv.lock`.
5. **Implement** in `src/<package>/`, with tests next to each feature as you go.
6. **Finish** by running the four checks again and `uv run pre-commit install`. Report what was created and the commands to run.

## Kinds

| Kind | You get | Use for |
|---|---|---|
| `app` | `config.py` (typed settings from env vars), `main.py` with logging, `.env.example` | services, workers, automation, AI/LLM apps |
| `cli` | argparse entry point, `[project.scripts]` console command, `__main__.py` | command-line tools |
| `lib` | `py.typed`, a small typed core module | packages others import |

## Conventions to apply when writing code

- **Layout:** `src/<package>/` for code, `tests/` mirroring it, no logic in `__init__.py` beyond the version and public exports.
- **Typing:** annotate all public functions; keep `mypy --strict` green. When migrating untyped code, start with `strict = false`, enable per-module strictness, and ratchet up.
- **Config:** read environment variables once into a typed settings object; no `os.getenv` scattered through code; never commit `.env`, ship `.env.example`.
- **Logging, not print:** `logging.getLogger(__name__)`; configure handlers only in the entry point.
- **Errors:** raise specific exceptions with actionable messages; catch only what you can handle; never `except:` or silently pass.
- **Paths and time:** `pathlib.Path`; timezone-aware `datetime`.
- **Functions:** small, single purpose, no mutable default arguments, pure where possible so tests need no mocks.
- **Tests:** pytest functions, fixtures over setup code, `tmp_path` and `monkeypatch` for isolation, parametrize edge cases, no network in unit tests.
- **Dependencies:** few, pinned by the lockfile, with lower bounds in `pyproject.toml`; justify each new one.

## AI / LLM projects

- Use the official `anthropic` SDK; the model name comes from configuration (`ANTHROPIC_MODEL`), never a scattered literal.
- Keep prompts in files (`src/<package>/prompts/*.md`) loaded at runtime so they are reviewable and testable.
- Wrap the client behind a small interface so tests inject a fake and never hit the network or spend money.
- Keep an `evals/` folder (cases plus a runner) and run it when prompts or models change. See `ai-workflow-builder` for pipelines and `prompt-writing` for the prompts themselves.
- Load the API key from the environment only; do not log prompts or responses that may contain personal data.

## Migrating an existing project

`requirements.txt` to uv: `uv init` in place (or add a `[project]` table), `uv add -r requirements.txt`, remove the old file. Replace `setup.py`/`setup.cfg` with `pyproject.toml`; replace black/isort/flake8 with ruff (`ruff format`, `ruff check --select E,F,I,B,UP`); change one concern per commit and keep tests green between steps.

## References

`references/tooling-notes.md`: pyproject sections explained, ruff rule sets, mypy adoption path, CI matrix, Docker image, publishing to PyPI, monorepo/workspaces.
