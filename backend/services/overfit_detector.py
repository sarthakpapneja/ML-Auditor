"""
ModelAuditAI — Overfitting Detection
Compares train vs test performance and runs cross-validation.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, r2_score
from typing import Any


def detect_overfitting(model: Any, X: pd.DataFrame, y: pd.Series,
                       task_type: str) -> dict:
    """
    Detect overfitting by comparing train/test splits and cross-validation.
    Returns overfit score (0-100) and warning level.
    """
    X_vals = X.select_dtypes(include=[np.number, bool]).astype(float).values
    y_vals = y.values

    result = {
        "overfit_detected": False,
        "overfit_score": 0.0,
        "warning_level": "none",
        "train_score": None,
        "test_score": None,
        "cv_scores": None,
        "cv_mean": None,
        "cv_std": None,
        "gap": 0.0,
        "details": "",
    }

    scoring = "accuracy" if task_type in ("classifier", "classification") else "r2"

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_vals, y_vals, test_size=0.2, random_state=42
        )

        # Train score
        if scoring == "accuracy":
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            train_score = float(accuracy_score(y_train, train_pred))
            test_score = float(accuracy_score(y_test, test_pred))
        else:
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            train_score = float(r2_score(y_train, train_pred))
            test_score = float(r2_score(y_test, test_pred))

        result["train_score"] = round(train_score, 4)
        result["test_score"] = round(test_score, 4)
        result["gap"] = round(train_score - test_score, 4)

        # Cross-validation
        try:
            cv_scores = cross_val_score(model, X_vals, y_vals, cv=5,
                                        scoring=scoring)
            result["cv_scores"] = [round(float(s), 4) for s in cv_scores]
            result["cv_mean"] = round(float(cv_scores.mean()), 4)
            result["cv_std"] = round(float(cv_scores.std()), 4)
        except Exception:
            # Some models may not support refitting for CV
            result["cv_scores"] = None
            result["cv_mean"] = None
            result["cv_std"] = None

        # Compute overfit score
        gap = train_score - test_score
        if gap > 0.15:
            result["overfit_detected"] = True
            result["warning_level"] = "high"
            result["overfit_score"] = min(100, round(gap * 200, 2))
            result["details"] = (
                f"Significant overfitting detected. Train score ({train_score:.3f}) "
                f"is much higher than test score ({test_score:.3f}). "
                f"Gap: {gap:.3f}. Consider regularization or more training data."
            )
        elif gap > 0.05:
            result["overfit_detected"] = True
            result["warning_level"] = "medium"
            result["overfit_score"] = round(gap * 150, 2)
            result["details"] = (
                f"Moderate overfitting detected. Train ({train_score:.3f}) vs "
                f"test ({test_score:.3f}). Gap: {gap:.3f}. Monitor closely."
            )
        else:
            result["warning_level"] = "low"
            result["overfit_score"] = max(0, round(gap * 100, 2))
            result["details"] = (
                f"No significant overfitting. Train ({train_score:.3f}) vs "
                f"test ({test_score:.3f}). Gap: {gap:.3f}."
            )

        # Invert for health: low overfit = high health  
        result["health_component"] = round(max(0, 100 - result["overfit_score"]), 2)

    except Exception as e:
        result["details"] = f"Could not perform overfitting analysis: {str(e)}"
        result["health_component"] = 50.0

    return result
