#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 1
done

echo "Waiting for rabbitmq..."
while ! nc -z rabbitmq 5672; do
  sleep 1
done

echo "Starting service..."

cd /app
export PYTHONPATH=/app

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000