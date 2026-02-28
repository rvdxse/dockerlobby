FROM python:3.14-alpine AS builder

WORKDIR /build

RUN apk add --no-cache build-base gcc musl-dev linux-headers

COPY requirements.txt .

RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

FROM python:3.14-alpine

ARG DOCKER_GID=985

RUN apk add --no-cache tzdata

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/botuser/.local/bin:$PATH

WORKDIR /app
RUN addgroup -g $DOCKER_GID docker_host && \
    adduser -D botuser && \
    addgroup botuser docker_host

COPY --from=builder --chown=botuser:botuser /root/.local /home/botuser/.local
COPY --chown=botuser:botuser requirements.txt .
COPY --chown=botuser:botuser . .

USER botuser

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "run:app"]
