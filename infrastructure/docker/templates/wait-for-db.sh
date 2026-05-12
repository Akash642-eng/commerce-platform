#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

echo "PostgreSQL started"

if [ ! -z "$RABBITMQ_ENABLED" ]; then

  echo "Waiting for rabbitmq..."

  while ! nc -z rabbitmq 5672; do
    sleep 1
  done

  echo "RabbitMQ started"
fi

echo "Starting service..."

exec "$@"