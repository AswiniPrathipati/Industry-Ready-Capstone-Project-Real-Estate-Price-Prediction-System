"""
Streamlit frontend: prediction form + business-intelligence dashboard.

Run locally:
    streamlit run frontend/dashboard.py

Talks to the FastAPI backend over HTTP (set API_BASE_URL env var to
override the default when running via docker-compose).
"""
import os
import sqlite3
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DB_PATH = Path(__file__).resolve().parents[1] / "backend" / "database" / "app.db"

st.set_page_config(page_title="Real Estate Price Predictor", page_icon="🏢", layout="wide")

LOCATIONS = ["Banjara Hills", "Gachibowli", "Madhapur", "Kondapur", "Kukatpally", "Miyapur", "Uppal", "LB Nagar"]
PROPERTY_TYPES = ["Apartment", "Independent House", "Villa", "Studio"]
FACING = ["East", "West", "North", "South", "North-East", "South-West"]

st.title("🏢 Real Estate Price Prediction System")
st.caption("Capstone Project — Month 6 · Production ML System")

tab_predict, tab_dashboard = st.tabs(["🔮 Predict", "📊 Business Intelligence Dashboard"])

with tab_predict:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Property Details")
        area = st.number_input("Area (sq. ft.)", min_value=200.0, max_value=10000.0, value=1450.0, step=50.0)
        bedrooms = st.slider("Bedrooms", 1, 6, 3)
        bathrooms = st.slider("Bathrooms", 1, 6, 2)
        age = st.slider("Property Age (years)", 0, 40, 5)
        location = st.selectbox("Location", LOCATIONS)
        property_type = st.selectbox("Property Type", PROPERTY_TYPES)
        floor = st.slider("Floor", 0, 30, 6)
        facing = st.selectbox("Facing", FACING)
        amenities_score = st.slider("Amenities Score (0-10)", 0.0, 10.0, 7.5)

        if st.button("Predict Price", type="primary", use_container_width=True):
            payload = {
                "area": area, "bedrooms": bedrooms, "bathrooms": bathrooms, "age": age,
                "location": location, "property_type": property_type,
                "floor": floor, "facing": facing, "amenities_score": amenities_score,
            }
            try:
                resp = requests.post(f"{API_BASE_URL}/api/v1/predict", json=payload, timeout=10)
                resp.raise_for_status()
                st.session_state["last_prediction"] = resp.json()
            except Exception as e:
                st.error(f"Prediction request failed: {e}")

    with col2:
        st.subheader("Prediction Result")
        result = st.session_state.get("last_prediction")
        if result:
            st.metric("Predicted Price", f"₹{result['predicted_price']:,.0f}")
            ci = result["confidence_interval"]
            st.write(f"**90% confidence range:** ₹{ci['lower_bound']:,.0f} – ₹{ci['upper_bound']:,.0f}")
            st.write(f"**Model version:** `{result['model_version']}`")
            st.write(f"**Inference latency:** {result['latency_ms']:.1f} ms")
        else:
            st.info("Fill in property details and click **Predict Price**.")

with tab_dashboard:
    st.subheader("Live System Analytics")
    if not DB_PATH.exists():
        st.warning("No prediction data yet. Make a few predictions first, or run the backend once.")
    else:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
        conn.close()

        if df.empty:
            st.info("No predictions logged yet.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Predictions", len(df))
            c2.metric("Avg Predicted Price", f"₹{df['predicted_price'].mean():,.0f}")
            c3.metric("Avg Latency", f"{df['latency_ms'].mean():.1f} ms")
            c4.metric("Active Model Version", df['model_version'].iloc[0])

            st.markdown("#### Predicted Price by Location")
            st.bar_chart(df.groupby("location")["predicted_price"].mean())

            st.markdown("#### Predicted Price by Property Type")
            st.bar_chart(df.groupby("property_type")["predicted_price"].mean())

            st.markdown("#### Recent Predictions")
            st.dataframe(
                df[["timestamp", "location", "property_type", "area", "bedrooms", "predicted_price", "latency_ms"]].head(20),
                use_container_width=True,
            )
