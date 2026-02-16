"""
ModelAuditAI — Model Loader Service
Loads .pkl, .joblib, .onnx models and validates compatibility.
"""
import pickle
import joblib
import os
import numpy as np
import pandas as pd
from typing import Any, Optional


def load_model(filepath: str) -> Any:
    """Load a model from disk based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pkl":
        with open(filepath, "rb") as f:
            model = pickle.load(f)
        return model

    elif ext == ".joblib":
        model = joblib.load(filepath)
        return model

    elif ext == ".onnx":
        try:
            import onnxruntime as ort
            session = ort.InferenceSession(filepath)
            return session
        except ImportError:
            raise ImportError("onnxruntime is required for ONNX models")

    else:
        raise ValueError(f"Unsupported model format: {ext}")


def validate_model_dataset(model: Any, df: pd.DataFrame, target_column: str) -> dict:
    """Validate that the model is compatible with the dataset."""
    issues = []

    X = df.drop(columns=[target_column], errors='ignore')
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

    # Check if model is an ONNX session
    is_onnx = hasattr(model, 'run') and hasattr(model, 'get_inputs')

    if is_onnx:
        try:
            input_shape = model.get_inputs()[0].shape
            if input_shape and len(input_shape) > 1 and input_shape[1] is not None:
                expected_features = input_shape[1]
                if len(numeric_cols) != expected_features:
                    issues.append(
                        f"ONNX model expects {expected_features} features, "
                        f"dataset has {len(numeric_cols)} numeric columns"
                    )
        except Exception as e:
            issues.append(f"Could not validate ONNX model inputs: {str(e)}")
    else:
        # sklearn-style model
        try:
            n_features = getattr(model, 'n_features_in_', None)
            if n_features is not None and n_features != len(numeric_cols):
                issues.append(
                    f"Model expects {n_features} features, "
                    f"dataset has {len(numeric_cols)} numeric columns"
                )
        except Exception:
            pass

        # Try a small prediction
        try:
            sample = X[numeric_cols].head(1).values
            if hasattr(model, 'predict'):
                model.predict(sample)
        except Exception as e:
            issues.append(f"Model prediction test failed: {str(e)}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "n_features": len(numeric_cols),
        "numeric_columns": numeric_cols,
    }


def detect_task_type(model: Any, y: pd.Series) -> str:
    """Auto-detect whether this is a classification or regression task."""
    # Check model type
    if hasattr(model, '_estimator_type'):
        return model._estimator_type  # 'classifier' or 'regressor'

    # Check target values
    unique_vals = y.nunique()
    if unique_vals <= 20 and y.dtype in ['object', 'category', 'bool']:
        return "classifier"
    if unique_vals <= 10:
        return "classifier"

    return "regressor"
