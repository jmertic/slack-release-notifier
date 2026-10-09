FROM python:3-alpine@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72

WORKDIR /action

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

COPY requirements-ci.txt /action/

RUN pip install --no-cache-dir --require-hashes -r /action/requirements-ci.txt

COPY pyproject.toml poetry.lock /action/

RUN poetry install --no-root --only main --no-interaction --no-ansi

COPY . /action

CMD [ "python", "/action/main.py" ]
