FROM python:3.11.5-alpine3.18

WORKDIR /app

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.2 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_HOME=/app/.local \
    POETRY_CACHE_DIR=/app/.cache \
    PYSETUP_PATH=/app \
    VENV_PATH=/app/.venv \
    PATH=/app/.local/bin:/usr/bin:/app/.venv:/bin:$PATH

RUN apk add gcc make musl-dev curl --no-cache && \
    chown -R nobody:nobody /app

USER nobody

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python -

COPY --chown=nobody:nobody poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY --chown=nobody:nobody . .

ENTRYPOINT ["poetry", "run", "start"]
