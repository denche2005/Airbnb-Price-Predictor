import os
import json
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

KEY_AMENITIES = [
    "Elevator", "Pool", "Hot tub", "Gym", "Doorman",
    "Air conditioning", "Heating", "Washer", "Dryer", "Kitchen",
    "TV", "Wifi", "Free parking on premises", "Indoor fireplace",
    "Patio or balcony", "Breakfast", "Buzzer/wireless intercom",
    "Wheelchair accessible",
]


def _col_name(amenity: str) -> str:
    return "has_" + amenity.lower().replace(" ", "_").replace("/", "_")


def _parse_price(s) -> float:
    """Parse '$1,234.00' -> 1234.0, return NaN on failure."""
    if pd.isna(s):
        return np.nan
    cleaned = re.sub(r"[^\d.]", "", str(s))
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def _parse_pct(s) -> float:
    if pd.isna(s):
        return np.nan
    cleaned = str(s).replace("%", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def _parse_bathrooms_text(s) -> float:
    if pd.isna(s):
        return np.nan
    match = re.search(r"([\d.]+)", str(s))
    if match:
        val = float(match.group(1))
        if "half" in str(s).lower():
            val = 0.5
        return val
    if "half" in str(s).lower():
        return 0.5
    return np.nan


def _parse_amenities_json(s) -> dict:
    """Parse Inside Airbnb JSON amenity array into count + binary flags."""
    result = {"amenities_count": 0}
    for a in KEY_AMENITIES:
        result[_col_name(a)] = 0

    if pd.isna(s):
        return result

    try:
        items = json.loads(s)
    except (json.JSONDecodeError, TypeError):
        items = [i.strip().strip('"') for i in str(s).strip("{}[]").split(",")]

    if not isinstance(items, list):
        return result

    result["amenities_count"] = len(items)
    items_lower = {str(i).lower() for i in items}

    amenity_aliases = {
        "wifi": ["wifi", "wireless internet", "wi-fi"],
        "air conditioning": ["air conditioning", "a/c", "ac"],
        "tv": ["tv", "television"],
        "free parking on premises": ["free parking on premises", "free parking", "free street parking"],
        "patio or balcony": ["patio or balcony", "patio", "balcony"],
        "hot tub": ["hot tub", "jacuzzi"],
        "buzzer/wireless intercom": ["buzzer/wireless intercom", "buzzer", "intercom"],
    }

    for a in KEY_AMENITIES:
        col = _col_name(a)
        aliases = amenity_aliases.get(a.lower(), [a.lower()])
        for alias in aliases:
            if alias in items_lower:
                result[col] = 1
                break

    return result


class DataIngestion:
    def __init__(self):
        self.raw_path = os.path.join(DATA_DIR, "worldwide_listings.csv.gz")
        self.train_path = os.path.join(ARTIFACTS_DIR, "train.csv")
        self.test_path = os.path.join(ARTIFACTS_DIR, "test.csv")

    def run(self) -> tuple[str, str]:
        print("[DataIngestion] Reading worldwide data...", flush=True)
        df = pd.read_csv(self.raw_path, low_memory=False)
        print(f"  Raw shape: {df.shape}", flush=True)
        print(f"  Cities: {df['city'].nunique()} — {sorted(df['city'].unique())}", flush=True)

        # --- Parse price ---
        df["price_numeric"] = df["price"].apply(_parse_price)
        df = df[df["price_numeric"] > 0].copy()
        df = df[df["price_numeric"] < df["price_numeric"].quantile(0.99)]
        df["log_price"] = np.log(df["price_numeric"])
        df.drop(columns=["price", "price_numeric"], inplace=True)

        # --- Parse bathrooms ---
        if "bathrooms_text" in df.columns:
            df["bathrooms"] = df["bathrooms_text"].apply(_parse_bathrooms_text)
            df.drop(columns=["bathrooms_text"], inplace=True, errors="ignore")
        if "bathrooms" not in df.columns:
            df["bathrooms"] = np.nan

        # --- Parse host rates ---
        df["host_response_rate"] = df["host_response_rate"].apply(_parse_pct)
        if "host_acceptance_rate" in df.columns:
            df["host_acceptance_rate"] = df["host_acceptance_rate"].apply(_parse_pct)
        else:
            df["host_acceptance_rate"] = np.nan

        # --- Parse boolean columns ---
        for col in ["host_is_superhost", "instant_bookable"]:
            if col in df.columns:
                df[col] = df[col].map({"t": "t", "f": "f"}).fillna("f")
            else:
                df[col] = "f"

        # --- Parse amenities ---
        amenity_features = df["amenities"].apply(_parse_amenities_json).apply(pd.Series)
        df = pd.concat([df, amenity_features], axis=1)

        # --- Select & clean columns we need ---
        keep_cols = [
            "log_price", "city", "country", "currency",
            "accommodates", "bedrooms", "beds", "bathrooms",
            "latitude", "longitude",
            "amenities_count",
            "host_response_rate", "host_acceptance_rate",
            "number_of_reviews", "reviews_per_month",
            "review_scores_rating", "review_scores_accuracy",
            "review_scores_cleanliness", "review_scores_checkin",
            "review_scores_communication", "review_scores_location",
            "review_scores_value",
            "minimum_nights", "availability_365",
            "calculated_host_listings_count",
            "property_type", "room_type",
            "host_is_superhost", "instant_bookable",
        ] + [_col_name(a) for a in KEY_AMENITIES]

        existing = [c for c in keep_cols if c in df.columns]
        missing = [c for c in keep_cols if c not in df.columns]
        if missing:
            print(f"  Missing columns (will add as NaN): {missing}", flush=True)

        df = df[existing].copy()
        for col in missing:
            df[col] = np.nan

        # --- Ensure numeric types ---
        numeric_should = [
            "accommodates", "bedrooms", "beds", "bathrooms",
            "latitude", "longitude", "amenities_count",
            "host_response_rate", "host_acceptance_rate",
            "number_of_reviews", "reviews_per_month",
            "review_scores_rating", "review_scores_accuracy",
            "review_scores_cleanliness", "review_scores_checkin",
            "review_scores_communication", "review_scores_location",
            "review_scores_value",
            "minimum_nights", "availability_365",
            "calculated_host_listings_count",
        ]
        for col in numeric_should:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # --- Drop rows with missing target ---
        df.dropna(subset=["log_price"], inplace=True)

        print(f"  Clean shape: {df.shape}", flush=True)

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
        train_df.to_csv(self.train_path, index=False)
        test_df.to_csv(self.test_path, index=False)

        print(f"  Train shape: {train_df.shape}", flush=True)
        print(f"  Test shape:  {test_df.shape}", flush=True)
        print(f"  Columns ({len(df.columns)}): {list(df.columns)}", flush=True)
        print("[DataIngestion] Done.", flush=True)
        return self.train_path, self.test_path
