# Troubleshooting Guide

## `FileNotFoundError` / health check shows `model_loaded: false`

**Cause:** no trained model exists yet in `backend/models/registry/`.
**Fix:**
```bash
python ml-pipeline/data/generate_data.py
python ml-pipeline/training/train_models.py
```
Then restart the API or call `POST /api/v1/reload-model`.

## `pytest` fails with "metadata.json not found"

Same root cause as above — the model-quality-gate tests and several API
tests depend on a trained artifact existing. Run the two commands above
before testing.

## `ModuleNotFoundError: No module named 'preprocessing'` when loading the pickled model

**Cause:** the pickled pipeline references the `FeatureEngineer` class from
`ml-pipeline/data/preprocessing.py`. If that directory isn't on `sys.path`
when unpickling, Python can't resolve the class.
**Fix:** this is already handled in `backend/services/prediction_service.py`
(it appends the `ml-pipeline/data` path before loading the model). If you
see this error in a new script, add the same `sys.path.append(...)` line
before your `pickle.load(...)` call.

## Docker Compose: frontend can't reach backend

**Cause:** the dashboard defaults to `http://localhost:8000`, which doesn't
resolve inside a container network.
**Fix:** confirm `API_BASE_URL=http://backend:8000` is set in the frontend
service's environment in `docker-compose.yml` (it is, by default) — Docker's
internal DNS resolves the service name `backend`.

## 422 Unprocessable Entity on `/predict`

**Cause:** `location`, `property_type`, or `facing` doesn't match the
allow-listed values, or a numeric field is out of range.
**Fix:** check the response body's `detail` field — Pydantic reports exactly
which field failed and why. See `docs/API_REFERENCE.md` for valid values.

## Model accuracy looks wrong / predictions seem off for edge-case inputs

The training data is a seeded synthetic dataset covering realistic but
bounded ranges (e.g., area 300–6000 sqft). Predictions for inputs far outside
the training distribution (e.g., a 15,000 sqft property) will extrapolate
poorly — this is expected model behavior, not a bug. In production, add
input-distribution monitoring (see `MAINTENANCE.md`) to catch this pattern.

## Hardening `/api/v1/reload-model` before public exposure

This endpoint currently has no auth, which is fine for local/demo use but
not for a public deployment. Options: require an API key header checked in
a FastAPI dependency, restrict the route to an internal network/VPC via
Ingress rules, or gate it behind your existing auth middleware if you add one.

## Prometheus shows target as "down"

Confirm the backend container is healthy (`docker compose ps`) and that
`monitoring/prometheus/prometheus.yml`'s target (`backend:8000`) matches the
service name in `docker-compose.yml`.
