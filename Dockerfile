FROM python:3.11-alpine AS builder

WORKDIR /build

RUN apk add --no-cache build-base gcc musl-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir --user -r requirements.txt

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

COPY --from=builder /root/.local /home/botuser/.local
COPY --chown=botuser:botuser . .
RUN pip uninstall -y pip wheel setuptools && \
    rm -rf /home/botuser/.local/lib/python3.11/site-packages/pip* && \
    rm -rf /home/botuser/.local/lib/python3.11/site-packages/wheel* && \
    rm -rf /home/botuser/.local/lib/python3.11/site-packages/setuptools*
USER botuser

ENV PATH=/home/botuser/.local/bin:$PATH

CMD ["gunicorn", \
            "--bind", "0.0.0.0:8080", \
            "--workers", "4", \
            "--worker-class", "gthread", \
            "--threads", "2", \
            "run:app"]
