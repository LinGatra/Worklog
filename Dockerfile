FROM python:3.14-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt

FROM python:3.14-slim AS runtime

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY --chown=appuser:appuser . .
USER appuser
