import os
import warnings
import numpy as np
import optuna
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from app.utils import save_object, save_json

warnings.filterwarnings("ignore", category=UserWarning)
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")

optuna.logging.set_verbosity(optuna.logging.WARNING)

BASELINE_SAMPLE = 60_000
OPTUNA_SAMPLE = 60_000
OPTUNA_TRIALS = 8


def _get_baseline_models() -> dict:
    return {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(),
        "Lasso": Lasso(),
        "ElasticNet": ElasticNet(),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1, max_depth=20,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100, random_state=42, max_depth=6,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=200, random_state=42, verbosity=0, n_jobs=-1,
        ),
        "LightGBM": LGBMRegressor(
            n_estimators=200, random_state=42, verbose=-1, n_jobs=-1,
        ),
        "CatBoost": CatBoostRegressor(
            iterations=200, random_seed=42, verbose=0,
        ),
    }


def _create_tuned_model(name: str, params: dict):
    if name == "LightGBM":
        return LGBMRegressor(**params, random_state=42, verbose=-1, n_jobs=-1)
    if name == "XGBoost":
        return XGBRegressor(**params, random_state=42, verbosity=0, n_jobs=-1)
    if name == "CatBoost":
        return CatBoostRegressor(**params, random_seed=42, verbose=0)
    if name == "GradientBoosting":
        return GradientBoostingRegressor(**params, random_state=42)
    if name == "RandomForest":
        return RandomForestRegressor(**params, random_state=42, n_jobs=-1)
    raise ValueError(f"Unknown model: {name}")


def _objective(trial, name, X_tr, y_tr, X_te, y_te):
    if name == "LightGBM":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 500),
            "max_depth": trial.suggest_int("max_depth", 4, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 30, 120),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 60),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }
        model = LGBMRegressor(**params, random_state=42, verbose=-1, n_jobs=-1)
    elif name == "XGBoost":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 500),
            "max_depth": trial.suggest_int("max_depth", 4, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }
        model = XGBRegressor(**params, random_state=42, verbosity=0, n_jobs=-1)
    elif name == "CatBoost":
        params = {
            "iterations": trial.suggest_int("iterations", 200, 500),
            "depth": trial.suggest_int("depth", 4, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.15, log=True),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-4, 5.0, log=True),
        }
        model = CatBoostRegressor(**params, random_seed=42, verbose=0)
    elif name == "GradientBoosting":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 300),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
        }
        model = GradientBoostingRegressor(**params, random_state=42)
    elif name == "RandomForest":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 200),
            "max_depth": trial.suggest_int("max_depth", 10, 20),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        }
        model = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
    else:
        return 0.0

    model.fit(X_tr, y_tr)
    score = r2_score(y_te, model.predict(X_te))
    print(f"    trial {trial.number}: R2={score:.4f}", flush=True)
    return score


def _subsample(X, y, n, seed=42):
    if len(X) <= n:
        return X, y
    rng = np.random.RandomState(seed)
    idx = rng.choice(len(X), n, replace=False)
    return X[idx], y[idx]


class ModelTrainer:
    def __init__(self):
        self.model_path = os.path.join(ARTIFACTS_DIR, "model.pkl")
        self.metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")

    def run(self, train_arr: np.ndarray, test_arr: np.ndarray):
        X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
        X_test, y_test = test_arr[:, :-1], test_arr[:, -1]
        n = len(X_train)

        X_base, y_base = _subsample(X_train, y_train, BASELINE_SAMPLE)
        print(f"[ModelTrainer] Using {len(X_base):,} / {n:,} rows for baselines", flush=True)

        # --- Baseline evaluation ---
        print("[ModelTrainer] Training baseline models...", flush=True)
        models = _get_baseline_models()
        results = {}
        for name, model in models.items():
            print(f"  Training {name}...", end="", flush=True)
            model.fit(X_base, y_base)
            preds = model.predict(X_test)
            r2 = r2_score(y_test, preds)
            rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
            mae = float(mean_absolute_error(y_test, preds))
            results[name] = {"r2": round(r2, 5), "rmse": round(rmse, 5), "mae": round(mae, 5)}
            print(f" R2={r2:.4f}  RMSE={rmse:.4f}  MAE={mae:.4f}", flush=True)

        # --- Optuna tuning for top 3 ---
        X_opt, y_opt = _subsample(X_train, y_train, OPTUNA_SAMPLE)
        ranked = sorted(results.items(), key=lambda x: x[1]["r2"], reverse=True)
        top_names = [n for n, _ in ranked[:3]]
        print(f"\n[ModelTrainer] Tuning top 3 ({OPTUNA_TRIALS} trials each, {len(X_opt):,} rows): {top_names}", flush=True)

        best_model = None
        best_score = -np.inf
        best_name = ""
        best_params = {}

        for name in top_names:
            print(f"  Tuning {name}...", end="", flush=True)
            study = optuna.create_study(direction="maximize")
            study.optimize(
                lambda trial, n=name: _objective(trial, n, X_opt, y_opt, X_test, y_test),
                n_trials=OPTUNA_TRIALS,
                show_progress_bar=False,
            )
            bp = study.best_params
            score = study.best_value
            print(f" best_trial_R2={score:.4f}", flush=True)

            if score > best_score:
                best_score = score
                best_name = name
                best_params = bp

        # --- Retrain best on full data ---
        tuned_key = f"{best_name}_tuned"
        print(f"\n[ModelTrainer] Retraining {tuned_key} on full {n:,} rows...", flush=True)
        best_model = _create_tuned_model(best_name, best_params)
        best_model.fit(X_train, y_train)
        preds = best_model.predict(X_test)
        r2 = r2_score(y_test, preds)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        results[tuned_key] = {"r2": round(r2, 5), "rmse": round(rmse, 5), "mae": round(mae, 5)}
        print(f"  {tuned_key:30s} R2={r2:.4f}  RMSE={rmse:.4f}  MAE={mae:.4f}", flush=True)
        best_score = r2

        # --- Cross-validation ---
        print(f"\n[ModelTrainer] Cross-validating {tuned_key}...", flush=True)
        cv_X, cv_y = _subsample(X_train, y_train, 80_000, seed=99)
        cv = cross_val_score(best_model, cv_X, cv_y, cv=5, scoring="r2", n_jobs=-1)
        print(f"  CV R2: {cv.mean():.4f} (+/- {cv.std():.4f})", flush=True)

        # --- Feature importance ---
        importance = None
        if hasattr(best_model, "feature_importances_"):
            importance = [round(float(v), 6) for v in best_model.feature_importances_]

        # --- Persist ---
        save_object(self.model_path, best_model)

        metrics = {
            "best_model": tuned_key,
            "test_r2": round(best_score, 5),
            "test_rmse": results[tuned_key]["rmse"],
            "test_mae": results[tuned_key]["mae"],
            "cv_r2_mean": round(float(cv.mean()), 5),
            "cv_r2_std": round(float(cv.std()), 5),
            "all_results": results,
            "feature_importance": importance,
        }
        save_json(self.metrics_path, metrics)
        print(f"\n[ModelTrainer] Best model: {tuned_key} (R2={best_score:.4f})", flush=True)
        print("[ModelTrainer] Done.", flush=True)
        return best_model, metrics
