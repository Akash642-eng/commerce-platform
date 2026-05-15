import json
import time
import uuid

import httpx
import redis
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram,
                               generate_latest)

from shared.config.settings import settings
from shared.tracing.tracing import setup_tracing

from .config import SERVICES

app = FastAPI(title="API Gateway", redirect_slashes=False)


setup_tracing(app, "api-gateway")


REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "gateway_request_latency_seconds", "Request latency", ["endpoint"]
)


RESERVED_ROUTES = {"health", "docs", "openapi.json", "redoc", "metrics"}


AUTH_SERVICE_URL = SERVICES["auth"]

ENV = settings.ENV

REDIS_HOST = settings.REDIS_HOST

RATE_LIMIT = 5

WINDOW_SIZE = 10


redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {"message": f"API Gateway Running ({ENV})"}


async def verify_token(request: Request):

    auth_header = request.headers.get("authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing token")

    try:

        async with httpx.AsyncClient(timeout=5.0) as client:

            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/me", headers={"Authorization": auth_header}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.json()

    except Exception:

        raise HTTPException(status_code=401, detail="Unauthorized")


def check_rate_limit(client_id: str):

    key = f"rate_limit:{client_id}"

    current = redis_client.get(key)

    if current is None:

        redis_client.set(key, 1, ex=WINDOW_SIZE)

        return

    if int(current) >= RATE_LIMIT:

        raise HTTPException(status_code=429, detail="Too many requests")

    redis_client.incr(key)


def get_cache_key(service, path, query):
    return f"cache:{service}:{path}:{query}"


def get_cached_response(key):

    cached = redis_client.get(key)

    return json.loads(cached) if cached else None


def set_cache_response(key, data):

    redis_client.set(key, json.dumps(data), ex=15)


def validate_order_request(body):

    if not body:

        raise HTTPException(status_code=400, detail="Empty body")

    if "user_id" not in body:

        raise HTTPException(status_code=400, detail="user_id required")

    if "items" not in body or not isinstance(body["items"], list):

        raise HTTPException(status_code=400, detail="items must be list")

    if "total_amount" not in body:

        raise HTTPException(status_code=400, detail="total_amount required")


@app.api_route(
    "/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def gateway(service: str, path: str, request: Request):

    if service in RESERVED_ROUTES or service.startswith("health"):

        raise HTTPException(status_code=404, detail="Not found")

    if service not in SERVICES:

        raise HTTPException(status_code=404, detail="Service not found")

    trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())

    start_time = time.time()

    endpoint = f"{service}/{path}"

    try:

        if service != "auth":

            user = await verify_token(request)

            client_id = user["user"]["user_id"]

            check_rate_limit(client_id)

        service_url = SERVICES[service].rstrip("/")

        target_path = "/" + path.lstrip("/")

        if not target_path.endswith("/"):
            target_path += "/"

        url = f"{service_url}{target_path}"

        headers = dict(request.headers)

        headers.pop("host", None)

        headers["x-trace-id"] = trace_id

        raw_body = await request.body()

        parsed_body = None

        if raw_body:

            try:

                parsed_body = json.loads(raw_body)

            except Exception:

                raise HTTPException(status_code=400, detail="Invalid JSON")

        if service == "orders" and request.method == "POST":

            validate_order_request(parsed_body)

        cache_key = get_cache_key(service, path, str(request.query_params))

        if request.method == "GET":

            cached = get_cached_response(cache_key)

            if cached:

                REQUEST_COUNT.labels(request.method, endpoint, "200").inc()

                return cached

        timeout = 10.0 if ENV == "dev" else 5.0

        async with httpx.AsyncClient(timeout=timeout) as client:

            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=raw_body if raw_body else None,
            )

        try:

            response_data = response.json()

        except Exception:

            response_data = {"message": response.text}

        if request.method == "GET":

            set_cache_response(cache_key, response_data)

        duration = time.time() - start_time

        REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()

        REQUEST_LATENCY.labels(endpoint).observe(duration)

        return Response(
            content=json.dumps(response_data),
            status_code=response.status_code,
            media_type="application/json",
            headers={"x-trace-id": trace_id},
        )

    except httpx.RequestError as e:

        REQUEST_COUNT.labels(request.method, endpoint, "503").inc()

        raise HTTPException(status_code=503, detail=str(e))
