# Maintenance Guide

## Retraining Cadence

Recommend a **weekly** retrain in production (property markets move slowly
enough that daily retraining adds cost without meaningfully improving
accuracy). Automate this as a scheduled GitHub Actions job or Kubernetes
CronJob that runs `ml-pipeline/training/train_models.py` against the latest
data snapshot, then promotes the model only if it clears the quality gate.

## Model Registry Hygiene

`backend/models/registry/` accumulates one `.pkl` + one `metadata_<version>.json`
per training run. In production, prune artifacts older than N versions (keep
enough history for rollback — 5–10 versions is typical) with a scheduled
cleanup script.

## Database Maintenance

- The `predictions` table grows unbounded. Add a retention job (e.g., archive
  or delete rows older than 90 days) once real user data is involved, both
  for storage cost and for data-privacy compliance.
- For production write volumes beyond a few requests/second sustained,
  migrate from SQLite to PostgreSQL — the `backend/database/models.py`
  functions are already written as parameterized SQL, so migration mainly
  means swapping the connection string and driver.

## Monitoring Health

Check weekly (or wire into an on-call rotation via Alertmanager):
- **Error rate** — `HighErrorRate` alert fires above 5% 5xx over 5 minutes
- **Latency** — `HighLatency` alert fires if P95 exceeds 500ms
- **Model drift** — compare recent `predictions` table input distributions
  (location mix, area range, etc.) against the training data profile; a
  significant shift suggests the model needs retraining on fresher data even
  if accuracy metrics haven't degraded yet

## Dependency Updates

`requirements.txt` pins exact versions for reproducibility. Review and bump
quarterly; run the full test suite (`pytest tests/ -v --cov=backend`) after
any dependency bump before merging.

## Incident Response

1. Check `/api/v1/health` — if `model_loaded: false`, the registry artifact
   is missing or corrupted; redeploy from the last known-good version
   (see `docs/DEPLOYMENT.md` → Rollback).
2. Check Grafana for latency/error spikes correlated with a specific
   endpoint or time window.
3. Check `docker compose logs backend` / `kubectl logs` for stack traces.
