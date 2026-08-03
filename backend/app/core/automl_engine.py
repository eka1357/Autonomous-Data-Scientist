import os
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from xgboost import XGBClassifier, XGBRegressor

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


def detect_problem_type(
    df: pd.DataFrame, target_col: str | None = None, problem_type_override: str | None = None
) -> tuple[str, str | None]:
    if problem_type_override and problem_type_override.lower() in (
        "classification",
        "regression",
        "clustering",
    ):
        return problem_type_override.lower(), target_col

    # Always ensure numeric coercion is performed before inspecting dtypes & cardinality
    from app.core.profiler import clean_and_coerce_numeric_columns
    coerced_df = clean_and_coerce_numeric_columns(df)

    if not target_col or target_col not in coerced_df.columns:
        return "clustering", None

    y = coerced_df[target_col].dropna()
    if y.empty:
        return "clustering", None

    # Continuous numeric with high cardinality -> regression
    if pd.api.types.is_numeric_dtype(y):
        unique_cnt = y.nunique()
        if unique_cnt > 10 or (len(y) > 0 and (unique_cnt / len(y)) > 0.05):
            return "regression", target_col

    return "classification", target_col


def train_automl_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series | pd.DataFrame | None = None,
    y_test: pd.Series | pd.DataFrame | None = None,
    problem_type: str = "classification",
    model_output_path: str = "",
) -> tuple[Any, str, float, str, list[dict[str, Any]]]:
    """
    Trains multiple ML algorithms according to problem_type:
    - Classification: Logistic Regression, Random Forest, XGBoost, LightGBM
    - Regression: Linear Regression, Random Forest Regressor, XGBoost Regressor, LightGBM Regressor
    - Clustering: KMeans, DBSCAN, Agglomerative Clustering

    Compares models, selects the best, saves with joblib, and returns:
    (best_model_obj, best_algorithm_name, best_score, primary_metric, leaderboard)
    """
    leaderboard: list[dict[str, Any]] = []
    best_model_obj = None
    best_algorithm_name = ""
    best_score = -999999.0

    if problem_type == "classification":
        primary_metric = "f1_weighted"
        classifiers = [
            ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
            ("Random Forest", RandomForestClassifier(n_estimators=100, random_state=42)),
            ("XGBoost", XGBClassifier(eval_metric="logloss", random_state=42)),
        ]
        if HAS_LIGHTGBM:
            classifiers.append(("LightGBM", LGBMClassifier(random_state=42, verbose=-1)))
        else:
            classifiers.append(("Gradient Boosting", GradientBoostingClassifier(random_state=42)))

        for name, clf in classifiers:
            try:
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_test)
                
                acc = float(accuracy_score(y_test, y_pred))
                prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
                rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
                f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

                roc_auc = 0.0
                try:
                    if hasattr(clf, "predict_proba"):
                        proba = clf.predict_proba(X_test)
                        if proba.shape[1] == 2:
                            roc_auc = float(roc_auc_score(y_test, proba[:, 1]))
                        else:
                            roc_auc = float(roc_auc_score(y_test, proba, multi_class="ovr", average="weighted"))
                except Exception:
                    roc_auc = 0.0

                metrics = {
                    "accuracy": round(acc, 4),
                    "precision": round(prec, 4),
                    "recall": round(rec, 4),
                    "f1_weighted": round(f1, 4),
                    "roc_auc": round(roc_auc, 4),
                }

                leaderboard.append({
                    "algorithm": name,
                    "status": "completed",
                    "metrics": metrics,
                    "score": round(f1, 4),
                })

                if f1 > best_score:
                    best_score = f1
                    best_algorithm_name = name
                    best_model_obj = clf

            except Exception as e:
                leaderboard.append({
                    "algorithm": name,
                    "status": "failed",
                    "error": f"{type(e).__name__}: {str(e)}",
                    "score": -999999.0,
                })

    elif problem_type == "regression":
        primary_metric = "r2"
        regressors = [
            ("Linear Regression", LinearRegression()),
            ("Random Forest Regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
            ("XGBoost Regressor", XGBRegressor(random_state=42)),
        ]
        if HAS_LIGHTGBM:
            regressors.append(("LightGBM Regressor", LGBMRegressor(random_state=42, verbose=-1)))
        else:
            regressors.append(("Gradient Boosting Regressor", GradientBoostingRegressor(random_state=42)))

        for name, reg in regressors:
            try:
                reg.fit(X_train, y_train)
                y_pred = reg.predict(X_test)

                mae = float(mean_absolute_error(y_test, y_pred))
                mse = float(mean_squared_error(y_test, y_pred))
                rmse = float(np.sqrt(mse))
                r2 = float(r2_score(y_test, y_pred))

                pred_var = float(np.var(y_pred)) if len(y_pred) > 1 else 1.0

                metrics = {
                    "mae": round(mae, 4),
                    "mse": round(mse, 4),
                    "rmse": round(rmse, 4),
                    "r2": round(r2, 4),
                    "pred_variance": round(pred_var, 6),
                }
                if pred_var < 1e-12:
                    metrics["warning"] = "Near-zero variance in predictions detected"

                leaderboard.append({
                    "algorithm": name,
                    "status": "completed",
                    "metrics": metrics,
                    "score": round(r2, 4),
                })

                if r2 > best_score:
                    best_score = r2
                    best_algorithm_name = name
                    best_model_obj = reg

            except Exception as e:
                leaderboard.append({
                    "algorithm": name,
                    "status": "failed",
                    "error": f"{type(e).__name__}: {str(e)}",
                    "score": -999999.0,
                })

    else:  # clustering
        primary_metric = "silhouette_score"
        n_samples = len(X_train)
        n_clusters = min(3, max(2, n_samples - 1)) if n_samples > 2 else 2

        clusterers = [
            ("KMeans", KMeans(n_clusters=n_clusters, random_state=42, n_init=10)),
            ("DBSCAN", DBSCAN(eps=0.5, min_samples=2)),
            ("Agglomerative Clustering", AgglomerativeClustering(n_clusters=n_clusters)),
        ]

        for name, model in clusterers:
            try:
                labels = model.fit_predict(X_train)
                unique_labels = set(labels) - {-1}

                if len(unique_labels) > 1 and len(X_train) > len(unique_labels):
                    sil = float(silhouette_score(X_train, labels))
                    cal = float(calinski_harabasz_score(X_train, labels))
                    dav = float(davies_bouldin_score(X_train, labels))
                else:
                    sil, cal, dav = 0.0, 0.0, 0.0

                metrics = {
                    "silhouette_score": round(sil, 4),
                    "calinski_harabasz_score": round(cal, 4),
                    "davies_bouldin_score": round(dav, 4),
                    "cluster_count": len(set(labels)),
                }

                leaderboard.append({
                    "algorithm": name,
                    "status": "completed",
                    "metrics": metrics,
                    "score": round(sil, 4),
                })

                if sil > best_score or best_model_obj is None:
                    best_score = sil
                    best_algorithm_name = name
                    best_model_obj = model

            except Exception as e:
                leaderboard.append({
                    "algorithm": name,
                    "status": "failed",
                    "error": f"{type(e).__name__}: {str(e)}",
                    "score": -999999.0,
                })

    # Sort leaderboard by score descending
    leaderboard.sort(key=lambda x: x.get("score", -999999.0), reverse=True)

    # Sanity Check: if all models failed or all completed models computed to 0.0 metrics, raise error state
    completed_models = [m for m in leaderboard if m.get("status") == "completed"]
    all_scores_zero = len(completed_models) > 0 and all(m.get("score", 0.0) == 0.0 for m in completed_models)

    if not completed_models or (all_scores_zero and len(completed_models) > 1):
        err_msgs = [f"{m['algorithm']}: {m.get('error', 'Zero score/variance')}" for m in leaderboard]
        raise ValueError(f"AutoML Pipeline Error: All algorithms failed or produced zero metrics. Details: {'; '.join(err_msgs)}")

    # Save best model to disk with joblib if output path provided
    if best_model_obj is not None and model_output_path:
        os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
        joblib.dump(best_model_obj, model_output_path)

    return best_model_obj, best_algorithm_name, round(best_score, 4), primary_metric, leaderboard
