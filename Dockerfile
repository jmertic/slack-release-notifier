FROM python:3-alpine@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc

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
