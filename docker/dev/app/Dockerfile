FROM python:3.10.6-alpine3.16
ENV PYTHONUNBUFFERED=1 \
# poetry
POETRY_HOME="/opt/poetry" \
POETRY_CACHE_DIR="/opt/poetry/cache" \
SETUP_PATH='/opt/setup' \
POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_IN_PROJECT=false \
POETRY_VIRTUALENVS_CREATE=false \
# pip
PIP_NO_CACHE_DIR=off \
PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apk update && apk add gcc python3-dev curl

RUN pip3 install poetry-core poetry

WORKDIR $SETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-root

WORKDIR /app

COPY . .

RUN mkdir -p logs

CMD ["poetry", "run", "uvicorn", "main:app", "--reload"]
