FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["gunicorn", \
            "--bind", "0.0.0.0:8080", \
            "--workers", "4", \
            "--worker-class", "gthread", \
            "--threads", "2", \
            "run:app"]
