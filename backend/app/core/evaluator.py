from typing import Any
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


def evaluate_trained_model(
    model: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series | pd.DataFrame | None = None,
    y_test: pd.Series | pd.DataFrame | None = None,
    problem_type: str = "classification",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Evaluates a trained model:
    - Accuracy, Precision, Recall, F1, ROC AUC, Confusion Matrix (Classification)
    - MAE, MSE, RMSE, R² (Regression)
    - 5-fold Cross Validation
    - Feature Importance (MDI / coefs)
    - SHAP values summary

    Returns:
    (metrics_dict, feature_importance_dict, shap_values_dict)
    """
    metrics: dict[str, Any] = {}
    feature_importance: dict[str, float] = {}
    shap_summary: dict[str, float] = {}

    feature_names = list(X_test.columns)

    # 1. Feature Importance extraction
    if hasattr(model, "feature_importances_"):
        fi_vals = model.feature_importances_
        feature_importance = {
            col: round(float(val), 4) for col, val in zip(feature_names, fi_vals)
        }
    elif hasattr(model, "coef_"):
        coef_vals = np.abs(model.coef_).ravel()
        if len(coef_vals) == len(feature_names):
            feature_importance = {
                col: round(float(val), 4) for col, val in zip(feature_names, coef_vals)
            }

    # 2. Metric Calculations
    if problem_type == "classification" and y_test is not None:
        y_pred = model.predict(X_test)
        
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        roc_auc = 0.0
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X_test)
                if proba.shape[1] == 2:
                    roc_auc = float(roc_auc_score(y_test, proba[:, 1]))
                else:
                    roc_auc = float(roc_auc_score(y_test, proba, multi_class="ovr", average="weighted"))
        except Exception:
            roc_auc = 0.0

        # Cross Validation
        cv_scores: list[float] = []
        if y_train is not None and len(X_train) >= 5:
            try:
                cvs = cross_val_score(model, X_train, y_train, cv=min(5, len(X_train)), scoring="f1_weighted")
                cv_scores = [round(float(s), 4) for s in cvs]
            except Exception:
                cv_scores = []

        metrics = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": cm,
            "cross_validation": {
                "folds": cv_scores,
                "mean": round(float(np.mean(cv_scores)), 4) if cv_scores else round(f1, 4),
                "std": round(float(np.std(cv_scores)), 4) if cv_scores else 0.0,
            },
        }

    elif problem_type == "regression" and y_test is not None:
        y_pred = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, y_pred))
        mse = float(mean_squared_error(y_test, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_test, y_pred))

        # Cross Validation
        cv_scores = []
        if y_train is not None and len(X_train) >= 5:
            try:
                cvs = cross_val_score(model, X_train, y_train, cv=min(5, len(X_train)), scoring="r2")
                cv_scores = [round(float(s), 4) for s in cvs]
            except Exception:
                cv_scores = []

        metrics = {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "cross_validation": {
                "folds": cv_scores,
                "mean": round(float(np.mean(cv_scores)), 4) if cv_scores else round(r2, 4),
                "std": round(float(np.std(cv_scores)), 4) if cv_scores else 0.0,
            },
        }

    else:  # clustering or unsupervised evaluation
        labels = model.fit_predict(X_test) if hasattr(model, "fit_predict") else model.labels_
        metrics = {
            "cluster_count": len(set(labels)),
            "sample_count": len(X_test),
        }

    # 3. SHAP Values Computation
    if HAS_SHAP and problem_type in ("classification", "regression") and not X_test.empty:
        try:
            sample_size = min(100, len(X_test))
            sample_X = X_test.iloc[:sample_size].copy()

            for col in sample_X.columns:
                sample_X[col] = pd.to_numeric(sample_X[col], errors="coerce").fillna(0.0)

            model_name = type(model).__name__
            if hasattr(model, "tree_") or any(k in model_name for k in ["Forest", "XGB", "LGBM", "Boosting", "Tree"]):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(sample_X)
            elif "Linear" in model_name or "Logistic" in model_name:
                explainer = shap.LinearExplainer(model, sample_X)
                shap_vals = explainer.shap_values(sample_X)
            else:
                explainer = shap.Explainer(model, sample_X)
                shap_result = explainer(sample_X)
                shap_vals = getattr(shap_result, "values", shap_result)

            if isinstance(shap_vals, list):
                shap_matrix = np.mean([np.abs(np.array(v)) for v in shap_vals], axis=0)
            elif isinstance(shap_vals, np.ndarray):
                shap_matrix = np.abs(shap_vals).mean(axis=2) if shap_vals.ndim == 3 else np.abs(shap_vals)
            else:
                shap_matrix = None

            if shap_matrix is not None and shap_matrix.ndim == 2 and shap_matrix.shape[1] == len(feature_names):
                mean_abs_shap = shap_matrix.mean(axis=0)
                shap_summary = {
                    col: round(float(val), 4) for col, val in zip(feature_names, mean_abs_shap)
                }
        except Exception:
            shap_summary = feature_importance

    if not shap_summary and feature_importance:
        shap_summary = feature_importance

    return metrics, feature_importance, shap_summary
