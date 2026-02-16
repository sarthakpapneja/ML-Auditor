"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { getReport, getJsonDownloadUrl, getPdfDownloadUrl } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    PieChart,
    Pie,
    Cell,
    Legend,
} from "recharts";
import {
    Download,
    FileJson2,
    FileText,
    Shield,
    Activity,
    Brain,
    BarChart3,
    Zap,
    AlertTriangle,
    CheckCircle2,
    XCircle,
    Loader2,
    RefreshCw,
    TrendingUp,
    TrendingDown,
} from "lucide-react";

interface AuditResults {
    audit_id: string;
    generated_at: string;
    results: {
        evaluation: any;
        overfitting: any;
        fairness: any;
        drift: any;
        leakage: any;
        explainability: any;
        health_score: any;
    };
}

export default function AuditDashboard() {
    const params = useParams();
    const auditId = params.id as string;

    const [data, setData] = useState<AuditResults | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [polling, setPolling] = useState(true);

    const fetchReport = useCallback(async () => {
        try {
            const res = await getReport(auditId);
            if (res.status === "running" || res.status === "pending") {
                return false; // Still running
            }
            if (res.status === "failed") {
                setError(res.error || "Audit failed");
                setPolling(false);
                setLoading(false);
                return true;
            }
            setData(res);
            setLoading(false);
            setPolling(false);
            return true;
        } catch {
            return false;
        }
    }, [auditId]);

    useEffect(() => {
        let interval: NodeJS.Timeout;

        const startPolling = async () => {
            const done = await fetchReport();
            if (!done) {
                interval = setInterval(async () => {
                    const finished = await fetchReport();
                    if (finished) clearInterval(interval);
                }, 3000);
            }
        };

        startPolling();
        return () => clearInterval(interval);
    }, [fetchReport]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center space-y-4">
                    <Loader2 className="w-12 h-12 text-violet-400 animate-spin mx-auto" />
                    <h2 className="text-xl font-semibold">Running Audit...</h2>
                    <p className="text-zinc-400 text-sm max-w-md">
                        Analyzing model performance, bias, drift, leakage, and explainability.
                        This may take a minute.
                    </p>
                    <div className="flex items-center justify-center gap-2 text-xs text-zinc-500">
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        Auto-refreshing every 3 seconds
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Card className="max-w-md bg-zinc-900/50 border-zinc-800/60">
                    <CardContent className="pt-6 text-center space-y-4">
                        <XCircle className="w-12 h-12 text-red-400 mx-auto" />
                        <h2 className="text-xl font-semibold">Audit Failed</h2>
                        <p className="text-zinc-400 text-sm">{error}</p>
                        <Button onClick={() => window.location.href = "/"} variant="outline">
                            Try Again
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!data) return null;

    const r = data.results;
    const health = r.health_score;

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Audit Report</h1>
                    <p className="text-zinc-400 text-sm mt-1">
                        ID: {auditId} • Generated: {new Date(data.generated_at).toLocaleString()}
                    </p>
                </div>
                <div className="flex gap-3">
                    <a href={getJsonDownloadUrl(auditId)} download>
                        <Button variant="outline" size="sm" className="gap-2 border-zinc-700 hover:bg-zinc-800">
                            <FileJson2 className="w-4 h-4" /> JSON
                        </Button>
                    </a>
                    <a href={getPdfDownloadUrl(auditId)} download>
                        <Button size="sm" className="gap-2 bg-violet-600 hover:bg-violet-500 text-white">
                            <FileText className="w-4 h-4" /> PDF Report
                        </Button>
                    </a>
                </div>
            </div>

            {/* Health Score Hero */}
            <HealthScoreCard health={health} />

            {/* Warnings */}
            {health.warnings?.length > 0 && (
                <div className="grid gap-3 mt-6">
                    {health.warnings.map((w: string, i: number) => (
                        <Alert
                            key={i}
                            className="bg-amber-500/10 border-amber-500/30 text-amber-200"
                        >
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>{w}</AlertDescription>
                        </Alert>
                    ))}
                </div>
            )}

            {/* Tabs */}
            <Tabs defaultValue="performance" className="mt-8">
                <TabsList className="bg-zinc-900/80 border border-zinc-800/60 p-1 h-auto flex-wrap">
                    <TabsTrigger value="performance" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <BarChart3 className="w-4 h-4" /> Performance
                    </TabsTrigger>
                    <TabsTrigger value="fairness" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <Shield className="w-4 h-4" /> Fairness
                    </TabsTrigger>
                    <TabsTrigger value="drift" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <Activity className="w-4 h-4" /> Drift
                    </TabsTrigger>
                    <TabsTrigger value="overfitting" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <TrendingUp className="w-4 h-4" /> Overfitting
                    </TabsTrigger>
                    <TabsTrigger value="leakage" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <Zap className="w-4 h-4" /> Leakage
                    </TabsTrigger>
                    <TabsTrigger value="explainability" className="gap-2 data-[state=active]:bg-violet-600 data-[state=active]:text-white">
                        <Brain className="w-4 h-4" /> SHAP
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="performance" className="mt-6">
                    <PerformanceTab evaluation={r.evaluation} />
                </TabsContent>

                <TabsContent value="fairness" className="mt-6">
                    <FairnessTab fairness={r.fairness} />
                </TabsContent>

                <TabsContent value="drift" className="mt-6">
                    <DriftTab drift={r.drift} />
                </TabsContent>

                <TabsContent value="overfitting" className="mt-6">
                    <OverfittingTab overfitting={r.overfitting} />
                </TabsContent>

                <TabsContent value="leakage" className="mt-6">
                    <LeakageTab leakage={r.leakage} />
                </TabsContent>

                <TabsContent value="explainability" className="mt-6">
                    <ExplainabilityTab explainability={r.explainability} />
                </TabsContent>
            </Tabs>

            {/* Recommendations */}
            {health.recommendations?.length > 0 && (
                <Card className="mt-8 bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                            Recommendations
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-3">
                            {health.recommendations.map((rec: string, i: number) => (
                                <li key={i} className="flex items-start gap-3 text-sm text-zinc-300">
                                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center text-xs text-cyan-400 flex-shrink-0 mt-0.5">
                                        {i + 1}
                                    </span>
                                    {rec}
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

// ---- Sub-Components ----

function HealthScoreCard({ health }: { health: any }) {
    const score = health.health_score;
    const gradeColors: Record<string, string> = {
        A: "text-emerald-400",
        B: "text-green-400",
        C: "text-yellow-400",
        D: "text-orange-400",
        F: "text-red-400",
    };

    const radarData = Object.entries(health.component_scores || {}).map(
        ([key, value]) => ({
            subject: key.charAt(0).toUpperCase() + key.slice(1),
            score: value as number,
            fullMark: 100,
        })
    );

    return (
        <Card className="bg-zinc-900/50 border-zinc-800/60 overflow-hidden">
            <div className="bg-gradient-to-r from-violet-500/10 via-cyan-500/10 to-violet-500/10 p-1">
                <div className="bg-zinc-950 rounded-lg">
                    <CardContent className="py-8">
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                            {/* Score */}
                            <div className="text-center md:text-left">
                                <p className="text-zinc-400 text-sm uppercase tracking-wider mb-2">
                                    Model Health Score
                                </p>
                                <div className="flex items-baseline gap-3 justify-center md:justify-start">
                                    <span className="text-7xl font-bold tabular-nums bg-gradient-to-r from-violet-300 to-cyan-300 bg-clip-text text-transparent">
                                        {score}
                                    </span>
                                    <span className="text-2xl text-zinc-500">/100</span>
                                </div>
                                <div className="flex items-center gap-3 mt-4 justify-center md:justify-start">
                                    <Badge
                                        className={`text-lg px-4 py-1 ${score >= 80
                                                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                                : score >= 60
                                                    ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                                                    : "bg-red-500/20 text-red-400 border-red-500/30"
                                            }`}
                                    >
                                        Grade {health.grade}
                                    </Badge>
                                    <span className="text-zinc-400">{health.status}</span>
                                </div>

                                {/* Component bars */}
                                <div className="mt-6 space-y-3 max-w-sm">
                                    {Object.entries(health.component_scores || {}).map(
                                        ([key, value]) => (
                                            <div key={key}>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="text-zinc-400 capitalize">{key}</span>
                                                    <span className="text-zinc-300">{value as number}%</span>
                                                </div>
                                                <Progress
                                                    value={value as number}
                                                    className="h-2 bg-zinc-800"
                                                />
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>

                            {/* Radar Chart */}
                            <div className="h-72">
                                <ResponsiveContainer width="100%" height="100%">
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="#3f3f46" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
                                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#71717a", fontSize: 10 }} />
                                        <Radar
                                            name="Score"
                                            dataKey="score"
                                            stroke="#8b5cf6"
                                            fill="#8b5cf6"
                                            fillOpacity={0.2}
                                            strokeWidth={2}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </CardContent>
                </div>
            </div>
        </Card>
    );
}

function PerformanceTab({ evaluation }: { evaluation: any }) {
    if (!evaluation) return <p className="text-zinc-400">No evaluation data.</p>;

    const isClassification = evaluation.task_type === "classification";

    const metrics = isClassification
        ? [
            { name: "Accuracy", value: evaluation.accuracy, format: "%" },
            { name: "F1 Score", value: evaluation.f1_score, format: "%" },
            { name: "ROC AUC", value: evaluation.roc_auc, format: "%" },
        ]
        : [
            { name: "RMSE", value: evaluation.rmse, format: "" },
            { name: "MAE", value: evaluation.mae, format: "" },
            { name: "R²", value: evaluation.r2, format: "" },
        ];

    const chartData = metrics
        .filter((m) => m.value !== null && m.value !== undefined)
        .map((m) => ({
            name: m.name,
            value: m.format === "%" ? +(m.value * 100).toFixed(1) : +m.value,
        }));

    return (
        <div className="grid md:grid-cols-3 gap-4">
            {metrics.map((m) => (
                <Card key={m.name} className="bg-zinc-900/50 border-zinc-800/60">
                    <CardContent className="pt-6 text-center">
                        <p className="text-sm text-zinc-400 mb-2">{m.name}</p>
                        <p className="text-4xl font-bold tabular-nums">
                            {m.value !== null && m.value !== undefined
                                ? m.format === "%"
                                    ? `${(m.value * 100).toFixed(1)}%`
                                    : m.value
                                : "N/A"}
                        </p>
                    </CardContent>
                </Card>
            ))}

            <Card className="md:col-span-3 bg-zinc-900/50 border-zinc-800/60">
                <CardHeader>
                    <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                                <XAxis dataKey="name" tick={{ fill: "#a1a1aa" }} />
                                <YAxis tick={{ fill: "#a1a1aa" }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#18181b",
                                        border: "1px solid #3f3f46",
                                        borderRadius: "8px",
                                    }}
                                />
                                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

function FairnessTab({ fairness }: { fairness: any }) {
    if (!fairness)
        return <p className="text-zinc-400">No fairness data available.</p>;

    const columnMetrics = Object.entries(fairness.metrics_by_column || {});

    return (
        <div className="space-y-6">
            <Card className="bg-zinc-900/50 border-zinc-800/60">
                <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-zinc-400">Overall Fairness Score</p>
                            <p className="text-4xl font-bold mt-1">
                                {fairness.overall_fairness_score?.toFixed(1)}%
                            </p>
                        </div>
                        <Badge
                            className={
                                fairness.overall_fairness_score >= 80
                                    ? "bg-emerald-500/20 text-emerald-400"
                                    : "bg-amber-500/20 text-amber-400"
                            }
                        >
                            {fairness.overall_fairness_score >= 80 ? "Fair" : "Review Required"}
                        </Badge>
                    </div>
                </CardContent>
            </Card>

            {fairness.warnings?.map((w: string, i: number) => (
                <Alert key={i} className="bg-amber-500/10 border-amber-500/30 text-amber-200">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{w}</AlertDescription>
                </Alert>
            ))}

            {columnMetrics.map(([col, metrics]: [string, any]) => {
                const groups = Object.entries(metrics.groups || {});
                const chartData = groups.map(([group, vals]: [string, any]) => ({
                    group,
                    positive_rate: +(vals.positive_rate * 100).toFixed(1),
                    accuracy: vals.accuracy ? +(vals.accuracy * 100).toFixed(1) : 0,
                }));

                return (
                    <Card key={col} className="bg-zinc-900/50 border-zinc-800/60">
                        <CardHeader>
                            <CardTitle className="text-lg">
                                Sensitive Column: <span className="text-violet-400">{col}</span>
                            </CardTitle>
                            <div className="flex gap-4 text-sm text-zinc-400">
                                <span>
                                    Demographic Parity Diff:{" "}
                                    <strong className="text-zinc-200">
                                        {metrics.demographic_parity_difference}
                                    </strong>
                                </span>
                                <span>
                                    Disparate Impact:{" "}
                                    <strong className="text-zinc-200">
                                        {metrics.disparate_impact_ratio}
                                    </strong>
                                </span>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="h-56">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                                        <XAxis dataKey="group" tick={{ fill: "#a1a1aa" }} />
                                        <YAxis tick={{ fill: "#a1a1aa" }} />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "#18181b",
                                                border: "1px solid #3f3f46",
                                                borderRadius: "8px",
                                            }}
                                        />
                                        <Bar dataKey="positive_rate" name="Positive Rate %" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="accuracy" name="Accuracy %" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                                        <Legend />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}

function DriftTab({ drift }: { drift: any }) {
    if (!drift) return <p className="text-zinc-400">No drift data available.</p>;

    const featureData = Object.entries(drift.feature_details || {}).map(
        ([feat, detail]: [string, any]) => ({
            feature: feat,
            psi: detail.psi,
            ks_stat: detail.ks_statistic,
            drifted: detail.drifted,
            severity: detail.severity,
        })
    );

    const COLORS = {
        high: "#ef4444",
        medium: "#f59e0b",
        low: "#22c55e",
        none: "#6b7280",
    };

    return (
        <div className="space-y-6">
            <Card className="bg-zinc-900/50 border-zinc-800/60">
                <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-zinc-400">Drift Health Score</p>
                            <p className="text-4xl font-bold mt-1">{drift.drift_health_score}%</p>
                        </div>
                        <Badge
                            className={
                                drift.drift_detected
                                    ? "bg-red-500/20 text-red-400"
                                    : "bg-emerald-500/20 text-emerald-400"
                            }
                        >
                            {drift.drift_detected ? "Drift Detected" : "No Drift"}
                        </Badge>
                    </div>
                    <p className="text-sm text-zinc-400 mt-3">{drift.summary}</p>
                    {drift.note && (
                        <p className="text-xs text-zinc-500 mt-2 italic">{drift.note}</p>
                    )}
                </CardContent>
            </Card>

            {featureData.length > 0 && (
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle>Feature Drift Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={featureData.slice(0, 15)} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                                    <XAxis type="number" tick={{ fill: "#a1a1aa" }} />
                                    <YAxis dataKey="feature" type="category" width={120} tick={{ fill: "#a1a1aa", fontSize: 11 }} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: "#18181b",
                                            border: "1px solid #3f3f46",
                                            borderRadius: "8px",
                                        }}
                                    />
                                    <Bar dataKey="psi" name="PSI Score" radius={[0, 4, 4, 0]}>
                                        {featureData.slice(0, 15).map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={COLORS[entry.severity as keyof typeof COLORS] || COLORS.none}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

function OverfittingTab({ overfitting }: { overfitting: any }) {
    if (!overfitting)
        return <p className="text-zinc-400">No overfitting data available.</p>;

    const compareData = [
        {
            name: "Train",
            score: overfitting.train_score ? +(overfitting.train_score * 100).toFixed(1) : 0,
        },
        {
            name: "Test",
            score: overfitting.test_score ? +(overfitting.test_score * 100).toFixed(1) : 0,
        },
    ];

    const warningColors: Record<string, string> = {
        high: "bg-red-500/20 text-red-400",
        medium: "bg-amber-500/20 text-amber-400",
        low: "bg-emerald-500/20 text-emerald-400",
        none: "bg-zinc-500/20 text-zinc-300",
    };

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-4">
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardContent className="pt-6 text-center">
                        <p className="text-sm text-zinc-400 mb-2">Train Score</p>
                        <p className="text-3xl font-bold">
                            {overfitting.train_score ? (overfitting.train_score * 100).toFixed(1) + "%" : "N/A"}
                        </p>
                    </CardContent>
                </Card>
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardContent className="pt-6 text-center">
                        <p className="text-sm text-zinc-400 mb-2">Test Score</p>
                        <p className="text-3xl font-bold">
                            {overfitting.test_score ? (overfitting.test_score * 100).toFixed(1) + "%" : "N/A"}
                        </p>
                    </CardContent>
                </Card>
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardContent className="pt-6 text-center">
                        <p className="text-sm text-zinc-400 mb-2">Warning Level</p>
                        <Badge className={warningColors[overfitting.warning_level] || warningColors.none}>
                            {overfitting.warning_level?.toUpperCase() || "UNKNOWN"}
                        </Badge>
                    </CardContent>
                </Card>
            </div>

            <Card className="bg-zinc-900/50 border-zinc-800/60">
                <CardHeader>
                    <CardTitle>Train vs Test Performance</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-56">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={compareData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                                <XAxis dataKey="name" tick={{ fill: "#a1a1aa" }} />
                                <YAxis tick={{ fill: "#a1a1aa" }} domain={[0, 100]} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#18181b",
                                        border: "1px solid #3f3f46",
                                        borderRadius: "8px",
                                    }}
                                />
                                <Bar dataKey="score" name="Score %" radius={[4, 4, 0, 0]}>
                                    <Cell fill="#8b5cf6" />
                                    <Cell fill="#06b6d4" />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-sm text-zinc-400 mt-4">{overfitting.details}</p>
                </CardContent>
            </Card>

            {overfitting.cv_scores && (
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle>Cross-Validation Scores</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4 flex-wrap">
                            {overfitting.cv_scores.map((s: number, i: number) => (
                                <div key={i} className="text-center">
                                    <p className="text-xs text-zinc-500">Fold {i + 1}</p>
                                    <p className="text-lg font-bold tabular-nums">
                                        {(s * 100).toFixed(1)}%
                                    </p>
                                </div>
                            ))}
                            <Separator orientation="vertical" className="h-10 bg-zinc-700" />
                            <div className="text-center">
                                <p className="text-xs text-zinc-500">Mean ± Std</p>
                                <p className="text-lg font-bold">
                                    {(overfitting.cv_mean * 100).toFixed(1)}% ±{" "}
                                    {(overfitting.cv_std * 100).toFixed(1)}%
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

function LeakageTab({ leakage }: { leakage: any }) {
    if (!leakage)
        return <p className="text-zinc-400">No leakage data available.</p>;

    return (
        <div className="space-y-6">
            <Card className="bg-zinc-900/50 border-zinc-800/60">
                <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-zinc-400">Leakage Health</p>
                            <p className="text-4xl font-bold mt-1">{leakage.health_component}%</p>
                        </div>
                        <Badge
                            className={
                                leakage.leakage_detected
                                    ? "bg-red-500/20 text-red-400"
                                    : "bg-emerald-500/20 text-emerald-400"
                            }
                        >
                            {leakage.leakage_detected ? "Leakage Found" : "No Leakage"}
                        </Badge>
                    </div>
                </CardContent>
            </Card>

            {leakage.warnings?.length > 0 && (
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-amber-400" /> Warnings
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {leakage.warnings.map((w: string, i: number) => (
                                <li key={i} className="text-sm text-amber-200 flex items-start gap-2">
                                    <span className="text-amber-400 mt-0.5">•</span> {w}
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}

            {leakage.high_correlation_features?.length > 0 && (
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle>High Correlation Features</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {leakage.high_correlation_features.map((f: any) => (
                                <div key={f.feature} className="flex items-center justify-between">
                                    <span className="text-sm text-zinc-300">{f.feature}</span>
                                    <div className="flex items-center gap-2">
                                        <Progress value={f.correlation * 100} className="w-32 h-2 bg-zinc-800" />
                                        <span className="text-sm font-mono text-red-400">
                                            {f.correlation}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {leakage.id_columns?.length > 0 && (
                <Card className="bg-zinc-900/50 border-zinc-800/60">
                    <CardHeader>
                        <CardTitle>Suspected ID Columns</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex gap-2 flex-wrap">
                            {leakage.id_columns.map((col: string) => (
                                <Badge key={col} variant="destructive" className="bg-red-500/20 text-red-400 border-red-500/30">
                                    {col}
                                </Badge>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

function ExplainabilityTab({ explainability }: { explainability: any }) {
    if (!explainability)
        return <p className="text-zinc-400">No explainability data available.</p>;

    if (explainability.error) {
        return (
            <Alert className="bg-amber-500/10 border-amber-500/30 text-amber-200">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{explainability.error}</AlertDescription>
            </Alert>
        );
    }

    const topFeatures = explainability.top_features || [];
    const chartData = topFeatures.map((f: any) => ({
        feature: f.feature,
        importance: +f.importance.toFixed(4),
    }));

    return (
        <div className="space-y-6">
            <Card className="bg-zinc-900/50 border-zinc-800/60">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="w-5 h-5 text-violet-400" />
                        Feature Importance (SHAP)
                    </CardTitle>
                    <p className="text-sm text-zinc-500">
                        Method: {explainability.method_used || "Unknown"}
                    </p>
                </CardHeader>
                <CardContent>
                    <div className="h-[400px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                                <XAxis type="number" tick={{ fill: "#a1a1aa" }} />
                                <YAxis
                                    dataKey="feature"
                                    type="category"
                                    width={150}
                                    tick={{ fill: "#a1a1aa", fontSize: 11 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#18181b",
                                        border: "1px solid #3f3f46",
                                        borderRadius: "8px",
                                    }}
                                />
                                <Bar
                                    dataKey="importance"
                                    name="SHAP Importance"
                                    fill="url(#shapGradient)"
                                    radius={[0, 4, 4, 0]}
                                />
                                <defs>
                                    <linearGradient id="shapGradient" x1="0" y1="0" x2="1" y2="0">
                                        <stop offset="0%" stopColor="#8b5cf6" />
                                        <stop offset="100%" stopColor="#06b6d4" />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
