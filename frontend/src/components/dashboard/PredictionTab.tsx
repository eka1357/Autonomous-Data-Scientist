"use client";

import React, { useState } from "react";
import { Send, Download, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface PredictionTabProps {
  datasetId: string;
  history: any[];
  onPredictSuccess: () => void;
}

export const PredictionTab: React.FC<PredictionTabProps> = ({
  datasetId,
  history,
  onPredictSuccess,
}) => {
  const [jsonInput, setJsonInput] = useState<string>('{"feature1": 2.5, "feature2": 3.5}');
  const [singleResult, setSingleResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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

      {/* Header */}
      <div className="panel-card p-5">
        <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" />
          Model Prediction & Inference Interface
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Execute single feature inference or batch predictions against trained model binaries.
        </p>
      </div>

      {/* Inference Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="panel-card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-900">Single Prediction Input (JSON Format)</h3>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            rows={5}
            className="w-full p-3 rounded-lg bg-slate-50 border border-slate-200 font-mono text-xs text-slate-800 focus:outline-none focus:border-blue-600"
            placeholder='{"feature1": 1.0, "feature2": 2.0}'
          />
          <button
            onClick={handlePredictSingle}
            disabled={loading || !datasetId}
            className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-4 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm disabled:opacity-50 cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
            {loading ? "Predicting..." : "Execute Prediction"}
          </button>
        </div>

        {/* Prediction Result Display */}
        <div className="panel-card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-900">Inference Output</h3>
          {singleResult ? (
            <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200 space-y-2">
              <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold uppercase">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Prediction Completed
              </div>
              <p className="text-xl font-bold text-slate-900">
                Result: {String(singleResult.output_summary?.prediction ?? "N/A")}
              </p>
              <pre className="text-xs font-mono text-slate-700 overflow-x-auto bg-white p-3 rounded border border-slate-200">
                {JSON.stringify(singleResult, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-slate-200 rounded-lg">
              Prediction results will appear here after execution.
            </div>
          )}
        </div>
      </div>

      {/* Prediction History Table */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Prediction History Log</h3>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Timestamp</th>
                <th className="px-4 py-2.5">Type</th>
                <th className="px-4 py-2.5">Input Summary</th>
                <th className="px-4 py-2.5">Output Summary</th>
                <th className="px-4 py-2.5">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {history && history.length > 0 ? (
                history.map((h: any) => (
                  <tr key={h.id} className="hover:bg-slate-50 transition">
                    <td className="px-4 py-2.5 font-mono text-slate-500">
                      {new Date(h.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5 uppercase font-semibold text-blue-700">{h.prediction_type}</td>
                    <td className="px-4 py-2.5 font-mono text-slate-600">{JSON.stringify(h.input_summary)}</td>
                    <td className="px-4 py-2.5 font-mono text-emerald-700">{JSON.stringify(h.output_summary)}</td>
                    <td className="px-4 py-2.5">
                      {h.result_file_path && (
                        <a
                          href={api.getPredictionDownloadUrl(h.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium"
                        >
                          <Download className="w-3.5 h-3.5" />
                          Download CSV
                        </a>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No prediction history recorded yet.
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
