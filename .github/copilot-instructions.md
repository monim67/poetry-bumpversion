# Project Guidelines

## What This Project Is

`poetry-bumpversion` is a Poetry application plugin that extends the `poetry version` command to update version strings in arbitrary project files (e.g. `__init__.py`, `README.md`) whenever `poetry version <bump>` is run. It is published to PyPI and used via `poetry self add poetry-bumpversion`.

- Entry point: `poetry_bumpversion.plugin:BumpVersionPlugin` (registered as `poetry.application.plugin`)
- Source layout: `src/poetry_bumpversion/` (packaged with `poetry-core`)
- Python: `>=3.10,<4`; Poetry: `>=1.2.0` (requires Poetry `>=2.0` to build)
- Configuration in consumer projects is done via `[tool.poetry_bumpversion.file."..."]` or `[[tool.poetry_bumpversion.replacements]]` sections in their `pyproject.toml`

## Architecture

| Module | Role |
|--------|------|
| `plugin.py` | Poetry plugin lifecycle — hooks into `TERMINATE` event, calls `handle_version_update()` |
| `models.py` | Pydantic models for parsing `[tool.poetry_bumpversion.*]` config from `pyproject.toml` |

Pydantic v1 API is used via `pydantic.v1` with a fallback import for older pydantic installs.

## Build and Test

```bash
# Install all dependencies (build group contains test/lint tools)
poetry install

# Run tests with coverage
poe test-cov

# Run tests only (no coverage)
pytest

# Run tests across multiple Python versions
tox
```

Tests are integration-style: they copy `tests/assets/sample-project/` to a `tmp_path`, optionally swap in a fixture `pyproject.toml` from `tests/assets/pyproject-files/`, then invoke `poetry version` as a subprocess with coverage tracking.

## Conventions

- **Docstring style**: Google convention (`pydocstyle` with `D401,D404` added). All public functions/classes need docstrings.
- **Type annotations**: Strict mypy (`strict = true`). All code must be fully typed.
- **Formatting**: `black` (targets py310–py314) + `isort` (profile = black). Files are auto-formatted on save — agents do not need to run the linter manually.
- **Test fixtures**: To add a new test scenario, add a `.toml` file to `tests/assets/pyproject-files/` and reference it in `tests/test_main.py`.
- **Version placeholder**: The package's own `__version__` is `"0.0.0"` — it is updated at release time by this plugin itself via `[tool.poetry_bumpversion.file."src/poetry_bumpversion/__init__.py"]` in `pyproject.toml`.
- **i18n**: Output strings passed to `command.line()`/`command.info()` are wrapped in `_()` (cleo's translation shim).

## Updating Package Requirements

Use the **update-package-requirements** skill (`/update-package-requirements`). Covers both Python version support changes and production dependency updates.
