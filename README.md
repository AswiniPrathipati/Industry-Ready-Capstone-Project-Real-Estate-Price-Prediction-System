# 🏢 Real Estate Price Prediction System

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)

**Capstone Project — Month 6: Capstone & Career Launch**
VIT-AP University · B.Tech/BSc-MSc Data Science · The Developers Arena Internship
Author: **Aswini** (Reg. No. 21BSD7033)

A complete, production-ready data science system that predicts real-estate
prices for Hyderabad micro-markets, featuring an automated ML pipeline,
a FastAPI backend, a Streamlit business-intelligence dashboard, containerized
deployment, monitoring/alerting, and a CI/CD pipeline with a model quality gate.

---

## 🎯 Project Goals

- Predict property prices from structural and location features with high accuracy
- Compare multiple ML algorithms and automatically promote the best performer
- Serve predictions through a versioned, monitored, horizontally-scalable API
- Give business stakeholders a live BI dashboard, not just a model in a notebook
- Demonstrate industry-standard MLOps practices: testing, CI/CD, containerization,
  a model registry, and observability

## 📊 Model Performance (validation set)

| Model | MAE (₹) | MAPE | R² |
|---|---|---|---|
| Ridge Regression | 1,104,287 | 12.09% | 0.919 |
| Random Forest | 814,947 | 8.34% | 0.969 |
| Gradient Boosting | 624,146 | 6.34% | 0.981 |
| XGBoost | 639,027 | 6.39% | 0.980 |
| **Ensemble (GB + XGBoost) — production model** | **614,138** | **6.18%** | **0.982** |

## 🏗️ Architecture

```
Client (Streamlit dashboard / API consumer)
        │
        ▼
FastAPI backend (uvicorn, 3+ replicas behind a load balancer)
        │
   ┌────┴─────┐
   ▼          ▼
Model       SQLite
Registry    (prediction log +
(pickled     model version
ensemble)    history)
        │
        ▼
Prometheus (metrics) → Grafana (dashboards) → Alertmanager (alerts)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full system design.

## 🚀 Quick Start

### Option A — Docker Compose (recommended, full stack)

```bash
docker compose up --build
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Option B — Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate data and train models
python ml-pipeline/data/generate_data.py
python ml-pipeline/training/train_models.py

# 3. Start the API
uvicorn backend.main:app --reload --port 8000

# 4. In a second terminal, start the dashboard
streamlit run frontend/dashboard.py
```

Full setup instructions: [`docs/SETUP.md`](docs/SETUP.md)

## 🔌 API Usage

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
        "area": 1450, "bedrooms": 3, "bathrooms": 2, "age": 5,
        "location": "Gachibowli", "property_type": "Apartment",
        "floor": 6, "facing": "East", "amenities_score": 7.5
      }'
```

Full API reference: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

## 🧪 Testing

```bash
pytest tests/ -v --cov=backend --cov-report=term-missing
```

33 tests covering preprocessing, request validation, API endpoints, and a
model-quality gate — **92% coverage**, exceeding the 80% requirement.

## 📁 Project Structure

```
capstone-project/
├── backend/            FastAPI application, services, DB models, model registry
├── frontend/           Streamlit BI dashboard
├── ml-pipeline/         Data generation, preprocessing, training, evaluation
├── infrastructure/      Docker, Docker Compose, Kubernetes manifests
├── monitoring/          Prometheus, Grafana, alert rules
├── tests/               Unit, integration & model-quality tests
├── docs/                Full documentation suite
├── .github/workflows/   CI/CD pipeline
└── scripts/             Automation helpers
```

## 📚 Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design & component breakdown |
| [SETUP.md](docs/SETUP.md) | Installation & configuration guide |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Full endpoint reference |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment guide (Docker & Kubernetes) |
| [USER_MANUAL.md](docs/USER_MANUAL.md) | Dashboard user guide |
| [MAINTENANCE.md](docs/MAINTENANCE.md) | Maintenance & retraining playbook |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & fixes |
| [BUSINESS_IMPACT.md](docs/BUSINESS_IMPACT.md) | ROI & business impact analysis |
| [ANALYSIS_QUESTIONS.md](docs/ANALYSIS_QUESTIONS.md) | Answers to the capstone analysis questions |

## 🛠️ Tech Stack

FastAPI · scikit-learn · XGBoost · Streamlit · SQLite · Docker · Docker Compose
· Kubernetes · Prometheus · Grafana · GitHub Actions · pytest

## 📄 License

MIT — see [LICENSE](LICENSE).
