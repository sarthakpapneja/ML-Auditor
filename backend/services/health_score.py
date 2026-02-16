"""
ModelAuditAI — Health Score Calculator
Combines all audit metrics into a unified health score.
"""


def compute_health_score(evaluation: dict, overfitting: dict,
                         fairness: dict, drift: dict,
                         leakage: dict) -> dict:
    """
    Compute overall model health score using weighted combination:
      0.25 × performance
      0.20 × fairness
      0.20 × drift
      0.20 × overfit
      0.15 × leakage
    """
    # Performance score (0-100)
    perf_score = evaluation.get("performance_score", 50)

    # Fairness score (0-100)
    fair_score = fairness.get("overall_fairness_score", 100)

    # Drift health (0-100)
    drift_score = drift.get("drift_health_score", 100)

    # Overfit health (0-100)
    overfit_score = overfitting.get("health_component", 100)

    # Leakage health (0-100)
    leakage_score = leakage.get("health_component", 100)

    # Weighted combination
    health = (
        0.25 * perf_score +
        0.20 * fair_score +
        0.20 * drift_score +
        0.20 * overfit_score +
        0.15 * leakage_score
    )

    health = round(min(100, max(0, health)), 2)

    # Determine grade
    if health >= 90:
        grade = "A"
        status = "Excellent"
    elif health >= 80:
        grade = "B"
        status = "Good"
    elif health >= 70:
        grade = "C"
        status = "Fair"
    elif health >= 60:
        grade = "D"
        status = "Poor"
    else:
        grade = "F"
        status = "Critical"

    # Generate warnings and recommendations
    warnings = []
    recommendations = []

    if perf_score < 60:
        warnings.append("Low model performance detected.")
        recommendations.append(
            "Consider feature engineering, hyperparameter tuning, "
            "or trying a different model architecture."
        )

    if fair_score < 80:
        warnings.append("Fairness concerns detected.")
        recommendations.append(
            "Review model predictions across sensitive groups. "
            "Consider bias mitigation techniques like reweighting or adversarial debiasing."
        )

    if drift_score < 80:
        warnings.append("Significant data drift detected.")
        recommendations.append(
            "Your model may be operating on data that differs from training distribution. "
            "Consider retraining with more recent data."
        )

    if overfit_score < 80:
        warnings.append("Overfitting detected.")
        recommendations.append(
            "Model shows significant gap between training and test performance. "
            "Try regularization, dropout, or reducing model complexity."
        )

    if leakage_score < 80:
        warnings.append("Potential feature leakage detected.")
        recommendations.append(
            "Some features may contain information that wouldn't be available at prediction time. "
            "Review flagged features and remove any that leak target information."
        )

    return {
        "health_score": health,
        "grade": grade,
        "status": status,
        "component_scores": {
            "performance": round(perf_score, 2),
            "fairness": round(fair_score, 2),
            "drift": round(drift_score, 2),
            "overfitting": round(overfit_score, 2),
            "leakage": round(leakage_score, 2),
        },
        "weights": {
            "performance": 0.25,
            "fairness": 0.20,
            "drift": 0.20,
            "overfitting": 0.20,
            "leakage": 0.15,
        },
        "warnings": warnings,
        "recommendations": recommendations,
    }
