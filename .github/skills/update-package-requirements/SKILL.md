---
name: update-package-requirements
description: 'Update this project when adding or dropping Python version support, or when updating package dependencies. Use for: bumping supported Python range, adding/removing pyXYZ from build targets, updating prod/dev/build dependencies, fixing lint or test failures after a dependency change.'
---

# Update Package Requirements

## Adding or Dropping a Python Version

- In `pyproject.toml` → `[project] requires-python`: adjust the version range.
- In `pyproject.toml` → `[tool.black] target_version`: add/remove the `pyXYZ` entry.
- If the **minimum** version changed: update `[tool.mypy] python_version` and `[tool.isort] py_version` (compact form, e.g. `"310"` for 3.10). Also update `README.rst` prerequisite line.
- Switch env, regenerate lock, and reinstall:
   ```bash
   poetry env use <new-version>
   poetry lock
   poetry install
   ```
- Verify with `poetry run poe lint` and `poetry run poe test-cov`. If these fail due to outdated dependencies, update them and retry.
- In `pyproject.toml` → `[tool.tox] envlist`: add/remove the `pyXYZ` entry.
- In `.github/workflows/build.yml` → `pre-build` matrix: set to the latest supported version.
- In `.github/workflows/build.yml` → `build` matrix: list all remaining supported versions except the one in `pre-build`.
- In `.devcontainer/Dockerfile`: update the `pyenv install` and `pyenv global` lines — add/remove the version, keep the latest as the global default.
- Do a final sweep to check for any outdated refereces and report to user.


## Updating Production Dependencies

- Edit the version constraint for the package under `[project] dependencies` in `pyproject.toml`.
- Resolve and reinstall:
   ```bash
   poetry update <package-name>
   poetry install
   ```
- Verify with `poetry run poe lint` and `poetry run poe test-cov`.
- Update prerequisites in README.rst if necessary.
- Search the project for any other references to the old version and report to user.
