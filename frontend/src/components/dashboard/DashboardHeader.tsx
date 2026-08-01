"use client";

import React from "react";
import { Sparkles, Database, FileText, Download, CheckCircle2, Clock } from "lucide-react";
import { api } from "@/lib/api";

interface DashboardHeaderProps {
  datasetId: string;
  datasetName: string;
  status: string;
  onUploadClick: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  datasetId,
  datasetName,
  status,
  onUploadClick,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-xl px-6 py-4 sticky top-0 z-30 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-white tracking-tight">AutoDS Platform</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 border border-slate-700 text-slate-300">
              {datasetName || "No Dataset Selected"}
            </span>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
            Dataset ID: <span className="font-mono text-slate-300">{datasetId || "N/A"}</span>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
          {status === "completed" ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Pipeline Complete</span>
            </>
          ) : (
            <>
              <Clock className="w-4 h-4 text-amber-400 animate-spin" />
              <span>Status: {status}</span>
            </>
          )}
        </div>

        {/* Report Download Dropdown / Buttons */}
        {datasetId && (
          <div className="flex items-center gap-2">
            <a
              href={api.getEDAReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              EDA Report
            </a>
            <a
              href={api.getEvaluationReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-purple-400" />
              Eval Report
            </a>
          </div>
        )}

        <button
          onClick={onUploadClick}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 transition"
        >
          <Database className="w-4 h-4" />
          Upload Dataset
        </button>
      </div>
    </header>
  );
};
