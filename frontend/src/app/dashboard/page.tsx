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
import { Database, Filter, BarChart3, Cpu, ShieldCheck, Sparkles, Send, Upload, X } from "lucide-react";

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
  const [uploadProgressMsg, setUploadProgressMsg] = useState<string>("");

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
    } else {
      setShowUploadModal(true);
    }
  }, [datasetId]);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      setUploading(true);
      setUploadProgressMsg("Uploading dataset & running autonomous pipeline...");
      const defaultProjectId = "00000000-0000-0000-0000-000000000000";
      const res: any = await api.uploadDataset(defaultProjectId, uploadFile);
      const newId = res?.data?.dataset_id || res?.data?.id;
      if (newId) {
        setDatasetId(newId);
        setShowUploadModal(false);
        setUploadFile(null);
        await fetchDatasetDetails(newId);
      }
    } catch (err: any) {
      alert("Upload failed: " + (err.message || "Error uploading file"));
    } finally {
      setUploading(false);
      setUploadProgressMsg("");
    }
  };

  const handleLoadSampleDataset = async (sampleType: "tours" | "churn" | "housing") => {
    let csvData = "";
    let filename = "";

    if (sampleType === "tours") {
      filename = "concert_tours_sales.csv";
      csvData = `Artist,Actual gross,Adjusted gross,Shows,Year
Taylor Swift,"$736,421,584","$860,000,000",151,2023
Coldplay,"$617,800,000","$650,000,000",107,2022
Harry Styles,"$617,300,000","$630,000,000",169,2022
Ed Sheeran,"$776,200,000","$820,000,000",255,2019
U2,"$736,421,584","$810,000,000",110,2011
Guns N Roses,"$584,200,000","$610,000,000",158,2019
Rolling Stones,"$543,300,000","$580,000,000",147,2007
Metallica,"$432,100,000","$460,000,000",130,2019
Beyonce,"$579,800,000","$600,000,000",56,2023
Pink,"$397,300,000","$420,000,000",156,2019`;
    } else if (sampleType === "churn") {
      filename = "customer_churn_telecom.csv";
      csvData = `customer_id,age,tenure,monthly_charges,total_charges,contract,churn
1001,45,24,65.5,1572.0,One-Year,0
1002,29,3,89.9,269.7,Month-to-Month,1
1003,58,60,110.2,6612.0,Two-Year,0
1004,34,12,45.0,540.0,Month-to-Month,0
1005,62,48,78.4,3763.2,One-Year,0
1006,23,1,95.0,95.0,Month-to-Month,1
1007,41,36,55.8,2008.8,Two-Year,0
1008,50,18,102.5,1845.0,Month-to-Month,1
1009,31,6,70.1,420.6,Month-to-Month,1
1010,67,72,115.0,8280.0,Two-Year,0`;
    } else {
      filename = "housing_prices_seattle.csv";
      csvData = `house_id,sqft,bedrooms,bathrooms,year_built,garage_cars,price
2001,2150,4,2.5,2015,2,485000
2002,1420,3,1.5,1998,1,295000
2003,3100,5,3.5,2020,3,720000
2004,980,2,1.0,1975,0,185000
2005,1850,3,2.0,2008,2,395000
2006,2600,4,3.0,2018,2,580000
2007,1650,3,2.0,2002,1,340000
2008,4200,6,4.5,2022,3,1150000
2009,1200,2,1.5,1985,1,230000
2010,2900,4,3.0,2012,2,650000`;
    }

    const blob = new Blob([csvData], { type: "text/csv" });
    const file = new File([blob], filename, { type: "text/csv" });

    try {
      setUploading(true);
      setUploadProgressMsg(`Loading sample dataset '${filename}' & executing pipeline...`);
      const defaultProjectId = "00000000-0000-0000-0000-000000000000";
      const res: any = await api.uploadDataset(defaultProjectId, file);
      const newId = res?.data?.dataset_id || res?.data?.id;
      if (newId) {
        setDatasetId(newId);
        setShowUploadModal(false);
        setUploadFile(null);
        await fetchDatasetDetails(newId);
      }
    } catch (err: any) {
      alert("Sample upload failed: " + (err.message || "Error loading dataset"));
    } finally {
      setUploading(false);
      setUploadProgressMsg("");
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
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-blue-500 selection:text-white">
      <DashboardHeader
        datasetId={datasetId}
        datasetName={dataset?.filename || ""}
        status={dataset?.status || ""}
        onUploadClick={() => setShowUploadModal(true)}
      />

      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Workspace Navigation Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800 scrollbar-none">
          {tabs.map((t) => {
            const Icon = t.icon;
            const active = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  active
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-white" : "text-slate-400"}`} />
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
              preprocessing={preprocessing}
              profile={profile}
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
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-5">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Upload className="w-5 h-5 text-blue-400" />
                Upload Dataset (CSV / XLSX)
              </h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                disabled={uploading}
                className="w-full text-xs text-slate-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border file:border-slate-700 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer disabled:opacity-50"
              />

              {uploadProgressMsg && (
                <p className="text-xs text-blue-400 font-medium animate-pulse">
                  {uploadProgressMsg}
                </p>
              )}

              <div className="flex justify-end gap-3 pt-1">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  disabled={uploading}
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition border border-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!uploadFile || uploading}
                  className="px-5 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
                >
                  {uploading ? "Uploading..." : "Start Processing"}
                </button>
              </div>
            </form>

            {/* Quickstart Sample Datasets Section */}
            <div className="pt-4 border-t border-slate-800/80 space-y-2.5">
              <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400 block">
                Or Try a Quickstart Demo Dataset
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => handleLoadSampleDataset("tours")}
                  disabled={uploading}
                  className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition disabled:opacity-50 group"
                >
                  <p className="text-[11px] font-bold text-white group-hover:text-blue-400 truncate">🎵 Concert Tours</p>
                  <p className="text-[10px] text-slate-400 font-mono">Regression ($)</p>
                </button>

                <button
                  onClick={() => handleLoadSampleDataset("churn")}
                  disabled={uploading}
                  className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition disabled:opacity-50 group"
                >
                  <p className="text-[11px] font-bold text-white group-hover:text-purple-400 truncate">👥 Telecom Churn</p>
                  <p className="text-[10px] text-slate-400 font-mono">Classification</p>
                </button>

                <button
                  onClick={() => handleLoadSampleDataset("housing")}
                  disabled={uploading}
                  className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition disabled:opacity-50 group"
                >
                  <p className="text-[11px] font-bold text-white group-hover:text-emerald-400 truncate">🏠 Seattle Homes</p>
                  <p className="text-[10px] text-slate-400 font-mono">Regression</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
