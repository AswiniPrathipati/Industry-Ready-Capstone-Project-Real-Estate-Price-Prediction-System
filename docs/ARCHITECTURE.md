# System Architecture

## 1. Overview

The system is split into four independently deployable layers: **data/ML
pipeline**, **serving layer (API)**, **presentation layer (dashboard)**, and
**observability layer**. This separation lets the model be retrained and
promoted without touching the API code, and lets the dashboard be scaled
independently of the prediction service.

## 2. Component Diagram

```
                         ┌───────────────────────────┐
                         │   ml-pipeline/             │
                         │  generate_data.py          │
                         │  preprocessing.py          │
                         │  train_models.py           │
                         │  (Ridge, RF, GB, XGBoost,   │
                         │   auto-ensemble)            │
                         └─────────────┬──────────────┘
                                       │ exports versioned artifact
                                       ▼
                    backend/models/registry/
                    ├── production_model.pkl   (symlink-like "latest")
                    ├── model_<version>.pkl    (immutable history)
                    └── metadata.json          (metrics, feature list)
                                       │ loaded at startup / on /reload-model
                                       ▼
        ┌───────────────────────────────────────────────────────┐
        │                 backend/ (FastAPI)                     │
        │  api/routes.py      → thin HTTP handlers                │
        │  services/prediction_service.py → business logic        │
        │  database/models.py → SQLite (predictions, versions)    │
        │  main.py            → app wiring, Prometheus middleware │
        └───────────────────────────┬─────────────────────────────┘
                                     │ REST (JSON over HTTP)
                     ┌───────────────┼────────────────┐
                     ▼                                 ▼
        frontend/dashboard.py                 Any external API consumer
        (Streamlit: prediction form            (mobile app, partner
         + BI dashboard, reads                  integration, batch job)
         SQLite directly for analytics)
                     │
                     ▼
        Prometheus (scrapes /metrics) → Grafana (dashboards) → Alertmanager
```

## 3. Data Flow

1. **Collection** — in production this layer would poll listing-site APIs and
   municipal records; the capstone simulates this with a seeded synthetic
   generator (`ml-pipeline/data/generate_data.py`) so the whole pipeline is
   reproducible without external API keys.
2. **Preprocessing** — `preprocessing.py` defines a single `FeatureEngineer`
   + `ColumnTransformer` pipeline used identically at training and inference
   time, eliminating train/serve skew.
3. **Training** — `train_models.py` trains four candidate algorithms plus an
   auto-selected ensemble, logs comparative metrics, and writes the winner to
   the model registry with a timestamped version.
4. **Serving** — `PredictionService` loads the registry artifact once at
   startup (singleton pattern) and exposes it via FastAPI routes. Every
   prediction is logged to SQLite for audit and the BI dashboard.
5. **Observability** — a Prometheus middleware records request count and
   latency histograms per endpoint; Grafana visualizes them; Alertmanager
   rules watch for error-rate, latency, and model-load regressions.

## 4. Scalability & Performance Under Load

- The backend is stateless per-request (the model and DB connection are the
  only shared resources), so it scales horizontally — the Kubernetes manifest
  runs 3 replicas by default with an HPA that scales to 10 on CPU > 70%.
- SQLite is adequate for the capstone's demo traffic; the `DEPLOYMENT.md`
  guide describes the swap to PostgreSQL for higher write concurrency.
- The `/batch` endpoint caps requests at 100 properties to keep tail latency
  predictable; larger jobs should use an async queue (see `MAINTENANCE.md`).

## 5. Model Drift Detection & Management

- Every prediction and its inputs are logged, which enables offline drift
  analysis (comparing recent input distributions to training distributions).
- `metadata.json` retains the full metric history per version, so a
  newly retrained model can be compared against the currently deployed one
  before promotion.
- The CI/CD model-quality gate (`tests/test_model_performance.py`) blocks
  deployment of any model that regresses below R² 0.85 or MAPE 15%.
- `POST /api/v1/reload-model` allows hot-swapping the in-memory model after a
  new artifact is dropped into the registry, without a service restart.

## 6. Security

- Input validation is enforced at the schema layer (`backend/api/schemas.py`)
  with allow-lists for categorical fields and numeric bounds, preventing
  malformed or out-of-range payloads from reaching the model.
- The `/reload-model` admin endpoint is a candidate for API-key or mTLS
  protection in a real deployment (currently open for demo purposes — see
  `TROUBLESHOOTING.md` for a note on hardening before public exposure).
- CORS is currently permissive (`allow_origins=["*"]`) for local demo
  convenience; production deployments should restrict this to known origins.

## 7. Data Privacy & Compliance

- The dataset is fully synthetic — no real personal or property-owner data is
  collected or stored, sidestepping PII concerns for the capstone.
- In a real deployment, listing data containing owner contact details would
  need to be scrubbed of PII before entering the training pipeline, and the
  prediction log would need a data-retention policy (e.g., 90-day rolling
  purge) to stay compliant with data-protection regulations.

## 8. Extensibility

- New model candidates can be added to the `candidates` dict in
  `train_models.py` with no changes to the serving layer, since the registry
  contract is "any object with a `.predict(X)` method."
- New property features require updating `NUMERIC_FEATURES` /
  `CATEGORICAL_FEATURES` in `preprocessing.py` and the corresponding fields
  in `PropertyRequest` — both training and serving pick them up automatically.
- The MCP-style `/reload-model` and versioned registry make it straightforward
  to add a scheduled retraining job (e.g., a weekly GitHub Actions cron) that
  retrains, quality-gates, and promotes a new model with no manual steps.
