#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres.database.svc.cluster.local 5432; do
  sleep 1
done

echo "PostgreSQL started"

echo "Waiting for rabbitmq..."

while ! nc -z rabbitmq.messaging.svc.cluster.local 5672; do
  sleep 1
done

echo "RabbitMQ started"

echo "Starting service..."

uvicorn services.inventory_service.app.main:app \
  --host 0.0.0.0 \
  --port 8000