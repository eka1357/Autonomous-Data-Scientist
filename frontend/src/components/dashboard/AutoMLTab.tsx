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
        <div className="p-3.5 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between gap-3 text-xs text-red-700 font-medium">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-red-500 hover:text-red-700 underline text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Header & Run AutoML */}
      <div className="panel-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            Automated Machine Learning (AutoML) Leaderboard
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated algorithm competition across Logistic Regression, Random Forest, XGBoost, LightGBM, & Clustering.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunAutoML}
            disabled={loading || !datasetId}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Training Models..." : "Train AutoML Suite"}
          </button>

          {datasetId && models?.model_path && (
            <a
              href={api.getModelDownloadUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              Download best_model.joblib
            </a>
          )}
        </div>
      </div>

      {/* Best Model Winner Banner */}
      {models && (
        <div className="panel-card p-5 bg-gradient-to-r from-amber-50 to-white border border-amber-200 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-100 border border-amber-200 text-amber-700 flex items-center justify-center">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-amber-800 uppercase tracking-wider">Top Performing Model</span>
              <h3 className="text-lg font-bold text-slate-900 mt-0.5">{bestAlgorithm}</h3>
              <p className="text-xs text-slate-600 mt-0.5">
                Problem Type: <span className="text-slate-900 font-semibold uppercase">{problemType}</span> | Metric ({primaryMetric}): <span className="text-emerald-700 font-bold">{bestScore}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Algorithm Benchmark Leaderboard</h3>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Rank</th>
                <th className="px-4 py-2.5">Algorithm</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5">Primary Score ({primaryMetric})</th>
                <th className="px-4 py-2.5">Metrics Breakdown</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {leaderboard.length > 0 ? (
                leaderboard.map((item: any, idx: number) => {
                  const isWinner = idx === 0 && item.status === "completed";
                  return (
                    <tr key={idx} className={`hover:bg-slate-50 transition ${isWinner ? "bg-amber-50/50" : ""}`}>
                      <td className="px-4 py-2.5 font-bold text-slate-900">
                        {isWinner ? <Trophy className="w-3.5 h-3.5 text-amber-600 inline mr-1" /> : `#${idx + 1}`}
                      </td>
                      <td className="px-4 py-2.5 font-semibold text-slate-900">{item.algorithm}</td>
                      <td className="px-4 py-2.5">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${item.status === "completed" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 font-mono font-semibold text-emerald-700">{item.score}</td>
                      <td className="px-4 py-2.5 font-mono text-xs text-slate-500">
                        {item.metrics ? JSON.stringify(item.metrics) : item.error || "N/A"}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No trained models available yet. Click "Train AutoML Suite" to run.
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
