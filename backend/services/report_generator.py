"""
ModelAuditAI — Report Generator
Generates JSON and PDF audit reports.
"""
import json
import os
from datetime import datetime
from fpdf import FPDF
from typing import Any


REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def generate_json_report(audit_id: str, results: dict, metadata: dict = None) -> str:
    """Generate a JSON report file and return its path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{audit_id}.json")

    report = {
        "audit_id": audit_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata or {},
        "results": results,
    }

    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return path


def generate_pdf_report(audit_id: str, results: dict) -> str:
    """Generate a PDF report and return its path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{audit_id}.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Title Page ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 20, "Model Audit Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Audit ID: {audit_id}", ln=True, align="C")
    pdf.cell(0, 10, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
    pdf.ln(10)

    # --- Health Score ---
    health = results.get("health_score", {})
    if isinstance(health, dict):
        score = health.get("health_score", "N/A")
        grade = health.get("grade", "N/A")
        status = health.get("status", "N/A")

        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, f"Health Score: {score}/100 (Grade {grade} - {status})", ln=True)
        pdf.ln(5)

        # Component scores
        components = health.get("component_scores", {})
        if components:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Component Scores:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            for comp, val in components.items():
                v = f"{val:.2f}" if isinstance(val, (int, float)) else str(val)
                pdf.multi_cell(0, 7, f"  {comp.replace('_', ' ').capitalize()}: {v}/100", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

        # Warnings
        warnings = health.get("warnings", [])
        if warnings:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Warnings:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            for w in warnings:
                pdf.multi_cell(0, 7, f"  ! {w}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

        # Recommendations
        recs = health.get("recommendations", [])
        if recs:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Recommendations:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            for r in recs:
                pdf.multi_cell(0, 7, f"  - {r}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

    # --- Performance Metrics ---
    pdf.add_page()
    evaluation = results.get("evaluation", {})
    if evaluation:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Performance Metrics", ln=True)
        pdf.set_font("Helvetica", "", 11)

        task_type = evaluation.get("task_type", "")
        if task_type == "classification":
            _add_metric(pdf, "Accuracy", evaluation.get("accuracy"))
            _add_metric(pdf, "F1 Score", evaluation.get("f1_score"))
            _add_metric(pdf, "ROC AUC", evaluation.get("roc_auc"))
        else:
            _add_metric(pdf, "RMSE", evaluation.get("rmse"))
            _add_metric(pdf, "MAE", evaluation.get("mae"))
            _add_metric(pdf, "R²", evaluation.get("r2"))
        pdf.ln(5)

    # --- Overfitting ---
    overfit = results.get("overfitting", {})
    if overfit:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Overfitting Analysis", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, overfit.get("details", "No details available."), new_x="LMARGIN", new_y="NEXT")
        _add_metric(pdf, "Train Score", overfit.get("train_score"))
        _add_metric(pdf, "Test Score", overfit.get("test_score"))
        _add_metric(pdf, "Warning Level", overfit.get("warning_level"))
        pdf.ln(5)

    # --- Fairness ---
    fairness = results.get("fairness", {})
    if fairness:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Fairness Analysis", ln=True)
        pdf.set_font("Helvetica", "", 11)
        _add_metric(pdf, "Overall Fairness Score", fairness.get("overall_fairness_score"))

        for w in fairness.get("warnings", []):
            pdf.multi_cell(0, 7, f"  ! {w}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    # --- Drift ---
    drift = results.get("drift", {})
    if drift:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Data Drift Analysis", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, drift.get("summary", "No summary available."), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    # --- Leakage ---
    leakage = results.get("leakage", {})
    if leakage:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Feature Leakage Analysis", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for w in leakage.get("warnings", []):
            pdf.multi_cell(0, 7, f"  ! {w}", new_x="LMARGIN", new_y="NEXT")
        for r in leakage.get("recommendations", []):
            pdf.multi_cell(0, 7, f"  - {r}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    # --- Explainability ---
    explainability = results.get("explainability", {})
    if explainability and explainability.get("top_features"):
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Feature Importance (SHAP)", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for feat in explainability["top_features"][:10]:
            imp = feat['importance']
            v = f"{imp:.4f}" if isinstance(imp, (int, float)) else str(imp)
            pdf.multi_cell(0, 7, f"  {feat['feature']}: {v}", new_x="LMARGIN", new_y="NEXT")

    pdf.output(path)
    return path


def _add_metric(pdf, name: str, value: Any):
    """Add a single metric line to the PDF."""
    if value is not None:
        if isinstance(value, float):
            val_str = f"{value:.4f}"
        else:
            val_str = str(value)
        pdf.multi_cell(0, 7, f"  {name}: {val_str}", new_x="LMARGIN", new_y="NEXT")
