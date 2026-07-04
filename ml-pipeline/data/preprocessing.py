"""
Preprocessing / feature-engineering pipeline shared by training and
inference so both paths stay perfectly in sync (a common source of
train/serve skew in production ML systems).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["area", "bedrooms", "bathrooms", "age", "floor", "amenities_score"]
CATEGORICAL_FEATURES = ["location", "property_type", "facing"]


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Adds derived features that improve model signal."""

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        X["price_per_sqft_proxy"] = X["amenities_score"] / (X["age"] + 1)
        X["rooms_total"] = X["bedrooms"] + X["bathrooms"]
        X["is_high_floor"] = (X["floor"] >= 10).astype(int)
        X["is_new"] = (X["age"] <= 3).astype(int)
        return X


def build_preprocessor() -> Pipeline:
    """Returns a full sklearn Pipeline: feature engineering -> encoding/scaling."""
    engineered_numeric = NUMERIC_FEATURES + [
        "price_per_sqft_proxy",
        "rooms_total",
        "is_high_floor",
        "is_new",
    ]

    column_transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), engineered_numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("feature_engineering", FeatureEngineer()),
            ("column_transform", column_transformer),
        ]
    )
    return pipeline


def load_dataset(path: str) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)
    X = df.drop(columns=["price"])
    y = np.log1p(df["price"])  # log-transform target to stabilize variance
    return X, y
