FROM python:3.14-slim AS builder
WORKDIR /worklog
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt
RUN poetry export -f requirements.txt --with test --output requirements-test.txt

# только установка базовых зависимостей — без кода
FROM python:3.14-slim AS base-deps
WORKDIR /worklog
RUN useradd -m appuser
COPY --from=builder /worklog/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# отдельная ветка с тестовыми зависимостями — тоже без кода
FROM base-deps AS test-deps
USER root
COPY --from=builder /worklog/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
USER appuser

# --- конечные стадии: код копируется последним ---

FROM base-deps AS prod
COPY --chown=appuser:appuser . .
RUN rm -rf /worklog/tests
USER appuser

FROM test-deps AS test
COPY --chown=appuser:appuser . .
USER appuser

FROM test-deps AS dev
COPY --chown=appuser:appuser . .
USER appuser