/**
 * ModelAuditAI - Machine Learning Audit System
 * Copyright (c) 2026 Sarthak Papneja
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { uploadModel, uploadData, runAudit } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Upload,
  FileUp,
  Brain,
  Shield,
  Activity,
  BarChart3,
  Zap,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Loader2,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  // State
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [modelFilename, setModelFilename] = useState("");
  const [datasetFilename, setDatasetFilename] = useState("");
  const [columns, setColumns] = useState<string[]>([]);
  const [targetColumn, setTargetColumn] = useState("");
  const [taskType, setTaskType] = useState("classification");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [uploadProgress, setUploadProgress] = useState({
    model: false,
    dataset: false,
  });

  const handleModelUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setModelFile(file);
      setError("");

      try {
        setUploadProgress((p) => ({ ...p, model: true }));
        const res = await uploadModel(file);
        setModelFilename(res.filename);
        setUploadProgress((p) => ({ ...p, model: false }));
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Failed to upload model");
        setUploadProgress((p) => ({ ...p, model: false }));
        setModelFile(null);
      }
    },
    []
  );

  const handleDatasetUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setDatasetFile(file);
      setError("");

      try {
        setUploadProgress((p) => ({ ...p, dataset: true }));
        const res = await uploadData(file);
        setDatasetFilename(res.filename);
        setColumns(res.columns || []);
        setUploadProgress((p) => ({ ...p, dataset: false }));
        setStep(2);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Failed to upload dataset");
        setUploadProgress((p) => ({ ...p, dataset: false }));
        setDatasetFile(null);
      }
    },
    []
  );

  const handleRunAudit = useCallback(async () => {
    if (!modelFilename || !datasetFilename || !targetColumn) {
      setError("Please complete all steps before running audit.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await runAudit({
        model_filename: modelFilename,
        dataset_filename: datasetFilename,
        target_column: targetColumn,
        task_type: taskType,
      });
      router.push(`/audit/${res.audit_id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to start audit");
      setLoading(false);
    }
  }, [modelFilename, datasetFilename, targetColumn, taskType, router]);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-500/5 via-transparent to-transparent" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-violet-500/10 rounded-full blur-[120px]" />

        <div className="relative max-w-7xl mx-auto px-6 pt-20 pb-16">
          <div className="text-center max-w-3xl mx-auto">
            <Badge variant="secondary" className="mb-6 bg-violet-500/10 text-violet-400 border-violet-500/20 hover:bg-violet-500/15">
              Production-Ready ML Auditing
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-zinc-100 via-violet-200 to-cyan-200 bg-clip-text text-transparent">
              Audit Your ML Models
              <br />
              <span className="text-violet-400">Before They Ship</span>
            </h1>
            <p className="text-lg text-zinc-400 mb-10 leading-relaxed max-w-2xl mx-auto">
              Upload your trained model and dataset. Get comprehensive bias detection,
              drift analysis, overfitting checks, SHAP explainability, and a health
              score — all in one dashboard.
            </p>
          </div>

          {/* Feature pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-16">
            {[
              { icon: Shield, label: "Bias Detection" },
              { icon: Activity, label: "Drift Analysis" },
              { icon: Brain, label: "SHAP Explainability" },
              { icon: BarChart3, label: "Performance Metrics" },
              { icon: Zap, label: "Feature Leakage" },
              { icon: AlertTriangle, label: "Overfitting Check" },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900/80 border border-zinc-800/60 text-sm text-zinc-300"
              >
                <Icon className="w-4 h-4 text-violet-400" />
                {label}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        <div className="grid gap-6">
          {error && (
            <Alert variant="destructive" className="bg-red-500/10 border-red-500/30 text-red-300">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Step 1: Upload Files */}
          <Card className="bg-zinc-900/50 border-zinc-800/60 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-sm font-bold text-violet-400">
                  1
                </div>
                <div>
                  <CardTitle>Upload Model & Dataset</CardTitle>
                  <CardDescription className="text-zinc-500">
                    Upload your trained model (.pkl, .joblib, .onnx) and dataset
                    (.csv, .json)
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {/* Model upload */}
                <label className="relative group cursor-pointer">
                  <div
                    className={`flex flex-col items-center justify-center gap-3 p-8 rounded-xl border-2 border-dashed transition-all duration-300 ${modelFile
                      ? "border-emerald-500/40 bg-emerald-500/5"
                      : "border-zinc-700/60 hover:border-violet-500/40 hover:bg-violet-500/5"
                      }`}
                  >
                    {uploadProgress.model ? (
                      <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
                    ) : modelFile ? (
                      <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                    ) : (
                      <FileUp className="w-8 h-8 text-zinc-500 group-hover:text-violet-400 transition-colors" />
                    )}
                    <div className="text-center">
                      <p className="font-medium text-sm">
                        {modelFile ? modelFile.name : "Upload Model"}
                      </p>
                      <p className="text-xs text-zinc-500 mt-1">
                        .pkl, .joblib, .onnx
                      </p>
                    </div>
                  </div>
                  <input
                    type="file"
                    accept=".pkl,.joblib,.onnx"
                    onChange={handleModelUpload}
                    className="hidden"
                  />
                </label>

                {/* Dataset upload */}
                <label className="relative group cursor-pointer">
                  <div
                    className={`flex flex-col items-center justify-center gap-3 p-8 rounded-xl border-2 border-dashed transition-all duration-300 ${datasetFile
                      ? "border-emerald-500/40 bg-emerald-500/5"
                      : "border-zinc-700/60 hover:border-violet-500/40 hover:bg-violet-500/5"
                      }`}
                  >
                    {uploadProgress.dataset ? (
                      <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
                    ) : datasetFile ? (
                      <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                    ) : (
                      <Upload className="w-8 h-8 text-zinc-500 group-hover:text-violet-400 transition-colors" />
                    )}
                    <div className="text-center">
                      <p className="font-medium text-sm">
                        {datasetFile ? datasetFile.name : "Upload Dataset"}
                      </p>
                      <p className="text-xs text-zinc-500 mt-1">.csv, .json</p>
                    </div>
                  </div>
                  <input
                    type="file"
                    accept=".csv,.json"
                    onChange={handleDatasetUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </CardContent>
          </Card>

          {/* Step 2: Configure */}
          {step >= 2 && columns.length > 0 && (
            <Card className="bg-zinc-900/50 border-zinc-800/60 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-sm font-bold text-violet-400">
                    2
                  </div>
                  <div>
                    <CardTitle>Configure Audit</CardTitle>
                    <CardDescription className="text-zinc-500">
                      Select your target column and task type
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="text-zinc-300">Target Column</Label>
                    <Select value={targetColumn} onValueChange={setTargetColumn}>
                      <SelectTrigger className="bg-zinc-800/50 border-zinc-700/60">
                        <SelectValue placeholder="Select target column" />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-800">
                        {columns.map((col) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-zinc-300">Task Type</Label>
                    <Select value={taskType} onValueChange={setTaskType}>
                      <SelectTrigger className="bg-zinc-800/50 border-zinc-700/60">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-800">
                        <SelectItem value="classification">Classification</SelectItem>
                        <SelectItem value="regression">Regression</SelectItem>
                        <SelectItem value="auto">Auto-Detect</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button
                  onClick={handleRunAudit}
                  disabled={loading || !targetColumn}
                  className="w-full mt-6 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold h-12 text-base"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      Starting Audit...
                    </>
                  ) : (
                    <>
                      Run Full Audit
                      <ChevronRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </div>
  );
}
