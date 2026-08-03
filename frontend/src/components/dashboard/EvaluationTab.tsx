"use client";

import React, { useState } from "react";
import { Download, Play, ShieldCheck, Activity, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface EvaluationTabProps {
  datasetId: string;
  evaluation: any;
  onRunSuccess: () => void;
}

export const EvaluationTab: React.FC<EvaluationTabProps> = ({
  datasetId,
  evaluation,
  onRunSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const metrics = evaluation?.metrics || {};
  const featImp = evaluation?.feature_importance || {};
  const shapVals = evaluation?.shap_values || {};
  const cv = metrics?.cross_validation || {};

  const handleRunEvaluation = async () => {
    if (!datasetId) {
      setErrorMessage("Please upload a dataset first.");
      return;
    }
    try {
      setLoading(true);
      setErrorMessage(null);
      await api.evaluateModel(datasetId);
      onRunSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute model evaluation.");
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

      {/* Header & Run Evaluation */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            Model Evaluation & SHAP Explainability
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Test Set Performance Metrics, Confusion Matrices, 5-Fold Cross-Validation, & SHAP Feature Attributions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunEvaluation}
            disabled={loading || !datasetId}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Evaluating Model..." : "Run Model Evaluation"}
          </button>

          {datasetId && evaluation?.report_path && (
            <a
              href={api.getEvaluationReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              Download HTML Evaluation Report
            </a>
          )}
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Accuracy / R²</span>
          <p className="text-xl font-bold text-white mt-0.5">{metrics.accuracy ?? metrics.r2 ?? "N/A"}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">F1 Score / MAE</span>
          <p className="text-xl font-bold text-emerald-400 mt-0.5">{metrics.f1 ?? metrics.mae ?? "N/A"}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Precision / RMSE</span>
          <p className="text-xl font-bold text-white mt-0.5">{metrics.precision ?? metrics.rmse ?? "N/A"}</p>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <span className="text-xs text-slate-400 font-medium">Recall / MSE</span>
          <p className="text-xl font-bold text-white mt-0.5">{metrics.recall ?? metrics.mse ?? "N/A"}</p>
        </div>
      </div>

      {/* Cross-Validation Card */}
      {cv?.folds && (
        <div className="glass-card rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <Activity className="w-4 h-4 text-purple-400" />
            <span>5-Fold Cross-Validation Breakdown</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
            {cv.folds.map((score: number, idx: number) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 font-mono">Fold #{idx + 1}</span>
                <p className="text-sm font-bold text-white mt-0.5">{score}</p>
              </div>
            ))}
            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-center">
              <span className="text-[10px] text-purple-300 font-mono">CV Mean ± Std</span>
              <p className="text-sm font-bold text-purple-400 mt-0.5">{cv.mean} ± {cv.std}</p>
            </div>
          </div>
        </div>
      )}

      {/* Feature Importance & SHAP Values */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Feature Importance */}
        <div className="glass-card rounded-2xl p-5 space-y-3">
          <h3 className="text-sm font-bold text-white">MDI Feature Importance</h3>
          {Object.keys(featImp).length > 0 ? (
            <div className="space-y-2.5">
              {Object.entries(featImp).map(([col, val]: [string, any]) => {
                const maxFi = Math.max(...(Object.values(featImp) as number[]).map(v => Number(v) || 0), 0.0001);
                const numVal = Number(val) || 0;
                const pct = Math.min(100, Math.max(4, (numVal / maxFi) * 100));
                return (
                  <div key={col} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-slate-200">{col}</span>
                      <span className="text-blue-400 font-mono">{numVal}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-blue-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-400">Run evaluation to compute feature importance.</p>
          )}
        </div>

        {/* SHAP Summary */}
        <div className="glass-card rounded-2xl p-5 space-y-3">
          <h3 className="text-sm font-bold text-white">SHAP Value Importance</h3>
          {Object.keys(shapVals).length > 0 ? (
            <div className="space-y-2.5">
              {Object.entries(shapVals).map(([col, val]: [string, any]) => {
                const maxShap = Math.max(...(Object.values(shapVals) as number[]).map(v => Number(v) || 0), 0.0001);
                const numVal = Number(val) || 0;
                const pct = Math.min(100, Math.max(4, (numVal / maxShap) * 100));
                return (
                  <div key={col} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-slate-200">{col}</span>
                      <span className="text-purple-400 font-mono">{numVal}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-purple-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-400">Run evaluation to compute SHAP attributions.</p>
          )}
        </div>
      </div>
    </div>
  );
};
