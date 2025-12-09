# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete && \
    find /app/.venv -type f -name "*.pyo" -delete && \
    find /app/.venv -type d -name "*.dist-info" -exec rm -rf {}/RECORD {} + 2>/dev/null || true && \
    find /app/.venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

FROM gcr.io/distroless/python3-debian12:latest

WORKDIR /app

COPY --from=builder /app/.venv/lib/python3.12/site-packages /app/site-packages

COPY --from=builder /app/*.py /app/
COPY --from=builder /app/run.py /app/
COPY --from=builder /app/templates /app/templates
COPY --from=builder /app/static /app/static
COPY --from=builder /app/app /app/app


ENV PYTHONPATH=/app/site-packages:/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random


ENTRYPOINT ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "run:app"]
