"use client";

import React, { useState } from "react";
import { CheckCircle2, Download, Play, ShieldCheck, Activity } from "lucide-react";
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

  const metrics = evaluation?.metrics || {};
  const featImp = evaluation?.feature_importance || {};
  const shapVals = evaluation?.shap_values || {};
  const cv = metrics?.cross_validation || {};

  const handleRunEvaluation = async () => {
    try {
      setLoading(true);
      await api.evaluateModel(datasetId);
      onRunSuccess();
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Run Evaluation */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            Model Evaluation & Explainability
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Accuracy, Precision, Recall, F1, ROC AUC, R², MAE, RMSE, 5-Fold Cross Validation, & SHAP Values.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white transition shadow-lg shadow-cyan-600/20 disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            {loading ? "Evaluating..." : "Run Model Evaluation"}
          </button>

          {evaluation?.report_path && (
            <a
              href={api.getEvaluationReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-4 h-4 text-cyan-400" />
              Download HTML Evaluation Report
            </a>
          )}
        </div>
      </div>

      {/* Metric Grid Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {Object.entries(metrics).map(([k, v]) => {
          if (k === "confusion_matrix" || k === "cross_validation") return null;
          return (
            <div key={k} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-xs font-medium text-slate-400 uppercase">{k.replace("_", " ")}</span>
              <p className="text-xl font-bold text-cyan-400 mt-1">{String(v)}</p>
            </div>
          );
        })}
      </div>

      {/* Cross Validation */}
      {cv.mean !== undefined && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-3">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            5-Fold Cross Validation
          </h3>
          <p className="text-sm text-slate-300">
            Mean CV Score: <span className="font-bold text-emerald-400">{cv.mean}</span> &plusmn; {cv.std}
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {cv.folds?.map((score: number, idx: number) => (
              <span key={idx} className="px-3 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs font-mono text-slate-200">
                Fold {idx + 1}: {score}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Feature Importance & SHAP Values Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Feature Importance & SHAP Explainability</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Feature</th>
                <th className="px-4 py-3">Importance Score</th>
                <th className="px-4 py-3">Mean SHAP Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {Object.entries(featImp).map(([col, score]: [string, any]) => (
                <tr key={col} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 font-medium text-white">{col}</td>
                  <td className="px-4 py-3 font-mono text-cyan-400">{score}</td>
                  <td className="px-4 py-3 font-mono text-purple-400">{shapVals[col] ?? "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
