FROM python:3.10-slim


ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY Pipfile .

COPY Pipfile.lock .

RUN pip install pipenv

RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --system

ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY . /app/

