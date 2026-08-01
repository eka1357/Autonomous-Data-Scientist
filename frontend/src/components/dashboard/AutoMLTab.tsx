"use client";

import React, { useState } from "react";
import { Cpu, Download, Play, Trophy, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";

interface AutoMLTabProps {
  datasetId: string;
  models: any;
  onRunSuccess: () => void;
}

export const AutoMLTab: React.FC<AutoMLTabProps> = ({ datasetId, models, onRunSuccess }) => {
  const [loading, setLoading] = useState(false);

  const leaderboard = models?.leaderboard || [];
  const bestAlgorithm = models?.best_algorithm || "None";
  const bestScore = models?.best_score ?? "N/A";
  const problemType = models?.problem_type || "N/A";
  const primaryMetric = models?.primary_metric || "score";

  const handleRunAutoML = async () => {
    try {
      setLoading(true);
      await api.trainAutoML(datasetId);
      onRunSuccess();
    } catch (err) {
      console.error("AutoML training error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Run AutoML */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-amber-400" />
            Automated Machine Learning (AutoML) Leaderboard
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated algorithm competition across Logistic Regression, Random Forest, XGBoost, LightGBM, & Clustering.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunAutoML}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-amber-600 hover:bg-amber-500 text-white transition shadow-lg shadow-amber-600/20 disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            {loading ? "Training Models..." : "Train AutoML Suite"}
          </button>

          {models?.model_path && (
            <a
              href={api.getModelDownloadUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-4 h-4 text-amber-400" />
              Download best_model.joblib
            </a>
          )}
        </div>
      </div>

      {/* Best Model Winner Banner */}
      {models && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-500/30 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Trophy className="w-8 h-8" />
            </div>
            <div>
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Winning Model</span>
              <h3 className="text-2xl font-extrabold text-white mt-0.5">{bestAlgorithm}</h3>
              <p className="text-xs text-slate-400 mt-1">
                Problem Type: <span className="text-slate-200 font-semibold uppercase">{problemType}</span> | Metric ({primaryMetric}): <span className="text-emerald-400 font-bold">{bestScore}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Algorithm Benchmark Leaderboard</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Primary Score ({primaryMetric})</th>
                <th className="px-4 py-3">Metrics Breakdown</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {leaderboard.map((item: any, idx: number) => {
                const isWinner = idx === 0 && item.status === "completed";
                return (
                  <tr key={idx} className={`hover:bg-slate-800/40 transition ${isWinner ? "bg-amber-500/10" : ""}`}>
                    <td className="px-4 py-3 font-bold text-white">
                      {isWinner ? <Trophy className="w-4 h-4 text-amber-400 inline mr-1" /> : `#${idx + 1}`}
                    </td>
                    <td className="px-4 py-3 font-semibold text-white">{item.algorithm}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${item.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono font-bold text-emerald-400">{item.score}</td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {item.metrics ? JSON.stringify(item.metrics) : item.error || "N/A"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
