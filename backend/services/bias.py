"""
ModelAuditAI — Bias & Fairness Detection
Detects sensitive features and computes fairness metrics.
"""
import numpy as np
import pandas as pd
from typing import Any, Optional


SENSITIVE_KEYWORDS = [
    "gender", "sex", "race", "ethnicity", "age", "religion",
    "nationality", "disability", "marital", "region", "country",
    "color", "orientation", "pregnant"
]


def detect_sensitive_columns(df: pd.DataFrame) -> list[str]:
    """Auto-detect columns that may contain sensitive attributes."""
    sensitive = []
    for col in df.columns:
        col_lower = col.lower().strip()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in col_lower:
                sensitive.append(col)
                break
    return sensitive


def compute_fairness_metrics(model: Any, X: pd.DataFrame, y: pd.Series,
                             sensitive_columns: list[str],
                             task_type: str) -> dict:
    """
    Compute fairness metrics including demographic parity,
    equal opportunity, and disparate impact.
    """
    results = {
        "sensitive_columns_found": sensitive_columns,
        "metrics_by_column": {},
        "overall_fairness_score": 100.0,
        "warnings": [],
    }

    if not sensitive_columns:
        results["warnings"].append("No sensitive columns detected. Fairness analysis skipped.")
        results["overall_fairness_score"] = 100.0
        return results

    try:
        X_numeric = X.select_dtypes(include=[np.number])
        y_pred = model.predict(X_numeric.values)
    except Exception as e:
        results["warnings"].append(f"Could not generate predictions: {str(e)}")
        results["overall_fairness_score"] = 50.0
        return results

    is_classification = task_type in ("classifier", "classification")
    fairness_scores = []

    for col in sensitive_columns:
        if col not in X.columns:
            continue

        col_data = X[col]
        groups = col_data.unique()

        if len(groups) > 20:
            results["warnings"].append(
                f"Column '{col}' has too many unique values ({len(groups)}). "
                f"Skipping detailed fairness analysis."
            )
            continue

        group_metrics = {}
        positive_rates = {}

        for group in groups:
            mask = col_data == group
            group_size = int(mask.sum())

            if group_size < 5:
                continue

            group_y_true = y[mask].values
            group_y_pred = y_pred[mask]

            if is_classification:
                positive_rate = float(np.mean(group_y_pred == 1)) if len(np.unique(y_pred)) <= 2 \
                    else float(np.mean(group_y_pred == group_y_pred.max()))
                
                # True positive rate (equal opportunity)
                true_positives = np.sum((group_y_pred == 1) & (group_y_true == 1)) \
                    if len(np.unique(y_pred)) <= 2 else 0
                actual_positives = np.sum(group_y_true == 1) if len(np.unique(y)) <= 2 else 1
                tpr = float(true_positives / max(actual_positives, 1))
                
                accuracy = float(np.mean(group_y_pred == group_y_true))

                group_metrics[str(group)] = {
                    "size": group_size,
                    "positive_rate": round(positive_rate, 4),
                    "true_positive_rate": round(tpr, 4),
                    "accuracy": round(accuracy, 4),
                }
                positive_rates[str(group)] = positive_rate
            else:
                mean_pred = float(np.mean(group_y_pred))
                group_metrics[str(group)] = {
                    "size": group_size,
                    "mean_prediction": round(mean_pred, 4),
                }
                positive_rates[str(group)] = mean_pred

        # Compute demographic parity & disparate impact
        if len(positive_rates) >= 2:
            rates = list(positive_rates.values())
            max_rate = max(rates) if max(rates) > 0 else 1
            min_rate = min(rates)

            demographic_parity_diff = round(max(rates) - min(rates), 4)
            disparate_impact = round(min_rate / max_rate, 4) if max_rate > 0 else 0.0

            col_fairness = disparate_impact * 100  # 0-100

            column_result = {
                "groups": group_metrics,
                "demographic_parity_difference": demographic_parity_diff,
                "disparate_impact_ratio": disparate_impact,
                "fairness_score": round(col_fairness, 2),
            }

            if disparate_impact < 0.8:
                results["warnings"].append(
                    f"Potential bias detected in '{col}': disparate impact ratio "
                    f"({disparate_impact:.3f}) is below 0.8 threshold."
                )

            results["metrics_by_column"][col] = column_result
            fairness_scores.append(col_fairness)

    if fairness_scores:
        results["overall_fairness_score"] = round(np.mean(fairness_scores), 2)
    else:
        results["overall_fairness_score"] = 100.0

    return results
