FROM python:3.14

COPY --from=ghcr.io/astral-sh/uv:0.12.8 /uv /uvx /usr/local/bin/
RUN uv python install 3.12 3.11 3.10

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 -
