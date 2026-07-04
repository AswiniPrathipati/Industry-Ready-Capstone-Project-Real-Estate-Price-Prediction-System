import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.append(str(Path(__file__).resolve().parents[1]))
from backend.api.schemas import PropertyRequest  # noqa: E402

VALID_PAYLOAD = {
    "area": 1450, "bedrooms": 3, "bathrooms": 2, "age": 5,
    "location": "Gachibowli", "property_type": "Apartment",
    "floor": 6, "facing": "East", "amenities_score": 7.5,
}


def test_valid_payload_parses():
    req = PropertyRequest(**VALID_PAYLOAD)
    assert req.area == 1450


@pytest.mark.parametrize("field,value", [
    ("area", -10),
    ("area", 0),
    ("bedrooms", 0),
    ("bathrooms", -1),
    ("age", -5),
])
def test_invalid_numeric_fields_rejected(field, value):
    payload = {**VALID_PAYLOAD, field: value}
    with pytest.raises(ValidationError):
        PropertyRequest(**payload)


def test_invalid_location_rejected():
    payload = {**VALID_PAYLOAD, "location": "Atlantis"}
    with pytest.raises(ValidationError):
        PropertyRequest(**payload)


def test_invalid_property_type_rejected():
    payload = {**VALID_PAYLOAD, "property_type": "Castle"}
    with pytest.raises(ValidationError):
        PropertyRequest(**payload)


def test_defaults_applied():
    minimal = {
        "area": 1000, "bedrooms": 2, "bathrooms": 1, "age": 2,
        "location": "Miyapur", "property_type": "Studio",
    }
    req = PropertyRequest(**minimal)
    assert req.floor == 1
    assert req.facing == "East"
    assert req.amenities_score == 5.0
