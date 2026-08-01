"use client";

import React from "react";
import { Database, FileSpreadsheet, Layers, AlertCircle, Sparkles, Download } from "lucide-react";
import { api } from "@/lib/api";

interface DatasetOverviewTabProps {
  dataset: any;
  profile: any;
  analysis: any;
}

export const DatasetOverviewTab: React.FC<DatasetOverviewTabProps> = ({
  dataset,
  profile,
  analysis,
}) => {
  if (!dataset) {
    return (
      <div className="p-8 text-center text-slate-400">
        No dataset loaded. Upload a CSV dataset to view profiling metrics.
      </div>
    );
  }

  const missingValues = profile?.missing_values || {};
  const dataTypes = profile?.data_types || {};

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Total Rows</p>
              <p className="text-2xl font-bold text-white mt-0.5">{dataset.row_count || profile?.row_count || "N/A"}</p>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Total Columns</p>
              <p className="text-2xl font-bold text-white mt-0.5">{dataset.column_count || profile?.column_names?.length || "N/A"}</p>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Duplicate Rows</p>
              <p className="text-2xl font-bold text-white mt-0.5">{profile?.duplicate_row_count ?? 0}</p>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">File Type</p>
              <p className="text-2xl font-bold text-white mt-0.5 uppercase">{dataset.file_type || "CSV"}</p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis Summary */}
      {analysis && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
          <div className="flex items-center gap-2 text-purple-400 font-semibold text-base">
            <Sparkles className="w-5 h-5" />
            AI Executive Analysis & Recommended ML Task
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{analysis.summary}</p>
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <span className="px-3 py-1 rounded-lg text-xs font-medium bg-purple-500/10 border border-purple-500/20 text-purple-300">
              ML Task: <strong className="text-white capitalize">{analysis.recommended_ml_task || "Supervised Learning"}</strong>
            </span>
            <span className="px-3 py-1 rounded-lg text-xs font-medium bg-blue-500/10 border border-blue-500/20 text-blue-300">
              Target Candidate: <strong className="text-white">{analysis.target_column_candidate || "N/A"}</strong>
            </span>
          </div>
        </div>
      )}

      {/* Column Details Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-lg font-semibold text-white">Schema & Column Profile</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Column Name</th>
                <th className="px-4 py-3">Data Type</th>
                <th className="px-4 py-3">Missing Cells</th>
                <th className="px-4 py-3">Missing %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {profile?.column_names?.map((col: str) => {
                const count = missingValues[col] ?? 0;
                const total = profile?.row_count || 1;
                const pct = ((count / total) * 100).toFixed(1);
                return (
                  <tr key={col} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 font-medium text-white">{col}</td>
                    <td className="px-4 py-3 font-mono text-xs text-blue-400">{dataTypes[col] || "unknown"}</td>
                    <td className="px-4 py-3">{count}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${count > 0 ? "bg-amber-500/10 text-amber-400" : "bg-emerald-500/10 text-emerald-400"}`}>
                        {pct}%
                      </span>
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
