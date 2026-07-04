#!/usr/bin/env bash
# Retrains the model, runs the quality gate, and hot-reloads the running
# API only if the new model passes the acceptance thresholds.
set -e

echo "==> Retraining models"
python ml-pipeline/training/train_models.py

echo "==> Running model quality gate"
pytest tests/test_model_performance.py -v

echo "==> Quality gate passed. Reloading production model via API"
curl -sf -X POST "${API_BASE_URL:-http://localhost:8000}/api/v1/reload-model" || \
  echo "WARNING: could not reach the API to hot-reload; new model is saved to the registry and will load on next restart."
