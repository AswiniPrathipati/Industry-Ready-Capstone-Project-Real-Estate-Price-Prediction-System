from pydantic import BaseModel, Field, field_validator

VALID_LOCATIONS = {
    "Banjara Hills", "Gachibowli", "Madhapur", "Kondapur",
    "Kukatpally", "Miyapur", "Uppal", "LB Nagar",
}
VALID_PROPERTY_TYPES = {"Apartment", "Independent House", "Villa", "Studio"}
VALID_FACING = {"East", "West", "North", "South", "North-East", "South-West"}


class PropertyRequest(BaseModel):
    area: float = Field(..., gt=0, le=20000, description="Built-up area in sq. ft.")
    bedrooms: int = Field(..., ge=1, le=10)
    bathrooms: int = Field(..., ge=1, le=10)
    age: int = Field(..., ge=0, le=100, description="Property age in years")
    location: str
    property_type: str
    floor: int = Field(1, ge=0, le=100)
    facing: str = "East"
    amenities_score: float = Field(5.0, ge=0, le=10)

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if v not in VALID_LOCATIONS:
            raise ValueError(f"location must be one of {sorted(VALID_LOCATIONS)}")
        return v

    @field_validator("property_type")
    @classmethod
    def validate_property_type(cls, v):
        if v not in VALID_PROPERTY_TYPES:
            raise ValueError(f"property_type must be one of {sorted(VALID_PROPERTY_TYPES)}")
        return v

    @field_validator("facing")
    @classmethod
    def validate_facing(cls, v):
        if v not in VALID_FACING:
            raise ValueError(f"facing must be one of {sorted(VALID_FACING)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "area": 1450,
                "bedrooms": 3,
                "bathrooms": 2,
                "age": 5,
                "location": "Gachibowli",
                "property_type": "Apartment",
                "floor": 6,
                "facing": "East",
                "amenities_score": 7.5,
            }
        }


class BatchPropertyRequest(BaseModel):
    properties: list[PropertyRequest] = Field(..., max_length=100)


class ConfidenceInterval(BaseModel):
    lower_bound: float
    upper_bound: float


class PredictionResponse(BaseModel):
    prediction_id: str
    timestamp: str
    predicted_price: float
    currency: str
    confidence_interval: ConfidenceInterval
    model_version: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    timestamp: str


class MetricsResponse(BaseModel):
    total_predictions: int
    avg_latency_ms: float | None
    avg_predicted_price: float | None
    model_version: str
    model_r2: float | None
    model_mae: float | None
