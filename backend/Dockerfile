FROM python:3.12-slim

WORKDIR /app

# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .


ENV PYTHONUNBUFFERED=1


