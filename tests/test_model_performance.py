"""
Model-quality gate tests. These are the kind of checks a CI/CD pipeline
runs before promoting a newly trained model to production — if accuracy
regresses below an agreed threshold, the deploy step should fail.
"""
import json
from pathlib import Path

REGISTRY_DIR = Path(__file__).resolve().parents[1] / "backend" / "models" / "registry"
METADATA_PATH = REGISTRY_DIR / "metadata.json"

MIN_ACCEPTABLE_R2 = 0.85
MAX_ACCEPTABLE_MAPE = 0.15


def test_metadata_exists():
    assert METADATA_PATH.exists(), "Run ml-pipeline/training/train_models.py before running tests"


def test_production_model_file_exists():
    assert (REGISTRY_DIR / "production_model.pkl").exists()


def test_best_model_meets_r2_threshold():
    with open(METADATA_PATH) as f:
        meta = json.load(f)
    best = meta["best_model"]
    r2 = meta["metrics"][best]["r2"]
    assert r2 >= MIN_ACCEPTABLE_R2, f"Model R2 {r2:.4f} below acceptance threshold {MIN_ACCEPTABLE_R2}"


def test_best_model_meets_mape_threshold():
    with open(METADATA_PATH) as f:
        meta = json.load(f)
    best = meta["best_model"]
    mape = meta["metrics"][best]["mape"]
    assert mape <= MAX_ACCEPTABLE_MAPE, f"Model MAPE {mape:.3%} above acceptance threshold {MAX_ACCEPTABLE_MAPE:.0%}"


def test_all_candidate_models_were_compared():
    with open(METADATA_PATH) as f:
        meta = json.load(f)
    expected = {"ridge", "random_forest", "gradient_boosting", "xgboost", "ensemble"}
    assert expected.issubset(set(meta["metrics"].keys()))
