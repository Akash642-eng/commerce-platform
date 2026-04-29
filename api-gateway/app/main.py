from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import time
import json
import redis
import os

from .config import SERVICES

app = FastAPI(title="API Gateway")

AUTH_SERVICE_URL = "http://auth-service:8000"

# 🔥 REDIS CONNECTION
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# 🔥 RATE LIMIT CONFIG
RATE_LIMIT = 5
WINDOW_SIZE = 10  # seconds

# 🔐 TOKEN VERIFY
async def verify_token(request: Request):
    auth_header = request.headers.get("authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/me",
                headers={"Authorization": auth_header}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.json()

    except Exception:
        raise HTTPException(status_code=401, detail="Auth service error")

# 🚦 REDIS RATE LIMIT
def check_rate_limit(client_id: str):
    key = f"rate_limit:{client_id}"

    current = redis_client.get(key)

    if current is None:
        redis_client.set(key, 1, ex=WINDOW_SIZE)
        return

    if int(current) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")

    redis_client.incr(key)

# 🧠 CACHE (GET only)
def get_cache_key(service: str, path: str, query: str):
    return f"cache:{service}:{path}:{query}"

def get_cached_response(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cache_response(key, data):
    redis_client.set(key, json.dumps(data), ex=15)  # 15 sec cache

# ✅ VALIDATION
def validate_order_request(body: dict):
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")

    if "user_id" not in body:
        raise HTTPException(status_code=400, detail="user_id required")

    if "items" not in body or not isinstance(body["items"], list):
        raise HTTPException(status_code=400, detail="items must be list")

    if "total_amount" not in body:
        raise HTTPException(status_code=400, detail="total_amount required")

# 🌐 MAIN ROUTER
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):

    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    # 🔐 AUTH + RATE LIMIT
    if service != "auth":
        user = await verify_token(request)
        client_id = user["user"]["user_id"]
        check_rate_limit(client_id)

    # 🔥 BUILD URL
    if path:
        url = f"{SERVICES[service]}/{path}"
    else:
        url = f"{SERVICES[service]}/{service}/"

    try:
        headers = dict(request.headers)
        headers.pop("host", None)

        raw_body = await request.body()
        parsed_body = None

        if raw_body:
            try:
                parsed_body = json.loads(raw_body)
            except:
                raise HTTPException(status_code=400, detail="Invalid JSON")

        # ✅ VALIDATION
        if service == "orders" and request.method == "POST":
            validate_order_request(parsed_body)

        # 🔥 CACHE CHECK (GET only)
        cache_key = get_cache_key(service, path, str(request.query_params))

        if request.method == "GET":
            cached = get_cached_response(cache_key)
            if cached:
                print("⚡ CACHE HIT", flush=True)
                return cached

        # 🔁 FORWARD REQUEST
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=raw_body if raw_body else None
            )

        response_data = response.json()

        # 💾 STORE CACHE
        if request.method == "GET":
            set_cache_response(cache_key, response_data)

        return Response(
            content=json.dumps(response_data),
            status_code=response.status_code,
            media_type="application/json"
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"{service} unavailable: {str(e)}"
        )

# 🏠 ROOT
@app.get("/")
def root():
    return {"message": "API Gateway Running"}