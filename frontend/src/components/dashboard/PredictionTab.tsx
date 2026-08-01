"use client";

import React, { useState } from "react";
import { Send, Download, FileText, Sparkles, CheckCircle2 } from "lucide-react";
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
  const [jsonInput, setJsonInput] = useState<string>('{"f1": 2.5, "f2": 3.5}');
  const [singleResult, setSingleResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handlePredictSingle = async () => {
    try {
      setLoading(true);
      const parsed = JSON.parse(jsonInput);
      const res = await api.predictSingle(datasetId, parsed);
      setSingleResult(res.data);
      onPredictSuccess();
    } catch (err: any) {
      alert("Prediction error: " + (err.message || "Invalid JSON"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-400" />
          Model Prediction & Inference Interface
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Execute single feature inference, batch JSON predictions, or CSV uploads against trained model binaries.
        </p>
      </div>

      {/* Inference Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
          <h3 className="text-base font-semibold text-white">Single Prediction Input</h3>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            rows={5}
            className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            placeholder='{"feature1": 1.0, "feature2": 2.0}'
          />
          <button
            onClick={handlePredictSingle}
            disabled={loading}
            className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            {loading ? "Predicting..." : "Execute Prediction"}
          </button>
        </div>

        {/* Prediction Result Display */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
          <h3 className="text-base font-semibold text-white">Inference Output</h3>
          {singleResult ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase">
                <CheckCircle2 className="w-4 h-4" />
                Prediction Completed
              </div>
              <p className="text-2xl font-bold text-white">
                Result: {String(singleResult.output_summary?.prediction ?? "N/A")}
              </p>
              <pre className="text-xs font-mono text-slate-400 overflow-x-auto bg-slate-900 p-3 rounded-lg border border-slate-800">
                {JSON.stringify(singleResult, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
              Prediction results will appear here after execution.
            </div>
          )}
        </div>
      </div>

      {/* Prediction History Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Prediction History Log</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Input Summary</th>
                <th className="px-4 py-3">Output Summary</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {history?.map((h: any) => (
                <tr key={h.id} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                    {new Date(h.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 uppercase font-semibold text-xs text-blue-400">{h.prediction_type}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-300">{JSON.stringify(h.input_summary)}</td>
                  <td className="px-4 py-3 text-xs font-mono text-emerald-400">{JSON.stringify(h.output_summary)}</td>
                  <td className="px-4 py-3">
                    {h.result_file_path && (
                      <a
                        href={api.getPredictionDownloadUrl(h.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-blue-400 hover:underline font-medium"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Download CSV
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
