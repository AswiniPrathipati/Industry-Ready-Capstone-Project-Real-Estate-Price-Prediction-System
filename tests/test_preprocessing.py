import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "ml-pipeline" / "data"))
from preprocessing import FeatureEngineer, build_preprocessor  # noqa: E402


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {
                "area": 1200, "bedrooms": 3, "bathrooms": 2, "age": 5,
                "location": "Gachibowli", "property_type": "Apartment",
                "floor": 4, "facing": "East", "amenities_score": 7.0,
            },
            {
                "area": 2400, "bedrooms": 4, "bathrooms": 3, "age": 12,
                "location": "Kukatpally", "property_type": "Villa",
                "floor": 0, "facing": "North", "amenities_score": 5.5,
            },
        ]
    )


class TestFeatureEngineer:
    def test_adds_derived_columns(self, sample_df):
        fe = FeatureEngineer()
        out = fe.transform(sample_df)
        for col in ["price_per_sqft_proxy", "rooms_total", "is_high_floor", "is_new"]:
            assert col in out.columns

    def test_rooms_total_is_sum(self, sample_df):
        fe = FeatureEngineer()
        out = fe.transform(sample_df)
        assert list(out["rooms_total"]) == [5, 7]

    def test_is_new_flag(self, sample_df):
        fe = FeatureEngineer()
        out = fe.transform(sample_df)
        # is_new is defined as age <= 3; both sample rows (age 5, age 12) exceed that
        assert out["is_new"].tolist() == [0, 0]

    def test_does_not_mutate_input(self, sample_df):
        original_cols = list(sample_df.columns)
        fe = FeatureEngineer()
        fe.transform(sample_df)
        assert list(sample_df.columns) == original_cols


class TestBuildPreprocessor:
    def test_pipeline_fits_and_transforms(self, sample_df):
        pipeline = build_preprocessor()
        transformed = pipeline.fit_transform(sample_df)
        assert transformed.shape[0] == 2
        assert transformed.shape[1] > 0

    def test_handles_unknown_category_gracefully(self, sample_df):
        pipeline = build_preprocessor()
        pipeline.fit(sample_df)
        unseen = sample_df.copy()
        unseen.loc[0, "location"] = "Some New Suburb"
        # Should not raise thanks to handle_unknown="ignore"
        pipeline.transform(unseen)
