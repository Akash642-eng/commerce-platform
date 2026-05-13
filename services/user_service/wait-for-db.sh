#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres.database.svc.cluster.local 5432; do
    sleep 1
done

echo "PostgreSQL started"

uvicorn services.user_service.app.main:app \
    --host 0.0.0.0 \
    --port 8000