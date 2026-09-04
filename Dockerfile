FROM python:3-alpine@sha256:c6ead215bfd31f1e433d968853b7a769989117115b728874824e6c0a27cb96fc

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
