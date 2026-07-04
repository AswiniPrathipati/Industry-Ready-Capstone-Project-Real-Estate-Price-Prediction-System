import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))
from backend.main import app  # noqa: E402

client = TestClient(app)

VALID_PAYLOAD = {
    "area": 1450, "bedrooms": 3, "bathrooms": 2, "age": 5,
    "location": "Gachibowli", "property_type": "Apartment",
    "floor": 6, "facing": "East", "amenities_score": 7.5,
}


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "service" in resp.json()


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"healthy", "degraded"}
    assert "model_version" in body


def test_predict_success():
    resp = client.post("/api/v1/predict", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()
    assert body["predicted_price"] > 0
    assert body["confidence_interval"]["lower_bound"] < body["predicted_price"]
    assert body["confidence_interval"]["upper_bound"] > body["predicted_price"]


def test_predict_rejects_invalid_area():
    payload = {**VALID_PAYLOAD, "area": -100}
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 422


def test_predict_rejects_invalid_location():
    payload = {**VALID_PAYLOAD, "location": "Nowhere"}
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 422


def test_batch_prediction():
    resp = client.post("/api/v1/batch", json={"properties": [VALID_PAYLOAD, VALID_PAYLOAD]})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2


def test_batch_rejects_over_limit():
    resp = client.post("/api/v1/batch", json={"properties": [VALID_PAYLOAD] * 101})
    assert resp.status_code == 422


def test_metrics_endpoint():
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_predictions" in body


def test_prometheus_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text


def test_reload_model_endpoint():
    resp = client.post("/api/v1/reload-model")
    assert resp.status_code == 200
    assert resp.json()["status"] == "reloaded"


@pytest.mark.parametrize("area,bedrooms,location", [
    (500, 1, "Uppal"),
    (5000, 6, "Banjara Hills"),
    (900, 2, "LB Nagar"),
])
def test_predict_across_property_range(area, bedrooms, location):
    payload = {**VALID_PAYLOAD, "area": area, "bedrooms": bedrooms, "location": location}
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200
    assert resp.json()["predicted_price"] > 0
