"""
FastAPI application entrypoint for the Real Estate Price Prediction
System capstone project.

Run locally:
    uvicorn backend.main:app --reload --port 8000

Docs available at /docs (Swagger UI) once running.
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from backend.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("real_estate_api")

app = FastAPI(
    title="Real Estate Price Predictor",
    description="Production ML system for predicting real-estate prices in Hyderabad micro-markets.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus instrumentation ---
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["endpoint"])


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    endpoint = request.url.path
    REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint).observe(elapsed)
    logger.info("%s %s -> %s (%.1fms)", request.method, endpoint, response.status_code, elapsed * 1000)
    return response


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Real Estate Price Predictor",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


app.include_router(router)
