"use client";

import React, { useState } from "react";
import { Cpu, Download, Play, Trophy, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface AutoMLTabProps {
  datasetId: string;
  models: any;
  onRunSuccess: () => void;
}

export const AutoMLTab: React.FC<AutoMLTabProps> = ({ datasetId, models, onRunSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const leaderboard = models?.leaderboard || [];
  const bestAlgorithm = models?.best_algorithm || "None";
  const bestScore = models?.best_score ?? "N/A";
  const problemType = models?.problem_type || "N/A";
  const primaryMetric = models?.primary_metric || "score";

  const handleRunAutoML = async () => {
    if (!datasetId) {
      setErrorMessage("Please upload a dataset first.");
      return;
    }
    try {
      setLoading(true);
      setErrorMessage(null);
      await api.trainAutoML(datasetId);
      onRunSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute AutoML training.");
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

      {/* Header & Run AutoML */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            Automated Machine Learning (AutoML) Leaderboard
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Compares Logistic Regression, Random Forest, XGBoost, & LightGBM across 5-fold cross-validation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunAutoML}
            disabled={loading || !datasetId}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Training Models..." : "Run AutoML Training"}
          </button>

          {datasetId && models?.model_path && (
            <a
              href={api.getModelDownloadUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              Download Model (.joblib)
            </a>
          )}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-medium">Best Algorithm</span>
            <p className="text-base font-bold text-white mt-0.5">{bestAlgorithm}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Best Metric Score ({primaryMetric})</span>
          <p className="text-base font-bold text-emerald-400 mt-0.5">{bestScore}</p>
        </div>

        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Problem Task Type</span>
          <p className="text-base font-bold text-white mt-0.5 capitalize">{problemType}</p>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white">Algorithm Benchmark Comparison</h3>
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Primary Score</th>
                <th className="px-4 py-3">Detailed Metrics</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {leaderboard.length > 0 ? (
                leaderboard.map((item: any, idx: number) => {
                  const isTop = idx === 0;
                  return (
                    <tr key={idx} className={isTop ? "bg-blue-500/10 hover:bg-blue-500/15" : "hover:bg-slate-800/40"}>
                      <td className="px-4 py-3 font-mono font-bold text-slate-400">
                        {isTop ? <span className="text-amber-400">🏆 #1</span> : `#${idx + 1}`}
                      </td>
                      <td className="px-4 py-3 font-semibold text-white">{item.algorithm}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${
                            item.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-red-500/10 text-red-400 border border-red-500/20"
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-bold text-white">{item.score}</td>
                      <td className="px-4 py-3 text-slate-400 font-mono text-[11px]">
                        {item.metrics ? JSON.stringify(item.metrics) : "-"}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    No models trained yet. Click "Run AutoML Training" to benchmark models.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
