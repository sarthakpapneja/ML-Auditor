"""
ModelAuditAI — SHAP Explainability Engine
Generates feature importance and SHAP values.
"""
import numpy as np
import pandas as pd
import shap
from typing import Any


def compute_shap_values(model: Any, X: pd.DataFrame, task_type: str) -> dict:
    """
    Compute SHAP values for the model.
    Returns feature importance rankings and SHAP value data.
    """
    result = {
        "feature_importance": {},
        "shap_values_sample": None,
        "top_features": [],
        "method_used": "",
        "error": None,
    }

    numeric_X = X.select_dtypes(include=[np.number])
    
    # Use a sample for performance
    sample_size = min(200, len(numeric_X))
    X_sample = numeric_X.sample(n=sample_size, random_state=42) if len(numeric_X) > sample_size else numeric_X

    try:
        # Try TreeExplainer first (for tree-based models)
        if _is_tree_model(model):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample.values)
            result["method_used"] = "TreeExplainer"
        else:
            # Fall back to KernelExplainer
            background = shap.kmeans(X_sample.values, min(10, len(X_sample)))
            explainer = shap.KernelExplainer(model.predict, background)
            shap_values = explainer.shap_values(X_sample.values[:50])  # Limit for speed
            result["method_used"] = "KernelExplainer"

        # Handle multi-class output
        if isinstance(shap_values, list):
            # For multi-class, average absolute SHAP values across classes
            shap_array = np.abs(np.array(shap_values)).mean(axis=0)
        else:
            shap_array = np.abs(shap_values)

        # Mean absolute SHAP value per feature
        mean_shap = shap_array.mean(axis=0)
        feature_names = numeric_X.columns.tolist()

        importance = {}
        for i, fname in enumerate(feature_names):
            importance[fname] = round(float(mean_shap[i]), 6)

        # Sort by importance
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        result["feature_importance"] = dict(sorted_features)
        result["top_features"] = [
            {"feature": f, "importance": v}
            for f, v in sorted_features[:15]
        ]

        # Store sample SHAP values for visualization
        if isinstance(shap_values, list):
            sv = np.array(shap_values[0]) if len(shap_values) > 0 else shap_array
        else:
            sv = shap_values

        # Send a small sample for frontend visualization
        n_display = min(50, sv.shape[0])
        result["shap_values_sample"] = sv[:n_display].tolist()
        result["feature_names"] = feature_names
        result["sample_data"] = X_sample.values[:n_display].tolist()

    except Exception as e:
        result["error"] = f"SHAP analysis failed: {str(e)}"
        
        # Fallback: use model's built-in feature importance if available
        try:
            if hasattr(model, 'feature_importances_'):
                fi = model.feature_importances_
                feature_names = numeric_X.columns.tolist()
                importance = {
                    feature_names[i]: round(float(fi[i]), 6)
                    for i in range(len(feature_names))
                }
                sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
                result["feature_importance"] = dict(sorted_features)
                result["top_features"] = [
                    {"feature": f, "importance": v}
                    for f, v in sorted_features[:15]
                ]
                result["method_used"] = "built-in feature_importances_"
                result["error"] = None
        except Exception:
            pass

    return result


def _is_tree_model(model: Any) -> bool:
    """Check if the model is tree-based."""
    tree_types = [
        'RandomForestClassifier', 'RandomForestRegressor',
        'GradientBoostingClassifier', 'GradientBoostingRegressor',
        'DecisionTreeClassifier', 'DecisionTreeRegressor',
        'ExtraTreesClassifier', 'ExtraTreesRegressor',
        'XGBClassifier', 'XGBRegressor',
        'LGBMClassifier', 'LGBMRegressor',
    ]
    model_type = type(model).__name__
    return model_type in tree_types
