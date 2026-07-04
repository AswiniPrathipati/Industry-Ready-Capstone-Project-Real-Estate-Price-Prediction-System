"""
Trains and compares multiple regression models for real-estate price
prediction, selects the best performer, and exports a versioned
artifact to the model registry directory.

Models compared: Ridge, Random Forest, Gradient Boosting, XGBoost,
and a weighted Ensemble of the top-2 tree-based models.
"""
from __future__ import annotations

import json
import pickle
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

sys.path.append(str(Path(__file__).resolve().parents[1] / "data"))
sys.path.append(str(Path(__file__).resolve().parents[2]))
from preprocessing import build_preprocessor, load_dataset  # noqa: E402
from backend.models.ensemble import EnsembleWrapper  # noqa: E402

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "real_estate_data.csv"
REGISTRY_DIR = Path(__file__).resolve().parents[2] / "backend" / "models" / "registry"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


def evaluate(model, X_val, y_val_log) -> dict:
    pred_log = model.predict(X_val)
    pred = np.expm1(pred_log)
    true = np.expm1(y_val_log)
    return {
        "mae": float(mean_absolute_error(true, pred)),
        "mape": float(mean_absolute_percentage_error(true, pred)),
        "r2": float(r2_score(true, pred)),
    }


def main():
    print("Loading dataset...")
    X, y = load_dataset(str(DATA_PATH))
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = build_preprocessor()

    candidates = {
        "ridge": Ridge(alpha=1.0, random_state=42),
        "random_forest": RandomForestRegressor(
            n_estimators=300, max_depth=14, min_samples_leaf=2, n_jobs=-1, random_state=42
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42
        ),
        "xgboost": XGBRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        ),
    }

    results = {}
    fitted_pipelines = {}

    for name, estimator in candidates.items():
        print(f"Training {name} ...")
        start = time.time()
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])
        pipe.fit(X_train, y_train)
        elapsed = time.time() - start
        metrics = evaluate(pipe, X_val, y_val)
        metrics["train_time_sec"] = round(elapsed, 2)
        results[name] = metrics
        fitted_pipelines[name] = pipe
        print(f"  {name}: MAE=₹{metrics['mae']:,.0f} MAPE={metrics['mape']:.3%} R2={metrics['r2']:.4f}")

    # Build a simple ensemble of the two best individual models by R2
    ranked = sorted(results.items(), key=lambda kv: kv[1]["r2"], reverse=True)
    top2_names = [ranked[0][0], ranked[1][0]]
    print(f"Building ensemble from top-2 models: {top2_names}")

    ensemble = EnsembleWrapper([fitted_pipelines[n] for n in top2_names])
    ensemble_metrics = evaluate(ensemble, X_val, y_val)
    results["ensemble"] = ensemble_metrics
    print(f"  ensemble: MAE=₹{ensemble_metrics['mae']:,.0f} MAPE={ensemble_metrics['mape']:.3%} R2={ensemble_metrics['r2']:.4f}")

    best_name = max(results.items(), key=lambda kv: kv[1]["r2"])[0]
    print(f"\nBest model: {best_name} (R2={results[best_name]['r2']:.4f})")

    best_object = ensemble if best_name == "ensemble" else fitted_pipelines[best_name]

    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = REGISTRY_DIR / f"model_{version}.pkl"
    latest_path = REGISTRY_DIR / "production_model.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(best_object, f)
    with open(latest_path, "wb") as f:
        pickle.dump(best_object, f)

    metadata = {
        "version": version,
        "best_model": best_name,
        "metrics": results,
        "feature_columns": list(X.columns),
        "trained_at": datetime.now().isoformat(),
        "training_rows": len(X_train),
        "validation_rows": len(X_val),
    }
    with open(REGISTRY_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    with open(REGISTRY_DIR / f"metadata_{version}.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModel registry updated: {latest_path}")
    print(f"Metadata: {REGISTRY_DIR / 'metadata.json'}")
    return metadata


if __name__ == "__main__":
    main()
