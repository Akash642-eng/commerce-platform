from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import time
import uuid

from .config import SERVICES
from .middleware import RateLimitMiddleware
from .validator import validate_request

app = FastAPI(title="API Gateway")

# ✅ Attach Rate Limiter
app.add_middleware(RateLimitMiddleware)


@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):

    # ❌ Invalid service
    if service not in SERVICES:
        return JSONResponse(
            status_code=404,
            content={"error": "Service not found"}
        )

    # ✅ Validate request
    is_valid, error = await validate_request(request)
    if not is_valid:
        return JSONResponse(
            status_code=400,
            content={"error": error}
        )

    url = f"{SERVICES[service]}/{path}"

    # ✅ Request tracing
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        # 🔥 Fix headers
        headers = dict(request.headers)
        headers.pop("host", None)

        # 🔥 Read body safely
        body = await request.body()

        print(f"➡️ [{request_id}] {request.method} {service}/{path}", flush=True)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body if body else None
            )

        duration = round((time.time() - start_time) * 1000, 2)

        print(
            f"⬅️ [{request_id}] {response.status_code} {service} ({duration} ms)",
            flush=True
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
        duration = round((time.time() - start_time) * 1000, 2)

        print(
            f"❌ [{request_id}] ERROR {service} ({duration} ms) → {str(e)}",
            flush=True
        )

        return JSONResponse(
            status_code=503,
            content={
                "error": "Service unavailable",
                "service": service,
                "request_id": request_id,
                "details": str(e)
            }
        )


# ✅ Optional direct shortcut (cleaner version)
@app.api_route("/orders", methods=["GET", "POST"])
async def orders_root(request: Request):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            if request.method == "POST":
                body = await request.json()
                response = await client.post(
                    "http://order-service:8000/orders/",
                    json=body
                )
            else:
                response = await client.get(
                    "http://order-service:8000/orders/"
                )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/")
def root():
    return {"message": "API Gateway Running"}