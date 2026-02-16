"""
ModelAuditAI — Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional


class AuditRequest(BaseModel):
    model_filename: str
    dataset_filename: str
    target_column: str
    task_type: str  # "classification" or "regression"
    sensitive_columns: Optional[list[str]] = None
    reference_dataset_filename: Optional[str] = None


class AuditStatusResponse(BaseModel):
    audit_id: str
    status: str
    health_score: Optional[float] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    filename: str
    message: str
    columns: Optional[list[str]] = None
