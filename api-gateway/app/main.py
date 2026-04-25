from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="API Gateway")

SERVICES = {
    "auth": "http://auth-service:8000",
    "users": "http://user-service:8000",
    "products": "http://product-service:8000",
    "inventory": "http://inventory-service:8000",
    "cart": "http://cart-service:8000",
    "orders": "http://order-service:8000",
    "payments": "http://payment-service:8000",
    "delivery": "http://delivery-service:8000",
    "notifications": "http://notification-service:8000",
    "support": "http://support-service:8000",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):

    if service not in SERVICES:
        return {"error": "Service not found"}

    url = f"{SERVICES[service]}/{path}"

    try:
        # 🔥 Fix headers
        headers = dict(request.headers)
        headers.pop("host", None)

        # 🔥 Handle body safely
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
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "API Gateway Running"}