#!/usr/bin/env bash
# One-command local setup: install deps, generate data, train models, run tests.
set -e

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Generating training data"
python ml-pipeline/data/generate_data.py

echo "==> Training and comparing models"
python ml-pipeline/training/train_models.py

echo "==> Running test suite"
pytest tests/ -v --cov=backend --cov-report=term-missing

echo "==> Setup complete. Start the API with:"
echo "    uvicorn backend.main:app --reload --port 8000"
echo "==> And the dashboard with:"
echo "    streamlit run frontend/dashboard.py"
