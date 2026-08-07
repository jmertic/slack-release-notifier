# Setting base image to Python 3 on Alpine
FROM python:3-alpine

# Set working directory inside the container
WORKDIR /action

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock* /action/

# Install dependencies into system Python without root package
RUN poetry install --no-root --only main --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /action

# Run the main.py script
CMD [ "python", "/action/main.py" ]
