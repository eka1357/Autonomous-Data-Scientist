"use client";

import React, { useState, useEffect } from "react";
import { Send, Download, Sparkles, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";

interface PredictionTabProps {
  datasetId: string;
  history: any[];
  preprocessing?: any;
  profile?: any;
  onPredictSuccess: () => void;
}

export const PredictionTab: React.FC<PredictionTabProps> = ({
  datasetId,
  history,
  preprocessing,
  profile,
  onPredictSuccess,
}) => {
  const [jsonInput, setJsonInput] = useState<string>('{}');
  const [singleResult, setSingleResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Dynamically generate JSON template built from model's actual feature names and inferred types
  useEffect(() => {
    const summary = preprocessing?.execution_summary || {};
    const plan = preprocessing?.preprocessing_plan || {};
    const targetCol = preprocessing?.target_column || plan.target_column;

    let featureNames: string[] = [];

    if (summary.feature_names && Array.isArray(summary.feature_names) && summary.feature_names.length > 0) {
      featureNames = summary.feature_names;
    } else if (profile?.column_names && Array.isArray(profile.column_names)) {
      featureNames = profile.column_names.filter((c: string) => c !== targetCol);
    }

    if (featureNames.length > 0) {
      const templateObj: Record<string, any> = {};
      const dataTypes = profile?.data_types || {};

      featureNames.forEach((feat: string, idx: number) => {
        const dtype = (dataTypes[feat] || "").toLowerCase();
        if (dtype.includes("int")) {
          templateObj[feat] = (idx + 1) * 10;
        } else if (dtype.includes("float")) {
          templateObj[feat] = Number((1.5 + idx * 0.5).toFixed(2));
        } else if (dtype.includes("bool")) {
          templateObj[feat] = true;
        } else {
          templateObj[feat] = Number((1.0 + idx * 0.5).toFixed(2));
        }
      });

      setJsonInput(JSON.stringify(templateObj, null, 2));
    } else {
      setJsonInput(JSON.stringify({ feature_1: 1.0, feature_2: 2.0 }, null, 2));
    }
  }, [preprocessing, profile]);

  const handlePredictSingle = async () => {
    if (!datasetId) {
      setErrorMessage("Please upload a dataset and train a model first.");
      return;
    }
    try {
      setLoading(true);
      setErrorMessage(null);
      const parsed = JSON.parse(jsonInput);
      const res = await api.predictSingle(datasetId, parsed);
      setSingleResult(res.data);
      onPredictSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid JSON input or trained model binary not found.");
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

      {/* Header */}
      <div className="glass-card rounded-2xl p-5">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          Model Prediction & Inference Service
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Execute single feature JSON inferences or view historical batch prediction records.
        </p>
      </div>

      {/* Single Prediction Form */}
      <div className="glass-card rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Single Sample Inference (Dynamic Preprocessed Schema)</h3>
        </div>

        <div className="space-y-2">
          <label className="text-xs text-slate-400 font-medium">Feature Inputs (JSON format auto-generated from model features)</label>
          <textarea
            rows={6}
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-blue-300 font-mono focus:outline-none focus:border-blue-500 transition"
          />
        </div>

        <button
          onClick={handlePredictSingle}
          disabled={loading || !datasetId}
          className="inline-flex items-center gap-2 px-5 py-2.5 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
          {loading ? "Predicting..." : "Execute Prediction"}
        </button>

        {singleResult && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs space-y-1">
            <span className="font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Prediction Completed Successfully
            </span>
            <p className="text-slate-300 font-mono pt-1">
              Result: <strong className="text-white">{JSON.stringify(singleResult.output_summary)}</strong>
            </p>
          </div>
        )}
      </div>

      {/* Prediction History Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white">Prediction History Log</h3>
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Input Summary</th>
                <th className="px-4 py-3">Output Summary</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {history.length > 0 ? (
                history.map((h: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 font-semibold text-white uppercase">{h.prediction_type}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {h.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400">{JSON.stringify(h.input_summary)}</td>
                    <td className="px-4 py-3 font-mono text-blue-400">{JSON.stringify(h.output_summary)}</td>
                    <td className="px-4 py-3">
                      {h.result_file_path && (
                        <a
                          href={api.getPredictionDownloadUrl(h.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                        >
                          <Download className="w-3 h-3 text-slate-400" />
                          Download CSV
                        </a>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    No predictions recorded yet. Execute single or batch inference to generate logs.
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
