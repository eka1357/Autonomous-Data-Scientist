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
      <div className="panel-card p-12 text-center text-slate-500 text-sm">
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
        <div className="panel-card p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Total Rows</p>
            <p className="text-xl font-semibold text-slate-900 mt-0.5">{dataset.row_count || profile?.row_count || "N/A"}</p>
          </div>
        </div>

        <div className="panel-card p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Total Columns</p>
            <p className="text-xl font-semibold text-slate-900 mt-0.5">{dataset.column_count || profile?.column_names?.length || "N/A"}</p>
          </div>
        </div>

        <div className="panel-card p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-100 text-amber-600 flex items-center justify-center">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Duplicate Rows</p>
            <p className="text-xl font-semibold text-slate-900 mt-0.5">{profile?.duplicate_row_count ?? 0}</p>
          </div>
        </div>

        <div className="panel-card p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">File Format</p>
            <p className="text-xl font-semibold text-slate-900 mt-0.5 uppercase">{dataset.file_type || "CSV"}</p>
          </div>
        </div>
      </div>

      {/* AI Analysis Summary */}
      {analysis && (
        <div className="panel-card p-5 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-blue-600" />
            Dataset Executive Summary & Recommended Task
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">{analysis.summary}</p>
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
              ML Task: <strong className="text-slate-900 capitalize">{analysis.recommended_ml_task || "Supervised Learning"}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
              Target Candidate: <strong className="text-blue-900">{analysis.target_column_candidate || "N/A"}</strong>
            </span>
          </div>
        </div>
      )}

      {/* Column Details Table */}
      <div className="panel-card p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-900">Schema & Column Profile</h3>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Column Name</th>
                <th className="px-4 py-2.5">Data Type</th>
                <th className="px-4 py-2.5">Missing Cells</th>
                <th className="px-4 py-2.5">Missing %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {profile?.column_names?.map((col: string) => {
                const count = missingValues[col] ?? 0;
                const total = profile?.row_count || 1;
                const pct = ((count / total) * 100).toFixed(1);
                return (
                  <tr key={col} className="hover:bg-slate-50 transition">
                    <td className="px-4 py-2.5 font-medium text-slate-900">{col}</td>
                    <td className="px-4 py-2.5 font-mono text-slate-600">{dataTypes[col] || "unknown"}</td>
                    <td className="px-4 py-2.5">{count}</td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${count > 0 ? "bg-amber-50 text-amber-700 border border-amber-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"}`}>
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

