import time

from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.responses import JSONResponse


REQUEST_LOG = {}

RATE_LIMIT = 10
WINDOW_SIZE = 60


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        client_ip = request.client.host

        current_time = time.time()

        if client_ip not in REQUEST_LOG:
            REQUEST_LOG[client_ip] = []

        REQUEST_LOG[client_ip] = [
            t for t in REQUEST_LOG[client_ip]
            if current_time - t < WINDOW_SIZE
        ]

        if len(REQUEST_LOG[client_ip]) >= RATE_LIMIT:

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded"
                }
            )

        REQUEST_LOG[client_ip].append(current_time)

        response = await call_next(request)

        return response