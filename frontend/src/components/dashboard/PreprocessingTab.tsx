"use client";

import React, { useState } from "react";
import { Cpu, Download, Play, CheckCircle2 } from "lucide-react";
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

  const plan = preprocessing?.preprocessing_plan || {};
  const summary = preprocessing?.execution_summary || {};
  const ops = summary.operations_applied || [];

  const handleRunPreprocessing = async () => {
    try {
      setLoading(true);
      await api.preprocessDataset(datasetId);
      onRunSuccess();
    } catch (err) {
      console.error("Preprocessing error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header card with action & download */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" />
            Feature Engineering & ML Preprocessing
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Categorical Encodings (Label, One-Hot, Ordinal), Numeric Scalings (Standard, MinMax, Robust, Normalize), & Train/Test Split.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunPreprocessing}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            {loading ? "Preprocessing..." : "Run Preprocessing"}
          </button>

          {preprocessing?.ml_ready_path && (
            <a
              href={api.getMLReadyUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              Download ml_ready.csv
            </a>
          )}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Target Column</span>
          <p className="text-lg font-bold text-white mt-0.5">{preprocessing?.target_column || plan.target_column || "N/A"}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Feature Count</span>
          <p className="text-lg font-bold text-white mt-0.5">{summary.feature_count ?? "N/A"}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Train / Test Samples</span>
          <p className="text-lg font-bold text-white mt-0.5">{summary.train_rows || 0} / {summary.test_rows || 0}</p>
        </div>
      </div>

      {/* Applied Operations List */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Applied Preprocessing Operations</h3>
        {ops.length > 0 ? (
          <ul className="space-y-2">
            {ops.map((op: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-300 bg-slate-800/40 p-3 rounded-xl border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-400">Click "Run Preprocessing" to execute feature encoding, scaling, and train/test split.</p>
        )}
      </div>
    </div>
  );
};
