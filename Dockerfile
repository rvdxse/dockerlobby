FROM python:3.11-alpine AS builder

WORKDIR /build

RUN apk add --no-cache build-base gcc musl-dev

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.11-alpine

ARG DOCKER_GID=985

RUN apk add --no-cache tzdata

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1 

WORKDIR /app

RUN addgroup -g $DOCKER_GID docker_host && \
    adduser -D botuser && \
    addgroup botuser docker_host && \
    chown -R botuser /app

USER botuser

COPY --from=builder /root/.local /home/botuser/.local
COPY --chown=botuser:botuser . .

ENV PATH=/home/botuser/.local/bin:$PATH

ENTRYPOINT ["gunicorn", \
            "--bind", "0.0.0.0:8080", \
            "--workers", "4", \
            "--worker-class", "gthread", \
            "--threads", "2", \
            "run:app"]
