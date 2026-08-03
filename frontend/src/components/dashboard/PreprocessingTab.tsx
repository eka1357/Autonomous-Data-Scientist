"use client";

import React, { useState } from "react";
import { Cpu, Download, Play, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface PreprocessingTabProps {
  datasetId: string;
  preprocessing: any;
  onRunSuccess: () => void;
}

export const PreprocessingTab: React.FC<PreprocessingTabProps> = ({
  datasetId,
  preprocessing,
  onRunSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const plan = preprocessing?.preprocessing_plan || {};
  const summary = preprocessing?.execution_summary || {};
  const ops = summary.operations_applied || [];

  const handleRunPreprocessing = async () => {
    if (!datasetId) {
      setErrorMessage("Please upload a dataset first.");
      return;
    }
    try {
      setLoading(true);
      setErrorMessage(null);
      await api.preprocessDataset(datasetId);
      onRunSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute preprocessing on dataset.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Inline Error Banner */}
      {errorMessage && (
        <div className="p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-between gap-3 text-xs text-red-400 font-medium">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-red-400 hover:text-red-300 underline text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Header card with action & download */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            Feature Engineering & ML Preprocessing
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Categorical Encodings (Label, One-Hot, Ordinal), Numeric Scalings (Standard, MinMax, Robust, Normalize), & Train/Test Split.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunPreprocessing}
            disabled={loading || !datasetId}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Preprocessing..." : "Run Preprocessing"}
          </button>

          {datasetId && preprocessing?.ml_ready_path && (
            <a
              href={api.getMLReadyUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              Download ml_ready.csv
            </a>
          )}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Target Column</span>
          <p className="text-base font-semibold text-white mt-0.5">{preprocessing?.target_column || plan.target_column || "N/A"}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Feature Count</span>
          <p className="text-base font-semibold text-white mt-0.5">{summary.feature_count ?? "N/A"}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Train / Test Samples</span>
          <p className="text-base font-semibold text-white mt-0.5">{summary.train_rows || 0} / {summary.test_rows || 0}</p>
        </div>
      </div>

      {/* Applied Operations List */}
      <div className="glass-card rounded-2xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-white">Applied Preprocessing Operations</h3>
        {ops.length > 0 ? (
          <ul className="space-y-2">
            {ops.map((op: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-400">Click "Run Preprocessing" to execute feature encoding, scaling, and train/test split.</p>
        )}
      </div>
    </div>
  );
};
