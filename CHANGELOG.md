# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — 2026-07-04

### Added
- Synthetic Hyderabad real-estate data generator (6,000 records, 8 micro-markets)
- Feature engineering pipeline (derived ratios, room totals, floor/age flags)
- Multi-model training and comparison: Ridge, Random Forest, Gradient Boosting, XGBoost
- Automatic ensemble construction from the top-2 performing models
- Model registry with versioned artifacts and metadata (`backend/models/registry/`)
- FastAPI backend with `/predict`, `/batch`, `/health`, `/metrics`, `/reload-model`
- Prometheus instrumentation and `/metrics` endpoint for scraping
- SQLite persistence for prediction logs and model version history
- Streamlit BI dashboard with live prediction form and analytics charts
- Docker images for backend and frontend; `docker-compose.yml` full-stack demo
- Kubernetes manifests: Deployment, Service, HPA, Ingress, PVC
- Prometheus alert rules (error rate, latency, service-down, model-not-loaded)
- Grafana dashboard provisioning config
- GitHub Actions CI/CD pipeline: test → model quality gate → build → deploy
- 33-test suite (unit + integration + model-quality gate), 92% coverage
- Full documentation suite (architecture, setup, API reference, deployment,
  user manual, maintenance, troubleshooting, business impact)

## [0.1.0] — Internal development milestone

### Added
- Initial project scaffolding and architecture planning (Week 1)
