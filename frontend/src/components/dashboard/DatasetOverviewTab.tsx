"use client";

import React from "react";
import { Database, FileSpreadsheet, Layers, AlertCircle, Sparkles } from "lucide-react";

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
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400 text-sm">
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
        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400">Total Rows</p>
            <p className="text-xl font-bold text-white mt-0.5">{dataset.row_count || profile?.row_count || "N/A"}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400">Total Columns</p>
            <p className="text-xl font-bold text-white mt-0.5">{dataset.column_count || profile?.column_names?.length || "N/A"}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400">Duplicate Rows</p>
            <p className="text-xl font-bold text-white mt-0.5">{profile?.duplicate_row_count ?? 0}</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400">File Type & Size</p>
            <p className="text-sm font-bold text-white mt-0.5 uppercase">
              {dataset.file_type} ({(dataset.file_size_bytes / 1024).toFixed(1)} KB)
            </p>
          </div>
        </div>
      </div>

      {/* AI Executive Analysis Card */}
      {analysis && (
        <div className="glass-card rounded-2xl p-6 border-l-4 border-l-blue-500 space-y-3">
          <div className="flex items-center gap-2 text-blue-400 text-sm font-semibold">
            <Sparkles className="w-4 h-4" />
            <span>AI Executive Analysis & Recommendation</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed font-normal">{analysis.summary}</p>
          <div className="flex flex-wrap gap-4 pt-2 text-xs font-medium">
            <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300">
              Recommended Task: <strong className="text-white">{analysis.recommended_ml_task || "General Analysis"}</strong>
            </span>
            {analysis.target_column_candidate && (
              <span className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300">
                Candidate Target Column: <strong className="text-white">{analysis.target_column_candidate}</strong>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Schema & Missing Data Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white">Dataset Schema & Missing Values</h3>
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Column Name</th>
                <th className="px-4 py-3">Data Type</th>
                <th className="px-4 py-3">Missing Values</th>
                <th className="px-4 py-3">Completeness %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(profile?.column_names || []).map((col: string) => {
                const dtype = dataTypes[col] || "unknown";
                const missing = missingValues[col] || 0;
                const total = dataset.row_count || profile?.row_count || 1;
                const pct = Math.max(0, Math.min(100, ((total - missing) / total) * 100)).toFixed(1);
                return (
                  <tr key={col} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 font-semibold text-white">{col}</td>
                    <td className="px-4 py-3 text-slate-400 font-mono">{dtype}</td>
                    <td className="px-4 py-3 text-slate-400">{missing}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-blue-500 h-1.5 rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="font-medium text-slate-300">{pct}%</span>
                      </div>
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
