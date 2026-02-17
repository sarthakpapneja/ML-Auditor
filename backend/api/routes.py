"""
ModelAuditAI — API Routes
All REST endpoints for the audit system.
"""
import os
import uuid
import json
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

from schemas import AuditRequest, AuditStatusResponse, UploadResponse
from database import create_audit, update_audit, get_audit
from services.model_loader import load_model, validate_model_dataset, detect_task_type
from services.evaluator import evaluate_model
from services.overfit_detector import detect_overfitting
from services.bias import detect_sensitive_columns, compute_fairness_metrics
from services.drift import detect_drift, detect_drift_single_dataset
from services.leakage import detect_leakage
from services.shap_explainer import compute_shap_values
from services.health_score import compute_health_score
from services.report_generator import generate_json_report, generate_pdf_report

router = APIRouter()

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
MODELS_DIR = os.path.join(UPLOAD_DIR, "models")
DATASETS_DIR = os.path.join(UPLOAD_DIR, "datasets")
REPORTS_DIR = os.path.join(BACKEND_DIR, "reports")

# Ensure dirs exist
for d in [MODELS_DIR, DATASETS_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)


@router.post("/upload-model", response_model=UploadResponse)
async def upload_model(file: UploadFile = File(...)):
    """Upload a trained ML model (.pkl, .joblib, .onnx)."""
    allowed_ext = {".pkl", ".joblib", ".onnx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_ext)}"
        )

    # Save file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(MODELS_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Validate model loads
    try:
        model = load_model(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail=f"Could not load model: {str(e)}")

    return UploadResponse(
        filename=filename,
        message=f"Model '{file.filename}' uploaded successfully.",
    )


@router.post("/upload-data", response_model=UploadResponse)
async def upload_data(file: UploadFile = File(...)):
    """Upload a dataset (CSV or JSON)."""
    allowed_ext = {".csv", ".json"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_ext)}"
        )

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(DATASETS_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Read to get columns
    try:
        if ext == ".csv":
            df = pd.read_csv(filepath)
        else:
            df = pd.read_json(filepath)
        columns = df.columns.tolist()
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail=f"Could not parse dataset: {str(e)}")

    return UploadResponse(
        filename=filename,
        message=f"Dataset '{file.filename}' uploaded ({len(df)} rows, {len(columns)} columns).",
        columns=columns,
    )


@router.post("/run-audit")
async def run_audit(request: AuditRequest, background_tasks: BackgroundTasks):
    """Start an audit pipeline on the uploaded model and dataset."""
    # Validate files exist
    model_path = os.path.join(MODELS_DIR, request.model_filename)
    dataset_path = os.path.join(DATASETS_DIR, request.dataset_filename)

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found. Upload first.")
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset file not found. Upload first.")

    audit_id = uuid.uuid4().hex[:12]

    # Create audit record
    create_audit(
        audit_id=audit_id,
        model_filename=request.model_filename,
        dataset_filename=request.dataset_filename,
        target_column=request.target_column,
        task_type=request.task_type,
    )

    # Run audit in background
    background_tasks.add_task(
        _run_audit_pipeline, audit_id, model_path, dataset_path,
        request.target_column, request.task_type,
        request.sensitive_columns,
        os.path.join(DATASETS_DIR, request.reference_dataset_filename) if request.reference_dataset_filename else None,
    )

    return {"audit_id": audit_id, "status": "running", "message": "Audit started."}


@router.get("/report/{audit_id}")
async def get_report(audit_id: str, format: str = "json"):
    """Get audit results."""
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")

    if audit["status"] == "running" or audit["status"] == "pending":
        return {"audit_id": audit_id, "status": audit["status"], "message": "Audit still in progress."}

    if audit["status"] == "failed":
        return {"audit_id": audit_id, "status": "failed", "error": audit.get("error")}

    # Load results
    results_path = audit.get("results_path")
    if not results_path or not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Results file not found.")

    with open(results_path, "r") as f:
        results = json.load(f)

    if format == "pdf":
        pdf_path = os.path.join(REPORTS_DIR, f"{audit_id}.pdf")
        if not os.path.exists(pdf_path):
            generate_pdf_report(audit_id, results.get("results", results))
        return FileResponse(pdf_path, media_type="application/pdf",
                          filename=f"audit_report_{audit_id}.pdf")

    return results


@router.get("/report/{audit_id}/download/pdf")
async def download_pdf(audit_id: str):
    """Download PDF report."""
    pdf_path = os.path.join(REPORTS_DIR, f"{audit_id}.pdf")
    if not os.path.exists(pdf_path):
        # Try to generate
        json_path = os.path.join(REPORTS_DIR, f"{audit_id}.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                data = json.load(f)
            generate_pdf_report(audit_id, data.get("results", data))
        else:
            raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(pdf_path, media_type="application/pdf",
                       filename=f"audit_report_{audit_id}.pdf")


@router.get("/report/{audit_id}/download/json")
async def download_json(audit_id: str):
    """Download JSON report."""
    json_path = os.path.join(REPORTS_DIR, f"{audit_id}.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(json_path, media_type="application/json",
                       filename=f"audit_report_{audit_id}.json")


@router.get("/audits")
async def list_all_audits():
    """List all audit records."""
    from database import list_audits
    return list_audits()


# ---- Audit Pipeline ----

import numpy as np


def _run_audit_pipeline(audit_id: str, model_path: str, dataset_path: str,
                        target_column: str, task_type: str,
                        sensitive_columns: Optional[list[str]] = None,
                        reference_dataset_path: Optional[str] = None):
    """Run the full audit pipeline synchronously (called as background task)."""
    try:
        update_audit(audit_id, status="running")

        # 1. Load model
        model = load_model(model_path)

        # 2. Load dataset
        ext = os.path.splitext(dataset_path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(dataset_path)
        else:
            df = pd.read_json(dataset_path)

        # 3. Prepare features
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset.")

        y = df[target_column]
        X = df.drop(columns=[target_column])

        # Auto-detect task type if needed
        if task_type == "auto":
            task_type = detect_task_type(model, y)

        # Get numeric features for model, including bools (one-hot dummies)
        X_numeric = X.select_dtypes(include=[np.number, bool]).astype(float)

        # 4. Evaluation
        evaluation = evaluate_model(model, X_numeric, y, task_type)

        # 5. Overfitting detection
        overfitting = detect_overfitting(model, X, y, task_type)

        # 6. Bias & Fairness
        if sensitive_columns is None:
            from services.bias import detect_sensitive_columns
            sensitive_columns = detect_sensitive_columns(df)
        fairness = compute_fairness_metrics(model, X, y, sensitive_columns, task_type)

        # 7. Drift detection
        if reference_dataset_path and os.path.exists(reference_dataset_path):
            ref_ext = os.path.splitext(reference_dataset_path)[1].lower()
            if ref_ext == ".csv":
                ref_df = pd.read_csv(reference_dataset_path)
            else:
                ref_df = pd.read_json(reference_dataset_path)
            drift = detect_drift(ref_df, df, target_column)
        else:
            drift = detect_drift_single_dataset(df, target_column)

        # 8. Feature leakage
        leakage = detect_leakage(model, X, y, task_type)

        # 9. SHAP explainability
        explainability = compute_shap_values(model, X, task_type)

        # 10. Health score
        health = compute_health_score(evaluation, overfitting, fairness, drift, leakage)

        # Compile results
        results = {
            "evaluation": evaluation,
            "overfitting": overfitting,
            "fairness": fairness,
            "drift": drift,
            "leakage": leakage,
            "explainability": explainability,
            "health_score": health,
        }

        # metadata for re-configuration
        metadata = {
            "model_filename": os.path.basename(model_path),
            "dataset_filename": os.path.basename(dataset_path),
            "target_column": target_column,
            "task_type": task_type,
            "columns": df.columns.tolist()
        }

        # Generate reports
        json_path = generate_json_report(audit_id, results, metadata)
        
        pdf_path = None
        try:
            pdf_path = generate_pdf_report(audit_id, results)
        except Exception as pdf_err:
            import traceback
            print(f"PDF Generation failed for {audit_id}: {pdf_err}")
            traceback.print_exc()

        update_audit(
            audit_id,
            status="completed",
            completed_at=pd.Timestamp.utcnow().isoformat(),
            results_path=json_path,
            health_score=health["health_score"],
        )

    except Exception as e:
        import traceback
        update_audit(audit_id, status="failed", error=str(e))
        print(f"Audit {audit_id} failed: {traceback.format_exc()}")
