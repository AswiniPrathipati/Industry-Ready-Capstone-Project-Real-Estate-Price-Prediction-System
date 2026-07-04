# API Reference

Base URL (local): `http://localhost:8000`
Interactive docs: `GET /docs` (Swagger UI), `GET /redoc` (ReDoc)

All endpoints return JSON. All prediction endpoints require the fields in
**PropertyRequest** below; validation errors return HTTP `422` with a
field-level detail message.

## PropertyRequest schema

| Field | Type | Constraints | Default |
|---|---|---|---|
| `area` | float | 0 < area ≤ 20000 (sq ft) | required |
| `bedrooms` | int | 1–10 | required |
| `bathrooms` | int | 1–10 | required |
| `age` | int | 0–100 (years) | required |
| `location` | string | one of the 8 supported micro-markets* | required |
| `property_type` | string | Apartment, Independent House, Villa, Studio | required |
| `floor` | int | 0–100 | 1 |
| `facing` | string | East, West, North, South, North-East, South-West | East |
| `amenities_score` | float | 0–10 | 5.0 |

\* Banjara Hills, Gachibowli, Madhapur, Kondapur, Kukatpally, Miyapur, Uppal, LB Nagar

---

## `POST /api/v1/predict`

Predicts the price for a single property.

**Request body:** `PropertyRequest`

**Response `200`:**
```json
{
  "prediction_id": "59efc7a0-39d5-49d3-a642-b854a2d5dc6d",
  "timestamp": "2026-07-04T06:33:08.825922",
  "predicted_price": 15688444.25,
  "currency": "INR",
  "confidence_interval": { "lower_bound": 14433368.71, "upper_bound": 16943519.79 },
  "model_version": "20260704_063232",
  "latency_ms": 18.38
}
```

**Errors:** `422` invalid input · `503` model not loaded · `500` internal error

---

## `POST /api/v1/batch`

Predicts prices for up to 100 properties in one request.

**Request body:**
```json
{ "properties": [ { "...PropertyRequest fields...": "..." }, "..." ] }
```

**Response `200`:** array of `PredictionResponse` objects (same shape as `/predict`).

---

## `GET /api/v1/health`

Liveness/readiness probe used by Docker/Kubernetes health checks.

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "20260704_063232",
  "timestamp": "2026-07-04T06:33:08.804200"
}
```

`status` is `"degraded"` if no model is currently loaded.

---

## `GET /api/v1/metrics`

Business/prediction metrics (distinct from the Prometheus `/metrics` endpoint).

```json
{
  "total_predictions": 124587,
  "avg_latency_ms": 18.7,
  "avg_predicted_price": 8452110.4,
  "model_version": "20260704_063232",
  "model_r2": 0.982,
  "model_mae": 614137.9
}
```

---

## `GET /metrics`

Prometheus scrape endpoint (`text/plain`), exposing `http_requests_total`
and `http_request_latency_seconds` histograms, plus standard Python/GC
process metrics.

---

## `POST /api/v1/reload-model`

Hot-reloads the production model from `backend/models/registry/production_model.pkl`
without restarting the service — used after a CI/CD pipeline promotes a new
model version.

```json
{ "status": "reloaded", "model_version": "20260704_071500" }
```

> ⚠️ This endpoint is unauthenticated in the demo configuration. See
> `docs/TROUBLESHOOTING.md` for hardening guidance before exposing it publicly.
