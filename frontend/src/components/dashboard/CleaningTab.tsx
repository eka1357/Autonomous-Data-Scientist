"use client";

import React, { useState } from "react";
import { CheckCircle2, Download, Filter, Layers, Database, RefreshCw, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface CleaningTabProps {
  datasetId: string;
  cleaning: any;
  onRunSuccess?: () => void;
}

export const CleaningTab: React.FC<CleaningTabProps> = ({ datasetId, cleaning, onRunSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const plan = cleaning?.cleaning_plan || {};
  const summary = cleaning?.execution_summary || {};
  const ops = summary.operations_applied || [];

  const rowsBefore = summary.rows_before ?? 0;
  const rowsAfter = summary.rows_after ?? 0;
  const retentionPct = rowsBefore > 0 ? ((rowsAfter / rowsBefore) * 100).toFixed(1) : "100";

  const [columnStrategies, setColumnStrategies] = useState<Record<string, string>>(
    plan.fill_missing || {}
  );

  const handleStrategyChange = (col: string, strat: string) => {
    setColumnStrategies((prev) => ({
      ...prev,
      [col]: strat,
    }));
  };

  const handleReRunCleaning = async () => {
    if (!datasetId) return;
    try {
      setLoading(true);
      setErrorMessage(null);
      const customPlan = {
        ...plan,
        fill_missing: columnStrategies,
      };
      await api.cleanDataset(datasetId);
      if (onRunSuccess) onRunSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute custom cleaning plan.");
    } finally {
      setLoading(false);
    }
  };

  if (!cleaning) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400 text-sm">
        Data cleaning has not been executed yet.
      </div>
    );
  }

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

      {/* Header card with download link */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Filter className="w-4 h-4 text-blue-400" />
            Human-in-the-Loop Data Cleaning
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Preserves human-readable numbers and string values with smart imputation & per-column control.
          </p>
        </div>

        <a
          href={api.getCleanedFileUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20"
        >
          <Download className="w-3.5 h-3.5" />
          Download Cleaned CSV
        </a>
      </div>

      {/* Prominent Row Count Before vs After Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-medium">Rows Before Cleaning</span>
            <p className="text-xl font-bold text-white mt-0.5">{rowsBefore}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-medium">Rows After Cleaning</span>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">{rowsAfter}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-medium">Data Retained (%)</span>
            <p className="text-xl font-bold text-purple-400 mt-0.5">{retentionPct}%</p>
          </div>
        </div>
      </div>

      {/* Per-Column Missing Imputation Strategy Configuration */}
      {Object.keys(columnStrategies).length > 0 && (
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-white">Per-Column Missing Value Strategy</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Customize imputation (Median, Mean, Mode, Unknown) vs. Row Deletion per column.
              </p>
            </div>

            <button
              onClick={handleReRunCleaning}
              disabled={loading}
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition shadow-md cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              {loading ? "Re-cleaning..." : "Apply Custom Strategy"}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(columnStrategies).map(([col, strat]) => (
              <div key={col} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-bold text-white">{col}</span>
                  <p className="text-[11px] text-slate-400">Missing strategy</p>
                </div>

                <select
                  value={strat}
                  onChange={(e) => handleStrategyChange(col, e.target.value)}
                  className="bg-slate-950 border border-slate-800 text-xs text-blue-300 font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
                >
                  <option value="median">Impute (Median)</option>
                  <option value="mean">Impute (Mean)</option>
                  <option value="mode">Impute (Mode)</option>
                  <option value="Unknown">Impute ('Unknown')</option>
                  <option value="drop">Drop Rows</option>
                  <option value="ffill">Forward Fill</option>
                  <option value="bfill">Backward Fill</option>
                </select>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Applied Operations List */}
      <div className="glass-card rounded-2xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-white">Applied Cleaning Operations Log</h3>
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
          <p className="text-xs text-slate-400">Standard cleaning checks applied. No missing/duplicate anomalies required transformation.</p>
        )}
      </div>
    </div>
  );
};
