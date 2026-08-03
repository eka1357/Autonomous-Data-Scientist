"use client";

import React from "react";
import { CheckCircle2, Download, Filter } from "lucide-react";
import { api } from "@/lib/api";

interface CleaningTabProps {
  datasetId: string;
  cleaning: any;
}

export const CleaningTab: React.FC<CleaningTabProps> = ({ datasetId, cleaning }) => {
  if (!cleaning) {
    return (
      <div className="panel-card p-12 text-center text-slate-500 text-sm">
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
      <div className="panel-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <Filter className="w-4 h-4 text-blue-600" />
            Human-in-the-Loop Data Cleaning
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Preserves human-readable numbers and string values without applying ML encoding or scaling.
          </p>
        </div>

        <a
          href={api.getCleanedFileUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          Download Cleaned CSV
        </a>
      </div>

      {/* Applied Operations List */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Applied Cleaning Operations</h3>
        {ops.length > 0 ? (
          <ul className="space-y-2">
            {ops.map((op: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-md border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{op}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-500">Standard cleaning checks applied. No missing/duplicate anomalies required transformation.</p>
        )}
      </div>

      {/* Cleaning Plan Details */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900">Active Cleaning Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-xs text-slate-500 font-medium">Remove Duplicates</span>
            <p className="text-sm font-semibold text-slate-900 mt-1">{plan.remove_duplicates ? "Enabled" : "Disabled"}</p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-xs text-slate-500 font-medium">Trim Whitespace</span>
            <p className="text-sm font-semibold text-slate-900 mt-1">{plan.trim_whitespace ? "Enabled" : "Disabled"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

