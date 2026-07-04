"""
Synthetic real-estate data generator.

Simulates the output of the production data-collection layer (multiple
listing-site APIs + municipal records) described in the architecture doc.
A fixed random seed keeps the dataset reproducible for grading /
CI purposes while still exhibiting realistic, non-linear price behaviour.
"""
import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
N_RECORDS = 6000

LOCATIONS = {
    # location: (base_price_per_sqft, demand_multiplier)
    "Banjara Hills": (9500, 1.35),
    "Gachibowli": (7200, 1.25),
    "Madhapur": (6800, 1.20),
    "Kondapur": (5600, 1.10),
    "Kukatpally": (4800, 1.00),
    "Miyapur": (4200, 0.95),
    "Uppal": (3600, 0.85),
    "LB Nagar": (3400, 0.80),
}
PROPERTY_TYPES = {
    "Apartment": 1.00,
    "Independent House": 1.10,
    "Villa": 1.35,
    "Studio": 0.85,
}
FACING = ["East", "West", "North", "South", "North-East", "South-West"]


def generate_dataset(n_records: int = N_RECORDS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    locations = rng.choice(list(LOCATIONS.keys()), size=n_records)
    property_types = rng.choice(list(PROPERTY_TYPES.keys()), size=n_records, p=[0.55, 0.20, 0.10, 0.15])

    area = rng.normal(1400, 550, n_records).clip(300, 6000)
    bedrooms = rng.choice([1, 2, 3, 4, 5], size=n_records, p=[0.12, 0.35, 0.32, 0.15, 0.06])
    bathrooms = np.clip(bedrooms - rng.integers(0, 2, n_records), 1, None)
    age = rng.integers(0, 35, n_records)
    floor = rng.integers(0, 25, n_records)
    facing = rng.choice(FACING, size=n_records)
    amenities_score = rng.uniform(0, 10, n_records)  # 0-10 composite amenity index

    rows = []
    for i in range(n_records):
        base_ppsf, demand = LOCATIONS[locations[i]]
        type_mult = PROPERTY_TYPES[property_types[i]]

        price = area[i] * base_ppsf * type_mult * demand
        price *= (1 - 0.006 * age[i])                      # depreciation
        price *= (1 + 0.01 * min(floor[i], 15))             # higher floors, modest premium
        price *= (1 + 0.015 * amenities_score[i])           # amenities premium
        price *= (1 + 0.03 * (bedrooms[i] - 2))             # bedroom premium/discount
        price *= rng.normal(1.0, 0.07)                      # market noise

        rows.append(
            {
                "area": round(float(area[i]), 1),
                "bedrooms": int(bedrooms[i]),
                "bathrooms": int(bathrooms[i]),
                "age": int(age[i]),
                "location": locations[i],
                "property_type": property_types[i],
                "floor": int(floor[i]),
                "facing": facing[i],
                "amenities_score": round(float(amenities_score[i]), 2),
                "price": round(max(price, 150000), 2),
            }
        )

    df = pd.DataFrame(rows)
    return df


def main():
    out_dir = Path(__file__).resolve().parent
    df = generate_dataset()
    out_path = out_dir / "real_estate_data.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} records -> {out_path}")
    print(df.describe(include="all").T)


if __name__ == "__main__":
    main()
