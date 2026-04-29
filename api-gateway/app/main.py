from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import time

from .config import SERVICES

app = FastAPI(title="API Gateway")

AUTH_SERVICE_URL = "http://auth-service:8000"


# 🔥 SIMPLE IN-MEMORY RATE LIMIT
RATE_LIMIT = 5        # max requests
WINDOW_SIZE = 10      # seconds

request_log = {}


# 🔐 TOKEN VERIFICATION
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


# 🚦 RATE LIMIT FUNCTION
def check_rate_limit(client_id: str):
    current_time = time.time()

    if client_id not in request_log:
        request_log[client_id] = []

    # remove old requests
    request_log[client_id] = [
        t for t in request_log[client_id]
        if current_time - t < WINDOW_SIZE
    ]

    if len(request_log[client_id]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")

    request_log[client_id].append(current_time)


# 🌐 MAIN GATEWAY ROUTER
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):

    if service not in SERVICES:
        return {"error": "Service not found"}

    # 🔐 AUTH + RATE LIMIT
    if service != "auth":
        user = await verify_token(request)

        # 🔥 RATE LIMIT KEY = USER ID
        client_id = user["user"]["user_id"]

        check_rate_limit(client_id)

    # 🔥 FIX: handle empty path
    if path:
        url = f"{SERVICES[service]}/{path}"
    else:
        url = f"{SERVICES[service]}/{service}/"

    try:
        headers = dict(request.headers)
        headers.pop("host", None)

        body = await request.body()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body if body else None
            )

        # 🔥 Clean response headers
        excluded_headers = ["content-encoding", "transfer-encoding", "connection"]

        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in excluded_headers
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers
        )

    except httpx.RequestError as e:
        return {
            "error": "Service unavailable",
            "service": service,
            "details": str(e)
        }


# 🏠 ROOT
@app.get("/")
def root():
    return {"message": "API Gateway Running"}