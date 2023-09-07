FROM python:3.10.6-alpine3.16
ENV PYTHONUNBUFFERED=1 \
POETRY_HOME="/opt/poetry" \
POETRY_VIRTUALENVS_IN_PROJECT=true \
POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
RUN apk update && apk add gcc python3-dev

RUN pip3 install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-dev

COPY . .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--reload"]