# User Manual — Dashboard

## Accessing the Dashboard

Local run: `http://localhost:8501`
Docker Compose: `http://localhost:8501` (same port, containerized)

## Tab 1: Predict

1. Enter the property's **area** in square feet.
2. Set **bedrooms**, **bathrooms**, and **age** using the sliders.
3. Choose the **location** from the 8 supported Hyderabad micro-markets.
4. Choose the **property type** (Apartment, Independent House, Villa, Studio).
5. Set **floor**, **facing**, and an **amenities score** (0 = basic, 10 = fully
   loaded — clubhouse, gym, pool, security, etc.).
6. Click **Predict Price**.

The result panel shows:
- **Predicted Price** — the model's point estimate in INR
- **90% confidence range** — the band the true price is likely to fall within
- **Model version** — which trained model produced this prediction (useful
  for audit trails and for confirming a new deployment took effect)
- **Inference latency** — how long the prediction took, in milliseconds

## Tab 2: Business Intelligence Dashboard

This tab reads directly from the prediction log and updates automatically as
new predictions are made (by you, other dashboard users, or API callers).

- **Total Predictions** — how many predictions have been served
- **Avg Predicted Price** — the running average across all logged predictions
- **Avg Latency** — running average inference time
- **Active Model Version** — the version tag of the currently deployed model
- **Predicted Price by Location** / **by Property Type** — bar charts to spot
  pricing trends across market segments
- **Recent Predictions** — a table of the 20 most recent predictions, useful
  for spot-checking model behavior

## Tips

- If the dashboard shows "No prediction data yet," make at least one
  prediction in Tab 1 first — the analytics are populated from real usage.
- If predictions fail with a connection error, confirm the backend is running
  and that `API_BASE_URL` points to the right host (see `docs/SETUP.md`).
