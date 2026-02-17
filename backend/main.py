"""
ModelAuditAI — FastAPI Main Entry Point
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

"""
ModelAuditAI - Machine Learning Audit System
Copyright (c) 2026 Sarthak Papneja

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
from database import init_db

app = FastAPI(
    title="ModelAuditAI",
    description="AI-powered ML Model Auditing System",
    version="1.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for reports
reports_dir = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(reports_dir, exist_ok=True)
app.mount("/static/reports", StaticFiles(directory=reports_dir), name="reports")

# Include API routes
app.include_router(router, prefix="/api")

# Initialize database
init_db()


@app.get("/")
async def root():
    return {
        "name": "ModelAuditAI",
        "version": "1.0.0",
        "description": "AI-powered ML Model Auditing System",
        "endpoints": {
            "upload_model": "POST /api/upload-model",
            "upload_data": "POST /api/upload-data",
            "run_audit": "POST /api/run-audit",
            "get_report": "GET /api/report/{audit_id}",
            "download_pdf": "GET /api/report/{audit_id}/download/pdf",
            "download_json": "GET /api/report/{audit_id}/download/json",
            "list_audits": "GET /api/audits",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
