"""Train a smaller model on sample_bcn.csv.gz (for Render deployment).

Uses the existing DataIngestion/DataTransformation/ModelTrainer pipeline but
points it to backend/data/sample_bcn.csv.gz instead of the full worldwide
dataset, so training is much faster and lighter.
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONUNBUFFERED"] = "1"

sys.path.insert(0, os.path.dirname(__file__))

from app.ml.data_ingestion import DataIngestion  # type: ignore
from app.ml.data_transformation import DataTransformation  # type: ignore
from app.ml.model_trainer import ModelTrainer  # type: ignore


def main() -> None:
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")

    print("=" * 60, flush=True)
    print("  Train sample model for Render deployment", flush=True)
    print("=" * 60, flush=True)

    # Reuse the existing DataIngestion pipeline but point it to sample_bcn.csv.gz
    di = DataIngestion()
    di.raw_path = os.path.join(data_dir, "sample_bcn.csv.gz")
    train_path, test_path = di.run()

    train_arr, test_arr = DataTransformation().run(train_path, test_path)
    model, metrics = ModelTrainer().run(train_arr, test_arr)

    print("\n" + "=" * 60, flush=True)
    print("  Sample training complete!", flush=True)
    print(f"  Best model : {metrics['best_model']}", flush=True)
    print(f"  Test R²    : {metrics['test_r2']}", flush=True)
    print(f"  Test RMSE  : {metrics['test_rmse']}", flush=True)
    print(f"  CV R² mean : {metrics['cv_r2_mean']} ± {metrics['cv_r2_std']}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()

