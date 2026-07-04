# Setup Instructions

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Docker & Docker Compose | 24.x+ (only needed for the containerized path) |
| Node.js | Optional — only used for repo tooling in `package.json` |

## 1. Clone and Install

```bash
git clone <repository-url>
cd capstone-project
pip install -r requirements.txt
```

## 2. Generate Data & Train Models

The model registry is not checked into version control (it's a build
artifact), so generate it locally first:

```bash
python ml-pipeline/data/generate_data.py     # writes ml-pipeline/data/real_estate_data.csv
python ml-pipeline/training/train_models.py  # trains 4 models + ensemble, writes to backend/models/registry/
```

You should see output similar to:

```
Best model: ensemble (R2=0.9820)
Model registry updated: backend/models/registry/production_model.pkl
```

## 3. Run the Backend API

```bash
uvicorn backend.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 4. Run the Dashboard

In a separate terminal:

```bash
streamlit run frontend/dashboard.py
```

Visit `http://localhost:8501`.

## 5. Run the Full Stack with Docker Compose

```bash
docker compose up --build
```

This starts: backend (`:8000`), frontend (`:8501`), Prometheus (`:9090`),
and Grafana (`:3000`, login `admin` / `admin`).

## 6. Run the Test Suite

```bash
pytest tests/ -v --cov=backend --cov-report=term-missing
```

## 7. Environment Variables

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `API_BASE_URL` | frontend/dashboard.py | `http://localhost:8000` | Backend URL the dashboard calls |

## Troubleshooting Setup

If `pytest` fails with "metadata.json not found," run step 2 first — the
test suite (and the API itself) depends on a trained model artifact
existing in `backend/models/registry/`.

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) for further issues.
