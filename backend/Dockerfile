# Create stage for Poetry installation
FROM python:3.12-slim as poetry-base

# Install required system dependencies for venv
RUN apt-get update && apt-get install -y \
    python3-venv \
    gcc \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv /opt/poetry-venv \
    && /opt/poetry-venv/bin/pip install -U pip setuptools \
    && /opt/poetry-venv/bin/pip install poetry==1.8.3

# Create a new stage from the base python image
FROM python:3.12-slim as reoport-assistant

# Copy Poetry to app image
COPY --from=poetry-base /opt/poetry-venv /opt/poetry-venv

# Add Poetry to PATH
ENV PATH="${PATH}:/opt/poetry-venv/bin"

WORKDIR /app
# Copy Dependencies
COPY pyproject.toml ./

RUN poetry lock

RUN poetry check
# Install Dependencies
RUN poetry install --no-interaction --no-cache --without dev

# Copy Application
COPY . /app

WORKDIR reportassistant

#RUN poetry run python manage.py collectstatic --noinput