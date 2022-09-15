FROM python:3.8

ARG DEPLOYMENT_ENV

ENV DEPLOYMENT_ENV=${DEPLOYMENT_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.0

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /opt/working
COPY pyproject.toml /opt/working/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && /bin/bash -c "if [[ ${DEPLOYMENT_ENV} = prod ]] ; then poetry install --no-dev --no-interaction --no-ansi --no-root ; else poetry install --no-interaction --no-ansi --no-root ; fi"