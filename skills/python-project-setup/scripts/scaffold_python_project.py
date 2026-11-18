#!/usr/bin/env python3
"""scaffold_python_project.py - create a modern Python project (uv + ruff + pytest + mypy, src layout).

Usage:
  python scaffold_python_project.py my-project [--kind app|lib|cli] [--python 3.12]
                                    [--out DIR] [--description TEXT] [--force]

Kinds:
  lib  importable package, typed (py.typed), no entry point
  cli  package with a `my-project` console script (argparse, no extra dependencies)
  app  package with typed settings from environment variables and logging setup

Standard library only. Afterwards:  cd my-project && uv sync && uv run pytest
"""
import argparse
import os
import re
import sys
import textwrap

RUFF_TARGET = {"3.9": "py39", "3.10": "py310", "3.11": "py311", "3.12": "py312", "3.13": "py313", "3.14": "py314"}


def slug(name):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    if not s or s[0].isdigit():
        raise SystemExit(f"Error: '{name}' is not a usable project name (must start with a letter).")
    return s


def files(project, package, kind, py, description):
    dedent = lambda t: textwrap.dedent(t).lstrip("\n")  # noqa: E731
    scripts = f'\n[project.scripts]\n{project} = "{package}.cli:main"\n' if kind == "cli" else ""
    pyproject = dedent(f'''
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [project]
        name = "{project}"
        version = "0.1.0"
        description = "{description}"
        readme = "README.md"
        requires-python = ">={py}"
        dependencies = []
        {scripts}
        [dependency-groups]
        dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.6", "mypy>=1.11", "pre-commit>=3.8"]

        [tool.hatch.build.targets.wheel]
        packages = ["src/{package}"]

        [tool.ruff]
        line-length = 100
        target-version = "{RUFF_TARGET.get(py, 'py312')}"
        src = ["src", "tests"]

        [tool.ruff.lint]
        # E/F pycodestyle+pyflakes, I isort, B bugbear, UP pyupgrade, SIM simplify, C4 comprehensions, RUF ruff-specific
        select = ["E", "F", "I", "B", "UP", "SIM", "C4", "RUF"]

        [tool.ruff.lint.per-file-ignores]
        "tests/**" = ["B011"]

        [tool.pytest.ini_options]
        testpaths = ["tests"]
        addopts = "-ra --strict-markers --strict-config"

        [tool.mypy]
        python_version = "{py}"
        strict = true
        files = ["src"]
    ''')
    out = {
        "pyproject.toml": pyproject,
        ".python-version": py + "\n",
        ".gitignore": dedent('''
            __pycache__/
            *.py[cod]
            .venv/
            .env
            .pytest_cache/
            .mypy_cache/
            .ruff_cache/
            .coverage
            htmlcov/
            dist/
            build/
            *.egg-info/
        '''),
        "README.md": dedent(f'''
            # {project}

            {description}

            ## Develop

            ```bash
            uv sync                      # create .venv and install runtime + dev dependencies
            uv run pytest                # tests
            uv run ruff check . && uv run ruff format --check .   # lint and format check
            uv run mypy                  # type check
            uv run pre-commit install    # run the checks before every commit
            ```

            Add a dependency: `uv add <package>` (dev only: `uv add --dev <package>`). Commit `uv.lock`.
        '''),
        ".pre-commit-config.yaml": dedent('''
            repos:
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: v0.6.9          # run `pre-commit autoupdate` to move to the latest tag
                hooks:
                  - id: ruff
                    args: [--fix]
                  - id: ruff-format
              - repo: https://github.com/pre-commit/pre-commit-hooks
                rev: v5.0.0
                hooks:
                  - id: end-of-file-fixer
                  - id: trailing-whitespace
                  - id: check-yaml
                  - id: check-added-large-files
        '''),
        ".github/workflows/ci.yml": dedent(f'''
            name: CI
            on:
              push:
                branches: [main]
              pull_request:
            jobs:
              test:
                runs-on: ubuntu-latest
                strategy:
                  matrix:
                    python: ["{py}"]
                steps:
                  - uses: actions/checkout@v4
                  - uses: astral-sh/setup-uv@v5      # pin to the current major version
                  - run: uv sync --frozen --python ${{{{ matrix.python }}}}
                  - run: uv run ruff check .
                  - run: uv run ruff format --check .
                  - run: uv run mypy
                  - run: uv run pytest --cov={package} --cov-report=term-missing
        '''),
        f"src/{package}/__init__.py": dedent(f'''
            """{description}"""

            __version__ = "0.1.0"
        '''),
        "tests/__init__.py": "",
    }
    if kind == "lib":
        out[f"src/{package}/py.typed"] = ""
        out[f"src/{package}/core.py"] = dedent('''
            """Core functionality. Replace with your public API."""


            def greet(name: str) -> str:
                """Return a greeting for `name`."""
                if not name.strip():
                    raise ValueError("name must not be empty")
                return f"Hello, {name.strip()}!"
        ''')
        out["tests/test_core.py"] = dedent(f'''
            import pytest

            from {package}.core import greet


            def test_greet() -> None:
                assert greet(" Ada ") == "Hello, Ada!"


            def test_greet_rejects_blank() -> None:
                with pytest.raises(ValueError):
                    greet("  ")
        ''')
    elif kind == "cli":
        out[f"src/{package}/cli.py"] = dedent(f'''
            """Command-line entry point: `{project} --help`."""

            import argparse
            import sys
            from collections.abc import Sequence

            from {package} import __version__


            def build_parser() -> argparse.ArgumentParser:
                parser = argparse.ArgumentParser(prog="{project}", description="{description}")
                parser.add_argument("name", help="who to greet")
                parser.add_argument("--version", action="version", version=__version__)
                return parser


            def main(argv: Sequence[str] | None = None) -> int:
                args = build_parser().parse_args(argv)
                print(f"Hello, {{args.name}}!")
                return 0


            if __name__ == "__main__":
                sys.exit(main())
        ''')
        out[f"src/{package}/__main__.py"] = f"from {package}.cli import main\n\nraise SystemExit(main())\n"
        out["tests/test_cli.py"] = dedent(f'''
            import pytest

            from {package}.cli import main


            def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
                assert main(["Ada"]) == 0
                assert capsys.readouterr().out.strip() == "Hello, Ada!"
        ''')
    else:  # app
        out[f"src/{package}/config.py"] = dedent('''
            """Typed settings read once from environment variables."""

            import os
            from dataclasses import dataclass


            @dataclass(frozen=True)
            class Settings:
                env: str = "development"
                log_level: str = "INFO"

                @classmethod
                def from_env(cls) -> "Settings":
                    return cls(
                        env=os.getenv("APP_ENV", "development"),
                        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
                    )
        ''')
        out[f"src/{package}/main.py"] = dedent(f'''
            """Application entry point: `uv run python -m {package}.main`."""

            import logging

            from {package}.config import Settings

            log = logging.getLogger(__name__)


            def run(settings: Settings) -> None:
                log.info("starting in %s mode", settings.env)


            def main() -> None:
                settings = Settings.from_env()
                logging.basicConfig(
                    level=settings.log_level,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                )
                run(settings)


            if __name__ == "__main__":
                main()
        ''')
        out[".env.example"] = "APP_ENV=development\nLOG_LEVEL=INFO\n"
        out["tests/test_config.py"] = dedent(f'''
            import pytest

            from {package}.config import Settings


            def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
                monkeypatch.delenv("APP_ENV", raising=False)
                assert Settings.from_env().env == "development"


            def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
                monkeypatch.setenv("LOG_LEVEL", "debug")
                assert Settings.from_env().log_level == "DEBUG"
        ''')
    return out


def main():
    ap = argparse.ArgumentParser(description="Scaffold a modern Python project.")
    ap.add_argument("name", help="project name, e.g. my-project")
    ap.add_argument("--kind", choices=["app", "lib", "cli"], default="app")
    ap.add_argument("--python", default="3.12", help="minimum Python version (default 3.12)")
    ap.add_argument("--out", help="output directory (default ./<name>)")
    ap.add_argument("--description", default="A Python project.")
    ap.add_argument("--force", action="store_true", help="write into a non-empty directory")
    args = ap.parse_args()

    project = slug(args.name)
    package = project.replace("-", "_")
    out_dir = args.out or project
    if os.path.isdir(out_dir) and os.listdir(out_dir) and not args.force:
        print(f"Error: {out_dir} is not empty (use --force).", file=sys.stderr)
        return 1
    desc = args.description.replace('"', "'")
    for rel, content in files(project, package, args.kind, args.python, desc).items():
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    print(f"Created {args.kind} project '{project}' (package '{package}') in {out_dir}")
    print(f"Next: cd {out_dir} && uv sync && uv run pytest && uv run ruff check . && uv run mypy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
