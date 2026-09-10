FROM python:3.12-slim

WORKDIR /app

# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .


ENV PYTHONUNBUFFERED=1
# Celery forked tasks also need the top-level Flask config module.
ENV PYTHONPATH=/app


