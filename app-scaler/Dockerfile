FROM python:3.10-alpine3.16

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apk add gcc make musl-dev --no-cache
RUN pip3 install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "start"]
