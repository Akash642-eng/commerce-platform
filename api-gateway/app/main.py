from fastapi import FastAPI, Request
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

@app.api_route("/{service}/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        return {"error": "Service not found"}

    url = f"{SERVICES[service]}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            headers=request.headers.raw,
            content=await request.body()
        )

    return response.json()


@app.get("/")
def root():
    return {"message": "API Gateway Running"}