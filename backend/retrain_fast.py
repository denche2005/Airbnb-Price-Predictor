"""Fast retrain — skip data download & ingestion, use cached CSVs."""

import sys
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONUNBUFFERED"] = "1"
sys.path.insert(0, os.path.dirname(__file__))

from app.ml.data_transformation import DataTransformation
from app.ml.model_trainer import ModelTrainer

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
TRAIN_PATH = os.path.join(ARTIFACTS_DIR, "train.csv")
TEST_PATH = os.path.join(ARTIFACTS_DIR, "test.csv")


def main():
    print("=" * 60, flush=True)
    print("  Fast Retrain — using cached train/test CSVs", flush=True)
    print("=" * 60, flush=True)

    train_arr, test_arr = DataTransformation().run(TRAIN_PATH, TEST_PATH)
    model, metrics = ModelTrainer().run(train_arr, test_arr)

    print("\n" + "=" * 60, flush=True)
    print("  Training complete!", flush=True)
    print(f"  Best model : {metrics['best_model']}", flush=True)
    print(f"  Test R²    : {metrics['test_r2']}", flush=True)
    print(f"  Test RMSE  : {metrics['test_rmse']}", flush=True)
    print(f"  CV R² mean : {metrics['cv_r2_mean']} ± {metrics['cv_r2_std']}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
