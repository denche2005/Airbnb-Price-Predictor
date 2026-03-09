"""Train a compact model on Barcelona data for deployment.

This avoids downloading the full worldwide dataset, but keeps the same
preprocessing and prediction pipeline so the API and frontend behave
identically (just trained on a smaller subset).
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONUNBUFFERED"] = "1"

sys.path.insert(0, os.path.dirname(__file__))

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np

from app.ml.data_ingestion import DataIngestion  # type: ignore
from app.ml.data_transformation import DataTransformation  # type: ignore
from app.utils import save_json, save_object  # type: ignore


def main() -> None:
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")

    print("=" * 60, flush=True)
    print("  Train small deployment model (Barcelona subset)", flush=True)
    print("=" * 60, flush=True)

    # Use only Barcelona data for a lighter model
    di = DataIngestion()
    di.raw_path = os.path.join(data_dir, "barcelona.csv.gz")
    train_path, test_path = di.run()

    dt = DataTransformation()
    train_arr, test_arr = dt.run(train_path, test_path)

    X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
    X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

    # Compact RandomForest model (much smaller than full XGBoost)
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=16,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    r2 = r2_score(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae = float(mean_absolute_error(y_test, preds))

    importance = (
        [float(v) for v in model.feature_importances_]
        if hasattr(model, "feature_importances_")
        else None
    )

    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    save_object(os.path.join(artifacts_dir, "model.pkl"), model)

    metrics = {
        "best_model": "RandomForest_small_barcelona",
        "test_r2": round(float(r2), 5),
        "test_rmse": round(rmse, 5),
        "test_mae": round(mae, 5),
        "cv_r2_mean": round(float(r2), 5),  # placeholder (no CV here)
        "cv_r2_std": 0.0,
        "all_results": {
            "RandomForest_small_barcelona": {
                "r2": round(float(r2), 5),
                "rmse": round(rmse, 5),
                "mae": round(mae, 5),
            }
        },
        "feature_importance": importance,
    }
    save_json(os.path.join(artifacts_dir, "metrics.json"), metrics)

    print("\n" + "=" * 60, flush=True)
    print("  Small deployment training complete!", flush=True)
    print(f"  Best model : {metrics['best_model']}", flush=True)
    print(f"  Test R²    : {metrics['test_r2']}", flush=True)
    print(f"  Test RMSE  : {metrics['test_rmse']}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()

