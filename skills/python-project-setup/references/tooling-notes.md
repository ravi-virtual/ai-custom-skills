# Tooling Notes

## Contents
- [pyproject.toml sections](#pyprojecttoml-sections)
- [Ruff](#ruff)
- [mypy adoption path](#mypy-adoption-path)
- [Testing](#testing)
- [CI](#ci)
- [Docker](#docker)
- [Publishing a library](#publishing-a-library)
- [Workspaces / monorepo](#workspaces--monorepo)
- [Common problems](#common-problems)

## pyproject.toml sections

| Section | Purpose |
|---|---|
| `[build-system]` | Backend used to build wheels (hatchling here). Apps that are never published still need it for `uv sync` to install the package |
| `[project]` | Name, version, `requires-python`, runtime `dependencies`, optional `[project.scripts]` console commands |
| `[dependency-groups]` | Dev-only dependencies (PEP 735); `uv sync` installs the `dev` group by default |
| `[tool.hatch.build.targets.wheel]` | Which package folders go into the wheel (`src/<package>`) |
| `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.mypy]` | Tool configuration in one file |

Version bounds: use lower bounds (`requests>=2.32`) in libraries; the lockfile pins exact versions for apps.

## Ruff

The scaffold selects `E, F, I, B, UP, SIM, C4, RUF`. Meaning: pycodestyle errors, pyflakes, import order, bugbear (likely bugs), pyupgrade, simplifications, comprehensions, ruff-specific rules. Add as needed: `S` (security, via bandit rules), `PTH` (use pathlib), `T20` (no `print`), `D` (docstrings), `N` (naming). Silence a rule for one line with `# noqa: RULE`, and prefer per-file ignores in `pyproject.toml` over global disables. `ruff format` replaces black; do not run both.

## mypy adoption path

1. New code: `strict = true` from day one (the scaffold default).
2. Legacy code: set `strict = false`, enable `check_untyped_defs`, then add per-module overrides:
   ```toml
   [[tool.mypy.overrides]]
   module = "legacy_pkg.*"
   ignore_errors = true
   ```
3. Shrink the override list over time; third-party packages without stubs: `ignore_missing_imports` per module, not globally.

## Testing

- Layout: `tests/test_<module>.py`; fixtures in `tests/conftest.py`.
- Unit tests never touch the network, clock or real filesystem outside `tmp_path`; inject fakes at boundaries (HTTP client, LLM client, time).
- Parametrize edge cases (`@pytest.mark.parametrize`); assert on behaviour, not implementation.
- Coverage: `uv run pytest --cov=<package> --cov-report=term-missing`; use it to find untested branches, not as a score to game.
- Async code: add `pytest-asyncio` (`uv add --dev pytest-asyncio`) and mark tests with `@pytest.mark.asyncio`.

## CI

The generated workflow runs: install from the lockfile (`uv sync --frozen`), `ruff check`, `ruff format --check`, `mypy`, `pytest --cov`. To test several Python versions add them to the `matrix.python` list. Pin third-party actions to a current major version (or a commit SHA for stricter supply-chain control) and keep them updated with Dependabot.

## Docker

Pattern for an app image (pin the base and uv image tags in real use):

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "my_app.main"]
```

Dependencies are installed before the source is copied so Docker caches that layer. Run as a non-root user in production and never bake `.env` into the image.

## Publishing a library

`uv build` creates sdist and wheel in `dist/`; `uv publish` uploads (use a PyPI trusted publisher or a scoped token from the environment, never a token in the repo). Bump `version` in `pyproject.toml` and tag the release. Test installation from the built wheel in a clean environment before publishing.

## Workspaces / monorepo

For several related packages, use a uv workspace: a root `pyproject.toml` with `[tool.uv.workspace] members = ["packages/*"]` and each member depending on siblings via `[tool.uv.sources] sibling = { workspace = true }`. One lockfile covers all members.

## Common problems

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError` for your package in tests | Package not installed in the environment | `uv sync` (the project installs itself in editable mode) |
| Imports work locally but not in CI | Relying on the current directory instead of the installed package | Use the src layout and run through `uv run` |
| mypy "missing library stubs" | Dependency ships no types | `uv add --dev types-<pkg>` or a per-module ignore |
| Format check fails in CI only | Contributors skipped `ruff format` | `pre-commit install`; run `ruff format .` and commit |
| Lockfile out of date in CI (`--frozen` fails) | `pyproject.toml` changed without `uv lock` | Run `uv lock` and commit `uv.lock` |
