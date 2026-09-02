SERVER_SETTINGS_DIR:=/root/.vscode-server/data/Machine
REMOTE_SETTINGS_DIR:=/root/.vscode-remote/data/Machine

export

post-create:
	mkdir -p $$SERVER_SETTINGS_DIR
	echo {\"python.venvPath\": \"~/.cache/pypoetry/virtualenvs\"} > $$SERVER_SETTINGS_DIR/settings.json
	mkdir -p $$REMOTE_SETTINGS_DIR
	cp $$SERVER_SETTINGS_DIR/settings.json $$REMOTE_SETTINGS_DIR/settings.json
	poetry install
	poetry run pre-commit install --install-hooks
