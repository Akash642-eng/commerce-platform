#!/bin/sh

echo "Starting service..."

SERVICE_MODULE=$1

PORT=$2

exec uvicorn "$SERVICE_MODULE":app \
    --host 0.0.0.0 \
    --port "$PORT"