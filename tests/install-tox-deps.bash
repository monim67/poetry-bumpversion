#!/bin/bash

set -e

install() {
    poetry install --no-root --only build
    pip install -c tests/pip-constraints.txt -e .
}

install_if_deps_updated() {
    HASH_FILE="$VIRTUAL_ENV/deps.hash"
    CURRENT_HASH=$(md5sum poetry.lock tests/pip-constraints.txt tests/install-tox-deps.bash | md5sum | cut -d' ' -f1)
    if [[ ! -f "$HASH_FILE" ]] || [[ "$CURRENT_HASH" != "$(cat "$HASH_FILE")" ]]; then
        install
        echo "$CURRENT_HASH" > "$HASH_FILE"
    else
        echo "Dependencies are up to date. Skipping installation."
    fi
}

validate_poetry_honoring_virtualenvs() {
    if [[ "$(poetry env info -p)" != "$VIRTUAL_ENV" ]]; then
        echo "Error: Poetry is not honoring VIRTUAL_ENV=$VIRTUAL_ENV"
        echo "To fix this remove pinned python from $(poetry config virtualenvs.path)/envs.toml"
        exit 1
    fi
}

validate_which_poetry_resolves_to_tox_env() {
    EXPECTED_POETRY_PATH="$TOX_ENV_DIR/bin/poetry"
    if [[ "$(which poetry)" != "$EXPECTED_POETRY_PATH" ]]; then
        echo "Error: 'which poetry' does not resolve to $EXPECTED_POETRY_PATH"
        exit 1
    fi
}

validate_poetry_honoring_virtualenvs
validate_which_poetry_resolves_to_tox_env
install_if_deps_updated
