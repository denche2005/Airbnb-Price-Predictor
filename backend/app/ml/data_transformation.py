import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

from app.utils import save_object

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")

AMENITY_FEATURES = [
    "has_elevator", "has_pool", "has_hot_tub", "has_gym", "has_doorman",
    "has_air_conditioning", "has_heating", "has_washer", "has_dryer",
    "has_kitchen", "has_tv", "has_wifi",
    "has_free_parking_on_premises", "has_indoor_fireplace",
    "has_patio_or_balcony", "has_breakfast",
    "has_buzzer_wireless_intercom", "has_wheelchair_accessible",
]

NUMERICAL_COLS = [
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
    "rooms_per_person", "beds_per_room", "bath_per_room",
] + AMENITY_FEATURES

CATEGORICAL_COLS = [
    "property_type", "room_type",
    "city", "country",
    "host_is_superhost", "instant_bookable",
]

ALL_FEATURE_NAMES = NUMERICAL_COLS + CATEGORICAL_COLS

TARGET = "log_price"

CITIES = [
    "Amsterdam", "Athens", "Bangkok", "Barcelona", "Berlin",
    "Buenos Aires", "Cape Town", "Chicago", "Hong Kong", "Lisbon",
    "London", "Los Angeles", "Madrid", "Melbourne", "Mexico City",
    "New York", "Paris", "Prague", "Rome", "San Francisco",
    "Singapore", "Sydney", "Tokyo", "Vienna",
]

COUNTRIES = [
    "Argentina", "Australia", "Austria", "China", "Czech Republic",
    "France", "Germany", "Greece", "Italy", "Japan", "Mexico",
    "Netherlands", "Portugal", "Singapore", "South Africa", "Spain",
    "Thailand", "United Kingdom", "United States",
]

CITY_CURRENCY = {
    "Amsterdam": "EUR", "Athens": "EUR", "Bangkok": "THB",
    "Barcelona": "EUR", "Berlin": "EUR", "Buenos Aires": "ARS",
    "Cape Town": "ZAR", "Chicago": "USD", "Hong Kong": "HKD",
    "Lisbon": "EUR", "London": "GBP", "Los Angeles": "USD",
    "Madrid": "EUR", "Melbourne": "AUD", "Mexico City": "MXN",
    "New York": "USD", "Paris": "EUR", "Prague": "CZK",
    "Rome": "EUR", "San Francisco": "USD", "Singapore": "SGD",
    "Sydney": "AUD", "Tokyo": "JPY", "Vienna": "EUR",
}

CITY_COORDS = {
    "Amsterdam": (52.3676, 4.9041), "Athens": (37.9838, 23.7275),
    "Bangkok": (13.7563, 100.5018), "Barcelona": (41.3874, 2.1686),
    "Berlin": (52.52, 13.405), "Buenos Aires": (-34.6037, -58.3816),
    "Cape Town": (-33.9249, 18.4241), "Chicago": (41.8781, -87.6298),
    "Hong Kong": (22.3193, 114.1694), "Lisbon": (38.7223, -9.1393),
    "London": (51.5074, -0.1278), "Los Angeles": (34.0522, -118.2437),
    "Madrid": (40.4168, -3.7038), "Melbourne": (-37.8136, 144.9631),
    "Mexico City": (19.4326, -99.1332), "New York": (40.7128, -74.006),
    "Paris": (48.8566, 2.3522), "Prague": (50.0755, 14.4378),
    "Rome": (41.9028, 12.4964), "San Francisco": (37.7749, -122.4194),
    "Singapore": (1.3521, 103.8198), "Sydney": (-33.8688, 151.2093),
    "Tokyo": (35.6762, 139.6503), "Vienna": (48.2082, 16.3738),
}

CURRENCY_SYMBOL = {
    "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "AUD": "A$",
    "JPY": "\u00a5", "THB": "\u0e3f", "SGD": "S$", "HKD": "HK$",
    "CZK": "K\u010d", "MXN": "MX$", "ARS": "AR$", "ZAR": "R",
}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    safe_accommodates = df["accommodates"].replace(0, 1).fillna(1)
    safe_bedrooms = df["bedrooms"].replace(0, 1).fillna(1)
    df["rooms_per_person"] = df["bedrooms"].fillna(0) / safe_accommodates
    df["beds_per_room"] = df["beds"].fillna(0) / safe_bedrooms
    df["bath_per_room"] = df["bathrooms"].fillna(0) / safe_bedrooms

    for col in AMENITY_FEATURES:
        if col not in df.columns:
            df[col] = 0

    return df


class DataTransformation:
    def __init__(self):
        self.preprocessor_path = os.path.join(ARTIFACTS_DIR, "preprocessor.pkl")

    def _build_preprocessor(self) -> ColumnTransformer:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            )),
            ("scaler", StandardScaler()),
        ])

        return ColumnTransformer([
            ("num", num_pipeline, NUMERICAL_COLS),
            ("cat", cat_pipeline, CATEGORICAL_COLS),
        ])

    def run(self, train_path: str, test_path: str):
        print("[DataTransformation] Loading splits...", flush=True)
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        train_df = engineer_features(train_df)
        test_df = engineer_features(test_df)

        X_train = train_df.drop(columns=[TARGET, "currency"], errors="ignore")
        y_train = train_df[TARGET].values
        X_test = test_df.drop(columns=[TARGET, "currency"], errors="ignore")
        y_test = test_df[TARGET].values

        preprocessor = self._build_preprocessor()
        X_train_arr = preprocessor.fit_transform(X_train)
        X_test_arr = preprocessor.transform(X_test)

        save_object(self.preprocessor_path, preprocessor)
        save_object(
            os.path.join(ARTIFACTS_DIR, "feature_names.pkl"),
            ALL_FEATURE_NAMES,
        )

        train_arr = np.c_[X_train_arr, y_train]
        test_arr = np.c_[X_test_arr, y_test]

        print(f"  Features: {len(ALL_FEATURE_NAMES)} ({len(NUMERICAL_COLS)} num + {len(CATEGORICAL_COLS)} cat)", flush=True)
        print(f"  Train array: {train_arr.shape}", flush=True)
        print(f"  Test array:  {test_arr.shape}", flush=True)
        print("[DataTransformation] Done.", flush=True)
        return train_arr, test_arr
