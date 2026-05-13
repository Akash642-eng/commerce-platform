from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from prometheus_fastapi_instrumentator import Instrumentator

from .database import Base
from .database import engine

from shared.logging.logger import log_event

from .routes import users
from .routes import auth


load_dotenv()


app = FastAPI(
    title="User Service",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


Instrumentator().instrument(app).expose(app)


app.include_router(auth.router)
app.include_router(users.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="user-service",
        event="startup",
        trace_id="system",
        message="User Service started successfully"
    )


@app.on_event("shutdown")
def shutdown_event():

    log_event(
        service="user-service",
        event="shutdown",
        trace_id="system",
        message="User Service shutting down"
    )


@app.get("/")
def root():

    return {
        "service": "user-service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy"
        }
    )


@app.get("/live")
def liveness_probe():

    return JSONResponse(
        status_code=200,
        content={
            "status": "alive"
        }
    )


@app.get("/ready")
def readiness_probe():

    try:

        connection = engine.connect()

        connection.close()

        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "database": "connected"
            }
        )

    except Exception as e:

        log_event(
            service="user-service",
            event="readiness_failed",
            trace_id="system",
            message="Readiness probe failed",
            data={
                "error": str(e)
            },
            level="ERROR"
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "disconnected"
            }
        )