"use client";

import React from "react";
import { CheckCircle2, Download, Filter, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";

interface CleaningTabProps {
  datasetId: string;
  cleaning: any;
}

export const CleaningTab: React.FC<CleaningTabProps> = ({ datasetId, cleaning }) => {
  if (!cleaning) {
    return (
      <div className="p-8 text-center text-slate-400">
        Data cleaning has not been executed yet.
      </div>
    );
  }

  const plan = cleaning.cleaning_plan || {};
  const summary = cleaning.execution_summary || {};
  const ops = summary.operations_applied || [];

  return (
    <div className="space-y-6">
      {/* Header card with download link */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Filter className="w-5 h-5 text-blue-400" />
            Human-in-the-Loop Data Cleaning
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Data cleaning maintains human-readable numbers and strings without performing encoding or scaling.
          </p>
        </div>

        <a
          href={api.getCleanedFileUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition shadow-lg shadow-blue-600/20"
        >
          <Download className="w-4 h-4" />
          Download Cleaned CSV
        </a>
      </div>

      {/* Applied Operations List */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Applied Cleaning Operations</h3>
        {ops.length > 0 ? (
          <ul className="space-y-2">
            {ops.map((op: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-300 bg-slate-800/40 p-3 rounded-xl border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-400">Standard cleaning checks applied. No missing/duplicate anomalies required transformation.</p>
        )}
      </div>

      {/* Cleaning Plan Details */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white">Active Cleaning Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium">Remove Duplicates</span>
            <p className="text-base font-semibold text-white mt-1">{plan.remove_duplicates ? "Enabled" : "Disabled"}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium">Trim Whitespace</span>
            <p className="text-base font-semibold text-white mt-1">{plan.trim_whitespace ? "Enabled" : "Disabled"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
