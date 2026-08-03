"use client";

import React, { useState } from "react";
import { Download, Play, ShieldCheck, Activity } from "lucide-react";
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
      <div className="panel-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            Model Evaluation & Explainability
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Accuracy, Precision, Recall, F1, ROC AUC, R², MAE, RMSE, 5-Fold Cross Validation, & SHAP Values.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            {loading ? "Evaluating..." : "Run Model Evaluation"}
          </button>

          {evaluation?.report_path && (
            <a
              href={api.getEvaluationReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              Download Eval Report
            </a>
          )}
        </div>
      </div>

      {/* Metric Grid Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {Object.entries(metrics).map(([k, v]) => {
          if (k === "confusion_matrix" || k === "cross_validation") return null;
          return (
            <div key={k} className="panel-card p-3.5 text-center">
              <span className="text-xs font-medium text-slate-500 uppercase">{k.replace("_", " ")}</span>
              <p className="text-lg font-bold text-slate-900 mt-0.5">{String(v)}</p>
            </div>
          );
        })}
      </div>

      {/* Cross Validation */}
      {cv.mean !== undefined && (
        <div className="panel-card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-600" />
            5-Fold Cross Validation
          </h3>
          <p className="text-xs text-slate-700">
            Mean CV Score: <span className="font-semibold text-emerald-700">{cv.mean}</span> &plusmn; {cv.std}
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {cv.folds?.map((score: number, idx: number) => (
              <span key={idx} className="px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-xs font-mono text-slate-700">
                Fold {idx + 1}: {score}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Feature Importance & SHAP Values Table */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Feature Importance & SHAP Explainability</h3>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Feature</th>
                <th className="px-4 py-2.5">Importance Score</th>
                <th className="px-4 py-2.5">Mean SHAP Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {Object.entries(featImp).map(([col, score]: [string, any]) => (
                <tr key={col} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-2.5 font-medium text-slate-900">{col}</td>
                  <td className="px-4 py-2.5 font-mono text-blue-700">{score}</td>
                  <td className="px-4 py-2.5 font-mono text-purple-700">{shapVals[col] ?? "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

