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
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),   # ✅ FIXED
                params=request.query_params,     # ✅ ADD THIS
                content=await request.body()
            )

        # ✅ Proper response back to client
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except httpx.RequestError as e:
        return {
            "error": "Service unavailable",
            "service": service,
            "details": str(e)
        }


@app.get("/")
def root():
    return {"message": "API Gateway Running"}