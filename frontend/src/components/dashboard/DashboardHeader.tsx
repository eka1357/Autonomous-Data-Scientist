"use client";

import React from "react";
import { Database, FileText, Download, CheckCircle2, Clock, Bot } from "lucide-react";
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
    <header className="border-b border-slate-200 bg-white px-6 py-3.5 sticky top-0 z-30 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
          <Bot className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-semibold text-slate-900 tracking-tight">AutoDS Workspace</h1>
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 border border-slate-200 text-slate-700">
              {datasetName || "No Dataset Loaded"}
            </span>
          </div>
          {datasetId && (
            <p className="text-xs text-slate-500 font-mono mt-0.5">
              ID: {datasetId}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Status Indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700">
          {status === "completed" ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Pipeline Ready</span>
            </>
          ) : (
            <>
              <Clock className="w-3.5 h-3.5 text-amber-600 animate-spin" />
              <span>Status: {status}</span>
            </>
          )}
        </div>

        {/* Report Download Buttons */}
        {datasetId && (
          <div className="flex items-center gap-2">
            <a
              href={api.getEDAReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition"
            >
              <FileText className="w-3.5 h-3.5 text-slate-500" />
              EDA Report
            </a>
            <a
              href={api.getEvaluationReportUrl(datasetId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              Eval Report
            </a>
          </div>
        )}

        <button
          onClick={onUploadClick}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-slate-900 hover:bg-slate-800 text-white transition shadow-sm"
        >
          <Database className="w-3.5 h-3.5" />
          Upload Dataset
        </button>
      </div>
    </header>
  );
};

