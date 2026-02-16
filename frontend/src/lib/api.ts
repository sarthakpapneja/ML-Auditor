import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
    baseURL: API_BASE,
    timeout: 300000, // 5 min timeout for audits
});

export async function uploadModel(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/upload-model", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
}

export async function uploadData(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/upload-data", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
}

export async function runAudit(params: {
    model_filename: string;
    dataset_filename: string;
    target_column: string;
    task_type: string;
    sensitive_columns?: string[];
}) {
    const res = await api.post("/run-audit", params);
    return res.data;
}

export async function getReport(auditId: string) {
    const res = await api.get(`/report/${auditId}`);
    return res.data;
}

export function getJsonDownloadUrl(auditId: string) {
    return `${API_BASE}/report/${auditId}/download/json`;
}

export function getPdfDownloadUrl(auditId: string) {
    return `${API_BASE}/report/${auditId}/download/pdf`;
}

export async function listAudits() {
    const res = await api.get("/audits");
    return res.data;
}

export default api;
