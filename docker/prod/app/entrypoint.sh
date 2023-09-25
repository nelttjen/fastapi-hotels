#!/bin/sh

#ls

poetry run alembic upgrade head

#poetry run gunicorn main:app --workers 5 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
poetry run uvicorn main:app