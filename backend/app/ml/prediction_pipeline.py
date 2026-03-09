import os
import numpy as np
import pandas as pd

from app.utils import load_object, load_json
from app.ml.data_transformation import (
    engineer_features, ALL_FEATURE_NAMES, AMENITY_FEATURES,
    CITY_CURRENCY, CITY_COORDS, CURRENCY_SYMBOL, CITIES,
)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")

_model = None
_preprocessor = None
_metrics = None


def _load_artifacts():
    global _model, _preprocessor, _metrics
    if _model is None:
        _model = load_object(os.path.join(ARTIFACTS_DIR, "model.pkl"))
        _preprocessor = load_object(os.path.join(ARTIFACTS_DIR, "preprocessor.pkl"))
        try:
            _metrics = load_json(os.path.join(ARTIFACTS_DIR, "metrics.json"))
        except FileNotFoundError:
            _metrics = {}


def predict(features: dict) -> dict:
    _load_artifacts()

    city = str(features.get("city", "New York"))
    country = str(features.get("country", "United States"))
    currency = CITY_CURRENCY.get(city, "USD")
    coords = CITY_COORDS.get(city, (40.7128, -74.006))

    row = {
        "property_type": str(features.get("property_type", "Entire rental unit")),
        "room_type": str(features.get("room_type", "Entire home/apt")),
        "city": city,
        "country": country,
        "accommodates": int(features.get("accommodates", 2)),
        "bedrooms": float(features.get("bedrooms", 1)),
        "beds": float(features.get("beds", 1)),
        "bathrooms": float(features.get("bathrooms", 1.0)),
        "latitude": float(features.get("latitude", coords[0])),
        "longitude": float(features.get("longitude", coords[1])),
        "amenities_count": int(features.get("amenities_count", 20)),
        "host_response_rate": float(features.get("host_response_rate", 90)),
        "host_acceptance_rate": float(features.get("host_acceptance_rate", 85)),
        "number_of_reviews": int(features.get("number_of_reviews", 10)),
        "reviews_per_month": float(features.get("reviews_per_month", 1.5)),
        "review_scores_rating": float(features.get("review_scores_rating", 4.5)),
        "review_scores_accuracy": float(features.get("review_scores_accuracy", 4.5)),
        "review_scores_cleanliness": float(features.get("review_scores_cleanliness", 4.5)),
        "review_scores_checkin": float(features.get("review_scores_checkin", 4.5)),
        "review_scores_communication": float(features.get("review_scores_communication", 4.5)),
        "review_scores_location": float(features.get("review_scores_location", 4.5)),
        "review_scores_value": float(features.get("review_scores_value", 4.5)),
        "minimum_nights": int(features.get("minimum_nights", 2)),
        "availability_365": int(features.get("availability_365", 200)),
        "calculated_host_listings_count": int(features.get("calculated_host_listings_count", 1)),
        "host_is_superhost": str(features.get("host_is_superhost", "f")),
        "instant_bookable": str(features.get("instant_bookable", "f")),
    }

    for af in AMENITY_FEATURES:
        row[af] = int(features.get(af, 0))

    df = pd.DataFrame([row])
    df = engineer_features(df)
    scaled = _preprocessor.transform(df)
    log_price = float(_model.predict(scaled)[0])
    price = round(np.exp(log_price), 2)

    rmse = _metrics.get("test_rmse", 0.4)
    low = round(np.exp(log_price - 1.96 * rmse), 2)
    high = round(np.exp(log_price + 1.96 * rmse), 2)

    feature_names = ALL_FEATURE_NAMES
    importance = _metrics.get("feature_importance")
    fi_pairs = []
    if importance and len(importance) == len(feature_names):
        fi_pairs = sorted(
            zip(feature_names, importance), key=lambda x: x[1], reverse=True
        )

    return {
        "predicted_price": price,
        "log_price": round(log_price, 4),
        "confidence_low": low,
        "confidence_high": high,
        "currency": currency,
        "currency_symbol": CURRENCY_SYMBOL.get(currency, currency),
        "city": city,
        "feature_importance": [
            {"feature": n, "importance": round(v, 4)} for n, v in fi_pairs[:15]
        ],
        "model_name": _metrics.get("best_model", "unknown"),
    }


def get_city_info():
    return {
        "cities": CITIES,
        "city_currency": CITY_CURRENCY,
        "city_coords": CITY_COORDS,
        "currency_symbols": CURRENCY_SYMBOL,
    }
