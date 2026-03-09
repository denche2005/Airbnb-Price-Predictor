"""Training pipeline — run from the backend/ directory: python -u train.py"""

import sys
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONUNBUFFERED"] = "1"

sys.path.insert(0, os.path.dirname(__file__))

from app.ml.data_ingestion import DataIngestion
from app.ml.data_transformation import DataTransformation
from app.ml.model_trainer import ModelTrainer


def main():
    print("=" * 60, flush=True)
    print("  Worldwide Airbnb Price Predictor — Training Pipeline", flush=True)
    print("=" * 60, flush=True)

    train_path, test_path = DataIngestion().run()
    train_arr, test_arr = DataTransformation().run(train_path, test_path)
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
