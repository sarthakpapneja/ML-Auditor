"""
ModelAuditAI — Data Drift Detection
Uses KS test, PSI, and basic distribution comparison.
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Compute Population Stability Index (PSI)."""
    try:
        min_val = min(expected.min(), actual.min())
        max_val = max(expected.max(), actual.max())
        
        if min_val == max_val:
            return 0.0
        
        breakpoints = np.linspace(min_val, max_val, bins + 1)
        
        expected_counts = np.histogram(expected, bins=breakpoints)[0]
        actual_counts = np.histogram(actual, bins=breakpoints)[0]
        
        # Add small epsilon to avoid division by zero
        expected_pct = (expected_counts + 1) / (len(expected) + bins)
        actual_pct = (actual_counts + 1) / (len(actual) + bins)
        
        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(psi)
    except Exception:
        return 0.0


def detect_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame,
                 target_column: Optional[str] = None) -> dict:
    """
    Detect data drift between reference and current datasets.
    Uses KS test for continuous features and PSI.
    """
    result = {
        "drift_detected": False,
        "drifted_features": [],
        "feature_details": {},
        "severity_score": 0.0,
        "drift_health_score": 100.0,
        "summary": "",
    }

    # Get common numeric columns
    if target_column:
        ref_cols = [c for c in reference_df.select_dtypes(include=[np.number]).columns
                    if c != target_column]
        cur_cols = [c for c in current_df.select_dtypes(include=[np.number]).columns
                    if c != target_column]
    else:
        ref_cols = reference_df.select_dtypes(include=[np.number]).columns.tolist()
        cur_cols = current_df.select_dtypes(include=[np.number]).columns.tolist()

    common_cols = [c for c in ref_cols if c in cur_cols]

    if not common_cols:
        result["summary"] = "No common numeric features found for drift analysis."
        return result

    drift_scores = []

    for col in common_cols:
        ref_vals = reference_df[col].dropna().values
        cur_vals = current_df[col].dropna().values

        if len(ref_vals) < 10 or len(cur_vals) < 10:
            continue

        # KS test
        ks_stat, ks_pvalue = stats.ks_2samp(ref_vals, cur_vals)

        # PSI
        psi = compute_psi(ref_vals, cur_vals)

        # Determine if drifted
        is_drifted = ks_pvalue < 0.05 or psi > 0.1

        severity = "none"
        if psi > 0.25 or ks_pvalue < 0.001:
            severity = "high"
        elif psi > 0.1 or ks_pvalue < 0.01:
            severity = "medium"
        elif is_drifted:
            severity = "low"

        detail = {
            "ks_statistic": round(float(ks_stat), 4),
            "ks_pvalue": round(float(ks_pvalue), 6),
            "psi": round(psi, 4),
            "drifted": is_drifted,
            "severity": severity,
            "ref_mean": round(float(np.mean(ref_vals)), 4),
            "cur_mean": round(float(np.mean(cur_vals)), 4),
            "ref_std": round(float(np.std(ref_vals)), 4),
            "cur_std": round(float(np.std(cur_vals)), 4),
        }

        result["feature_details"][col] = detail

        if is_drifted:
            result["drifted_features"].append(col)
            drift_scores.append(psi)

    n_features = len(common_cols)
    n_drifted = len(result["drifted_features"])

    if n_drifted > 0:
        result["drift_detected"] = True
        result["severity_score"] = round(
            (n_drifted / max(n_features, 1)) * 100, 2
        )
        result["drift_health_score"] = round(
            max(0, 100 - result["severity_score"]), 2
        )
        result["summary"] = (
            f"{n_drifted}/{n_features} features show drift. "
            f"Most affected: {', '.join(result['drifted_features'][:5])}. "
            f"Consider retraining your model."
        )
    else:
        result["drift_health_score"] = 100.0
        result["summary"] = f"No significant drift detected across {n_features} features."

    return result


def detect_drift_single_dataset(df: pd.DataFrame,
                                target_column: Optional[str] = None) -> dict:
    """
    When no reference dataset is provided, split the data in half
    and compare the two halves (simulating temporal drift).
    """
    mid = len(df) // 2
    first_half = df.iloc[:mid]
    second_half = df.iloc[mid:]

    result = detect_drift(first_half, second_half, target_column)
    result["note"] = (
        "No reference dataset provided. Data was split into two halves "
        "to approximate drift detection. For accurate drift analysis, "
        "provide a reference dataset."
    )
    return result
