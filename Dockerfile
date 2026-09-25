FROM python:3-alpine@sha256:9e9fde4d32eedce0b661d9ab91e826b62dddf28e928c230ec55f1866cac66b01

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
