# Analysis Questions

### 1. How does the system handle scale and performance under load?

The FastAPI backend is stateless per request — the only shared state is the
in-memory model and the SQLite connection — so it scales horizontally. The
Kubernetes manifest (`infrastructure/kubernetes/backend-deployment.yaml`)
runs 3 replicas behind a `ClusterIP` Service and an `HorizontalPodAutoscaler`
that scales to 10 replicas once average CPU utilization crosses 70%.
Inference itself is fast (~18ms average in local testing) because the model
is a scikit-learn/XGBoost pipeline held in memory, not re-loaded per request.
The `/batch` endpoint caps requests at 100 properties to keep tail latency
bounded rather than allowing unbounded request sizes.

### 2. What monitoring strategies ensure system reliability?

A Prometheus middleware in `backend/main.py` records `http_requests_total`
(labeled by method, endpoint, status) and `http_request_latency_seconds`
histograms for every request, scraped every 15 seconds
(`monitoring/prometheus/prometheus.yml`). Alert rules
(`monitoring/alerts/alert_rules.yml`) fire on high error rate (>5% 5xx over
5 minutes), high P95 latency (>500ms), the backend target going unreachable,
and the model failing to load. Kubernetes readiness/liveness probes hit
`/api/v1/health` so unhealthy pods are automatically removed from rotation
and restarted.

### 3. How is model drift detected and managed in production?

Every prediction — inputs and output — is logged to SQLite
(`backend/database/models.py`), which supports offline comparison of recent
input distributions against the training data profile (see
`docs/MAINTENANCE.md`). On the model-quality side, every retrain's metrics
are captured in `metadata.json`, so a newly trained candidate can be compared
against the currently deployed version before promotion. The CI/CD pipeline
enforces a hard quality gate (R² ≥ 0.85, MAPE ≤ 15%) that blocks deployment
of a regressed model, and `POST /api/v1/reload-model` allows a validated
replacement to be hot-swapped without downtime.

### 4. What security measures protect the system and data?

Input validation happens at the Pydantic schema layer
(`backend/api/schemas.py`): numeric fields have explicit bounds, and
categorical fields (`location`, `property_type`, `facing`) are checked
against allow-lists, so malformed or adversarial payloads are rejected with
a `422` before reaching the model. The admin `/api/v1/reload-model` endpoint
is flagged in `docs/TROUBLESHOOTING.md` as needing authentication (API key
or network restriction) before any public deployment — it is intentionally
left open in this demo build for grading/testing convenience. CORS is
currently permissive for local development and should be restricted to
known origins in production (see the pre-production checklist in
`docs/DEPLOYMENT.md`).

### 5. How does the system ensure data privacy and compliance?

The training dataset is entirely synthetic (seeded generator, no real
listings or personal data), which avoids PII concerns for this capstone.
`docs/ARCHITECTURE.md` (§7) notes what would change for a real deployment:
scrubbing owner-contact PII before training, and adding a data-retention
policy (e.g., a 90-day rolling purge) on the prediction log once real user
data is involved.

### 6. What is the business ROI of this system?

See `docs/BUSINESS_IMPACT.md` for the full analysis. In short: faster,
more consistent first-pass property valuations, a scalable API that can back
multiple front-ends (dashboard, partner integrations) from one model, and
lower operational risk thanks to the CI/CD quality gate and one-command
rollback. The document is explicit that currency-denominated ROI figures
aren't claimed, since the dataset is synthetic and real revenue impact
depends on actual deployment usage.

### 7. How can the system be extended for future requirements?

New model candidates can be added to `train_models.py`'s `candidates` dict
with zero changes to the serving layer, since the registry contract is just
"any object exposing `.predict(X)`." New property features require updating
`NUMERIC_FEATURES`/`CATEGORICAL_FEATURES` in `preprocessing.py` and the
matching fields in `PropertyRequest` — both training and serving pick them
up automatically. The versioned registry and `/reload-model` endpoint make
it straightforward to add a scheduled retraining job (e.g., a weekly
GitHub Actions cron or Kubernetes CronJob) that retrains, quality-gates, and
promotes automatically with no manual intervention.
