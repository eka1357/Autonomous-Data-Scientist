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
      <div className="panel-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            Feature Engineering & ML Preprocessing
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Categorical Encodings (Label, One-Hot, Ordinal), Numeric Scalings (Standard, MinMax, Robust, Normalize), & Train/Test Split.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunPreprocessing}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Preprocessing..." : "Run Preprocessing"}
          </button>

          {preprocessing?.ml_ready_path && (
            <a
              href={api.getMLReadyUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              Download ml_ready.csv
            </a>
          )}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="panel-card p-4">
          <span className="text-xs text-slate-500 font-medium">Target Column</span>
          <p className="text-base font-semibold text-slate-900 mt-0.5">{preprocessing?.target_column || plan.target_column || "N/A"}</p>
        </div>
        <div className="panel-card p-4">
          <span className="text-xs text-slate-500 font-medium">Feature Count</span>
          <p className="text-base font-semibold text-slate-900 mt-0.5">{summary.feature_count ?? "N/A"}</p>
        </div>
        <div className="panel-card p-4">
          <span className="text-xs text-slate-500 font-medium">Train / Test Samples</span>
          <p className="text-base font-semibold text-slate-900 mt-0.5">{summary.train_rows || 0} / {summary.test_rows || 0}</p>
        </div>
      </div>

      {/* Applied Operations List */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Applied Preprocessing Operations</h3>
        {ops.length > 0 ? (
          <ul className="space-y-2">
            {ops.map((op: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-md border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-500">Click "Run Preprocessing" to execute feature encoding, scaling, and train/test split.</p>
        )}
      </div>
    </div>
  );
};

