# Deployment Guide

## Option 1: Docker Compose (single host, demo / small-scale production)

```bash
docker compose up --build -d
docker compose logs -f backend   # tail logs
docker compose ps                # check health status
```

Services and ports:

| Service | Port | Notes |
|---|---|---|
| backend | 8000 | FastAPI, trains a fresh model at image build time |
| frontend | 8501 | Streamlit dashboard |
| prometheus | 9090 | Scrapes backend `/metrics` every 15s |
| grafana | 3000 | Default login `admin` / `admin` — change immediately |

To retrain and hot-swap the model without downtime:

```bash
docker compose exec backend python ml-pipeline/training/train_models.py
curl -X POST http://localhost:8000/api/v1/reload-model
```

## Option 2: Kubernetes (multi-node, horizontally-scaled production)

Manifests live in `infrastructure/kubernetes/`.

```bash
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/frontend-and-ingress.yaml
kubectl get pods -n real-estate-ml
kubectl get hpa -n real-estate-ml
```

This provisions:
- **Deployment** (backend): 3 replicas, readiness/liveness probes on
  `/api/v1/health`, resource requests/limits, a PVC-mounted model registry
- **HorizontalPodAutoscaler**: scales 3→10 replicas at 70% CPU utilization
- **Deployment** (frontend): 2 replicas pointed at the backend Service
- **Ingress**: routes `/api/*` to the backend, `/` to the frontend

### Rolling a new model version in Kubernetes

1. Retrain and push a new image (or update the PVC contents via a Job)
2. `kubectl rollout restart deployment/real-estate-backend -n real-estate-ml`
3. Confirm via `kubectl rollout status` and `GET /api/v1/health`

## CI/CD Pipeline

`.github/workflows/ci-cd.yml` runs on every push:

1. **test** — installs deps, generates data, trains a model, runs the full
   pytest suite with a `--cov-fail-under=80` gate
2. **model-quality-gate** — re-runs `tests/test_model_performance.py` to
   enforce the R² ≥ 0.85 / MAPE ≤ 15% acceptance thresholds
3. **build-and-push** — builds backend/frontend Docker images (registry push
   is a placeholder step — wire in your registry credentials as GitHub Secrets)
4. **deploy** — applies Kubernetes manifests and hot-reloads the model
   (placeholder steps — wire in your cluster credentials)

Steps 3–4 only run on pushes to `main`, after both prior jobs succeed.

## Rollback

Because every trained model is retained under
`backend/models/registry/model_<version>.pkl`, rollback is a copy-and-reload:

```bash
cp backend/models/registry/model_<previous_version>.pkl backend/models/registry/production_model.pkl
curl -X POST http://localhost:8000/api/v1/reload-model
```

## Pre-Production Checklist

- [ ] Restrict CORS `allow_origins` to known frontend domains
- [ ] Put `/api/v1/reload-model` behind authentication
- [ ] Replace SQLite with PostgreSQL for concurrent write loads
- [ ] Set a real `GF_SECURITY_ADMIN_PASSWORD` for Grafana
- [ ] Point the Ingress `host` at your real domain and attach TLS
- [ ] Wire the CI/CD placeholder steps to your container registry and cluster
