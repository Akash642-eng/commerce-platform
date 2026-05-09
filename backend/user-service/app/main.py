from fastapi import FastAPI
from fastapi.responses import JSONResponse

from prometheus_fastapi_instrumentator import Instrumentator

from .database import Base, engine
from .logger import logger

from .routes import users
from .routes import auth


app = FastAPI(
    title="User Service",
    version="1.0.0"
)


# -----------------------------
# DATABASE
# -----------------------------
Base.metadata.create_all(bind=engine)


# -----------------------------
# METRICS
# -----------------------------
Instrumentator().instrument(app).expose(app)


# -----------------------------
# ROUTES
# -----------------------------
app.include_router(auth.router)
app.include_router(users.router)


# -----------------------------
# STARTUP EVENTS
# -----------------------------
@app.on_event("startup")
def startup_event():

    logger.info("User Service started successfully")


@app.on_event("shutdown")
def shutdown_event():

    logger.info("User Service shutting down")


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():

    return {
        "service": "user-service",
        "status": "running",
        "version": "1.0.0"
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health_check():

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy"
        }
    )


# -----------------------------
# LIVENESS PROBE
# -----------------------------
@app.get("/live")
def liveness_probe():

    return JSONResponse(
        status_code=200,
        content={
            "status": "alive"
        }
    )


# -----------------------------
# READINESS PROBE
# -----------------------------
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

        logger.error(f"Readiness probe failed: {str(e)}")

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "disconnected"
            }
        )