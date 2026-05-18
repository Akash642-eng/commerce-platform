#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres.database.svc.cluster.local 5432; do
  sleep 1
done

echo "PostgreSQL started"

echo "Starting cart-service..."

# FIX Bug#4: full dotted module path â€” build context is repo root, so /app/services/cart_service/app/main.py
exec uvicorn services.cart_service.app.main:app \
  --host 0.0.0.0 \
  --port 8000
