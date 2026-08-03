"use client";

import React, { useState, useEffect } from "react";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DatasetOverviewTab } from "@/components/dashboard/DatasetOverviewTab";
import { CleaningTab } from "@/components/dashboard/CleaningTab";
import { EDATab } from "@/components/dashboard/EDATab";
import { PreprocessingTab } from "@/components/dashboard/PreprocessingTab";
import { AutoMLTab } from "@/components/dashboard/AutoMLTab";
import { EvaluationTab } from "@/components/dashboard/EvaluationTab";
import { PredictionTab } from "@/components/dashboard/PredictionTab";
import { AIChatTab } from "@/components/dashboard/AIChatTab";
import { api } from "@/lib/api";
import { Database, Filter, BarChart3, Cpu, ShieldCheck, Sparkles, Send, Upload } from "lucide-react";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [datasetId, setDatasetId] = useState<string>("");
  const [dataset, setDataset] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [cleaning, setCleaning] = useState<any>(null);
  const [eda, setEDA] = useState<any>(null);
  const [preprocessing, setPreprocessing] = useState<any>(null);
  const [models, setModels] = useState<any>(null);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [predictionsHistory, setPredictionsHistory] = useState<any[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const fetchDatasetDetails = async (id: string) => {
    if (!id) return;
    try {
      const dRes = await api.getDataset(id);
      setDataset(dRes.data);

      try { const p = await api.getProfile(id); setProfile(p.data); } catch {}
      try { const a = await api.getAnalysis(id); setAnalysis(a.data); } catch {}
      try { const c = await api.getCleaning(id); setCleaning(c.data); } catch {}
      try { const e = await api.getEDA(id); setEDA(e.data); } catch {}
      try { const pr = await api.getPreprocessing(id); setPreprocessing(pr.data); } catch {}
      try { const m = await api.getModels(id); setModels(m.data); } catch {}
      try { const ev = await api.getEvaluation(id); setEvaluation(ev.data); } catch {}
      try { const pred = await api.getPredictionsHistory(id); setPredictionsHistory(pred.data); } catch {}
    } catch (err) {
      console.error("Error fetching dataset details:", err);
    }
  };

  useEffect(() => {
    if (datasetId) {
      fetchDatasetDetails(datasetId);
    }
  }, [datasetId]);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      setUploading(true);
      const defaultProjectId = "00000000-0000-0000-0000-000000000000";
      const res: any = await api.uploadDataset(defaultProjectId, uploadFile);
      const newId = res?.data?.dataset_id || res?.data?.id;
      if (newId) {
        setDatasetId(newId);
        setShowUploadModal(false);
        setUploadFile(null);
        fetchDatasetDetails(newId);
      }
    } catch (err: any) {
      alert("Upload failed: " + (err.message || "Error uploading file"));
    } finally {
      setUploading(false);
    }
  };

  const tabs = [
    { id: "overview", label: "Dataset Overview", icon: Database },
    { id: "cleaning", label: "Data Cleaning", icon: Filter },
    { id: "eda", label: "EDA & Charts", icon: BarChart3 },
    { id: "preprocessing", label: "ML Preprocessing", icon: Cpu },
    { id: "automl", label: "AutoML Leaderboard", icon: Cpu },
    { id: "evaluation", label: "Model Evaluation", icon: ShieldCheck },
    { id: "prediction", label: "Inference & Predictions", icon: Send },
    { id: "chat", label: "AI Assistant", icon: Sparkles },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <DashboardHeader
        datasetId={datasetId}
        datasetName={dataset?.filename || "No Dataset Loaded"}
        status={dataset?.status || "uploaded"}
        onUploadClick={() => setShowUploadModal(true)}
      />

      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Nav Tabs */}
        <div className="flex items-center gap-1.5 border-b border-slate-200 overflow-x-auto pb-1 scrollbar-none">
          {tabs.map((t) => {
            const Icon = t.icon;
            const active = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium whitespace-nowrap transition ${
                  active
                    ? "bg-white text-slate-900 shadow-sm border border-slate-200 font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <Icon className="w-3.5 h-3.5 text-slate-500" />
                {t.label}
              </button>
            );
          })}
        </div>

        {/* Tab Contents */}
        <main>
          {activeTab === "overview" && (
            <DatasetOverviewTab dataset={dataset} profile={profile} analysis={analysis} />
          )}
          {activeTab === "cleaning" && (
            <CleaningTab datasetId={datasetId} cleaning={cleaning} />
          )}
          {activeTab === "eda" && (
            <EDATab datasetId={datasetId} eda={eda} />
          )}
          {activeTab === "preprocessing" && (
            <PreprocessingTab
              datasetId={datasetId}
              preprocessing={preprocessing}
              onRunSuccess={() => fetchDatasetDetails(datasetId)}
            />
          )}
          {activeTab === "automl" && (
            <AutoMLTab
              datasetId={datasetId}
              models={models}
              onRunSuccess={() => fetchDatasetDetails(datasetId)}
            />
          )}
          {activeTab === "evaluation" && (
            <EvaluationTab
              datasetId={datasetId}
              evaluation={evaluation}
              onRunSuccess={() => fetchDatasetDetails(datasetId)}
            />
          )}
          {activeTab === "prediction" && (
            <PredictionTab
              datasetId={datasetId}
              history={predictionsHistory}
              onPredictSuccess={() => fetchDatasetDetails(datasetId)}
            />
          )}
          {activeTab === "chat" && (
            <AIChatTab datasetId={datasetId} />
          )}
        </main>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md p-6 rounded-xl bg-white border border-slate-200 shadow-lg space-y-4">
            <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Upload className="w-4 h-4 text-blue-600" />
              Upload Dataset (CSV)
            </h3>
            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-600 file:mr-4 file:py-2 file:px-3 file:rounded-lg file:border file:border-slate-300 file:text-xs file:font-medium file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 cursor-pointer"
                required
              />
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-4 py-1.5 text-xs font-medium rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 transition"
                >
                  {uploading ? "Uploading..." : "Upload Dataset"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

