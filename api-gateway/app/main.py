from fastapi import FastAPI, Request, Response, HTTPException
import httpx

from .config import SERVICES

app = FastAPI(title="API Gateway")

AUTH_SERVICE_URL = "http://auth-service:8000"


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


# 🌐 MAIN GATEWAY ROUTER
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):

    if service not in SERVICES:
        return {"error": "Service not found"}

    # 🔐 Skip auth for auth-service
    if service != "auth":
        await verify_token(request)

    # 🔥 FIX: handle empty path (IMPORTANT)
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