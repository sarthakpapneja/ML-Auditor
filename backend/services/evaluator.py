"""
ModelAuditAI — Evaluation Engine
Computes classification and regression metrics.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix
)
from typing import Any


def evaluate_model(model: Any, X: pd.DataFrame, y: pd.Series,
                   task_type: str) -> dict:
    """Evaluate model performance based on task type."""
    try:
        y_pred = model.predict(X.values if hasattr(X, 'values') else X)
    except Exception:
        X_numeric = X.select_dtypes(include=[np.number])
        y_pred = model.predict(X_numeric.values)

    if task_type in ("classifier", "classification"):
        return _classification_metrics(model, X, y, y_pred)
    else:
        return _regression_metrics(y, y_pred)


def _classification_metrics(model: Any, X: pd.DataFrame,
                            y: pd.Series, y_pred: np.ndarray) -> dict:
    """Compute classification metrics."""
    metrics = {
        "task_type": "classification",
        "accuracy": float(accuracy_score(y, y_pred)),
        "f1_score": float(f1_score(y, y_pred, average='weighted', zero_division=0)),
    }

    # ROC-AUC
    try:
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X.values if hasattr(X, 'values') else X)
            if y_proba.shape[1] == 2:
                metrics["roc_auc"] = float(roc_auc_score(y, y_proba[:, 1]))
            else:
                metrics["roc_auc"] = float(
                    roc_auc_score(y, y_proba, multi_class='ovr', average='weighted')
                )
        else:
            metrics["roc_auc"] = None
    except Exception:
        metrics["roc_auc"] = None

    # Confusion matrix
    try:
        cm = confusion_matrix(y, y_pred)
        metrics["confusion_matrix"] = cm.tolist()
    except Exception:
        metrics["confusion_matrix"] = None

    # Classification report
    try:
        report = classification_report(y, y_pred, output_dict=True, zero_division=0)
        metrics["classification_report"] = report
    except Exception:
        metrics["classification_report"] = None

    # Performance score (0-100)
    metrics["performance_score"] = round(
        (metrics["accuracy"] * 0.4 + metrics["f1_score"] * 0.4 +
         (metrics.get("roc_auc") or metrics["accuracy"]) * 0.2) * 100, 2
    )

    return metrics


def _regression_metrics(y: pd.Series, y_pred: np.ndarray) -> dict:
    """Compute regression metrics."""
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
    mae = float(mean_absolute_error(y, y_pred))
    r2 = float(r2_score(y, y_pred))

    # Normalize score to 0-100 (R² can be negative)
    perf_score = max(0, r2) * 100

    return {
        "task_type": "regression",
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "performance_score": round(perf_score, 2),
    }
