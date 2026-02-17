"""
ModelAuditAI — Feature Leakage Detection
Checks for features too correlated with target, ID columns, and future data leakage.
"""
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from typing import Any, Optional


def detect_leakage(model: Any, X: pd.DataFrame, y: pd.Series,
                   task_type: str) -> dict:
    """
    Detect potential feature leakage through:
    1. High correlation with target
    2. ID-like columns
    3. Permutation importance anomalies
    """
    result = {
        "leakage_detected": False,
        "suspicious_features": [],
        "id_columns": [],
        "high_correlation_features": [],
        "permutation_importance": {},
        "leakage_score": 0.0,
        "health_component": 100.0,
        "warnings": [],
        "recommendations": [],
    }

    numeric_X = X.select_dtypes(include=[np.number, bool]).astype(float)

    # --- 1. ID Column Detection ---
    for col in X.columns:
        col_data = X[col]
        # Check if column looks like an ID
        if col_data.nunique() == len(col_data):
            # All unique values — likely an ID
            if col_data.dtype in ['int64', 'int32', 'float64']:
                # Check if monotonically increasing
                if col_data.is_monotonic_increasing or col_data.is_monotonic_decreasing:
                    result["id_columns"].append(col)
                    result["warnings"].append(
                        f"Column '{col}' appears to be an ID column "
                        f"(all unique, monotonic). Remove before training."
                    )
            elif col_data.dtype == 'object':
                result["id_columns"].append(col)
                result["warnings"].append(
                    f"Column '{col}' has all unique string values — likely an ID."
                )

    # Check column names
    id_keywords = ['id', 'index', 'key', 'uuid', 'pk', 'primary_key']
    for col in X.columns:
        col_lower = col.lower().strip()
        if any(kw == col_lower or col_lower.endswith(f"_{kw}") or col_lower.startswith(f"{kw}_")
               for kw in id_keywords):
            if col not in result["id_columns"]:
                result["id_columns"].append(col)
                result["warnings"].append(
                    f"Column '{col}' name suggests it's an identifier."
                )

    # --- 2. High Correlation with Target ---
    try:
        y_numeric = pd.to_numeric(y, errors='coerce')
        if y_numeric.notna().sum() > 0:
            for col in numeric_X.columns:
                corr = abs(float(numeric_X[col].corr(y_numeric)))
                if corr > 0.95:
                    result["high_correlation_features"].append({
                        "feature": col,
                        "correlation": round(corr, 4),
                    })
                    result["warnings"].append(
                        f"Feature '{col}' has extremely high correlation ({corr:.3f}) "
                        f"with target. Possible data leakage."
                    )
    except Exception:
        pass

    # --- 3. Permutation Importance ---
    try:
        scoring = "accuracy" if task_type in ("classifier", "classification") else "r2"
        perm = permutation_importance(
            model, numeric_X.values, y.values,
            n_repeats=5, random_state=42, scoring=scoring
        )

        importances = {}
        for i, col in enumerate(numeric_X.columns):
            imp = float(perm.importances_mean[i])
            importances[col] = round(imp, 4)

            # Suspiciously high importance
            if imp > 0.5:
                result["suspicious_features"].append({
                    "feature": col,
                    "importance": round(imp, 4),
                    "reason": "Unusually high permutation importance"
                })

        result["permutation_importance"] = importances
    except Exception as e:
        result["warnings"].append(f"Could not compute permutation importance: {str(e)}")

    # --- Compute leakage score ---
    n_issues = (
        len(result["id_columns"]) +
        len(result["high_correlation_features"]) * 2 +
        len(result["suspicious_features"])
    )

    if n_issues > 0:
        result["leakage_detected"] = True
        result["leakage_score"] = min(100, n_issues * 20)
        result["health_component"] = max(0, 100 - result["leakage_score"])
        result["recommendations"].append(
            "Review flagged features for potential data leakage. "
            "Remove ID columns and highly correlated features before retraining."
        )
    else:
        result["leakage_score"] = 0
        result["health_component"] = 100.0
        result["recommendations"].append("No obvious feature leakage detected.")

    return result
