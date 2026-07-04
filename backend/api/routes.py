import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    BatchPropertyRequest,
    HealthResponse,
    MetricsResponse,
    PredictionResponse,
    PropertyRequest,
)
from backend.database.models import get_prediction_stats
from backend.services.prediction_service import ModelNotLoadedError, prediction_service

logger = logging.getLogger("real_estate_api")
router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse, tags=["Observability"])
async def health_check():
    return HealthResponse(
        status="healthy" if prediction_service.is_ready else "degraded",
        model_loaded=prediction_service.is_ready,
        model_version=prediction_service.version,
        timestamp=datetime.now().isoformat(),
    )


@router.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_price(request: PropertyRequest):
    try:
        result = prediction_service.predict(request.model_dump())
        return result
    except ModelNotLoadedError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/batch", response_model=list[PredictionResponse], tags=["Prediction"])
async def predict_batch(request: BatchPropertyRequest):
    try:
        payloads = [p.model_dump() for p in request.properties]
        return prediction_service.predict_batch(payloads)
    except ModelNotLoadedError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Batch prediction failed")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.get("/metrics", response_model=MetricsResponse, tags=["Observability"])
async def get_metrics():
    stats = get_prediction_stats()
    meta = prediction_service.get_metadata()
    best_model = meta.get("best_model")
    model_metrics = meta.get("metrics", {}).get(best_model, {}) if best_model else {}
    return MetricsResponse(
        total_predictions=stats.get("total") or 0,
        avg_latency_ms=stats.get("avg_latency"),
        avg_predicted_price=stats.get("avg_price"),
        model_version=prediction_service.version,
        model_r2=model_metrics.get("r2"),
        model_mae=model_metrics.get("mae"),
    )


@router.post("/reload-model", tags=["Admin"])
async def reload_model():
    """Hot-reloads the production model from the registry (used after CI/CD retrains)."""
    prediction_service.reload()
    return {"status": "reloaded", "model_version": prediction_service.version}
