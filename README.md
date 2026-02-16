# ModelAuditAI

> AI-powered ML model auditing system. Upload a trained model and dataset, get comprehensive bias detection, drift analysis, overfitting checks, SHAP explainability, and a unified health score — all in one dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Module              | Description                                           |
| ------------------- | ----------------------------------------------------- |
| **Performance**     | Accuracy, F1, ROC-AUC (classification) / RMSE, MAE, R² (regression) |
| **Overfitting**     | Train vs test comparison, cross-validation, overfit score |
| **Bias & Fairness** | Demographic parity, disparate impact, auto-detect sensitive columns |
| **Data Drift**      | KS test, PSI, feature-level drift severity |
| **Feature Leakage** | Correlation analysis, ID column detection, permutation importance |
| **Explainability**  | SHAP TreeExplainer / KernelExplainer, feature importance ranking |
| **Health Score**     | Weighted composite: 25% performance + 20% fairness + 20% drift + 20% overfit + 15% leakage |
| **Reports**         | Downloadable PDF + JSON reports |

## Architecture

```
model-auditor/
├── backend/                 # FastAPI + Python ML Engine
│   ├── main.py              # App entry point
│   ├── database.py          # SQLite metadata store
│   ├── schemas.py           # Pydantic models
│   ├── api/
│   │   └── routes.py        # REST endpoints
│   └── services/
│       ├── model_loader.py      # pkl/joblib/ONNX loader
│       ├── evaluator.py         # Classification + regression metrics
│       ├── overfit_detector.py  # Train/test gap analysis
│       ├── bias.py              # Fairness metrics
│       ├── drift.py             # KS test + PSI
│       ├── leakage.py           # Correlation + ID detection
│       ├── shap_explainer.py    # SHAP values
│       ├── health_score.py      # Weighted composite score
│       └── report_generator.py  # JSON + PDF output
├── frontend/                # Next.js + TypeScript + Tailwind + Shadcn
│   └── src/
│       ├── app/page.tsx         # Upload page
│       ├── app/audit/[id]/      # Audit dashboard
│       └── lib/api.ts           # Axios client
├── demo/
│   └── create_sample.py     # Generate sample model + dataset
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

### Demo Data

```bash
cd demo
python create_sample.py
```

This creates `sample_model.pkl` and `sample_dataset_encoded.csv` for testing.

### Docker

```bash
docker compose build
docker compose up
```

## API Endpoints

| Method | Endpoint                             | Description           |
| ------ | ------------------------------------ | --------------------- |
| POST   | `/api/upload-model`                  | Upload trained model  |
| POST   | `/api/upload-data`                   | Upload dataset        |
| POST   | `/api/run-audit`                     | Start audit pipeline  |
| GET    | `/api/report/{id}`                   | Get audit results     |
| GET    | `/api/report/{id}/download/pdf`      | Download PDF report   |
| GET    | `/api/report/{id}/download/json`     | Download JSON report  |
| GET    | `/api/audits`                        | List all audits       |

## Supported Models

- scikit-learn (`.pkl`, `.joblib`)
- XGBoost
- LightGBM
- ONNX (`.onnx`)

## Tech Stack

**Backend:** FastAPI · Pydantic · scikit-learn · SHAP · Evidently AI · fairlearn · pandas · scipy · statsmodels  
**Frontend:** Next.js 15 · TypeScript · Tailwind CSS · Shadcn UI · Recharts · Axios  
**Infrastructure:** Docker · SQLite · Uvicorn

## License

MIT
