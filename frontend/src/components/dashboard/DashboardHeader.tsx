"use client";

import React from "react";
import { Database, FileText, Download, CheckCircle2, Clock, Bot, AlertCircle } from "lucide-react";
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
  const isCompleted = status === "completed";
  const isProcessing = status === "processing" || status === "uploaded";
  const isFailed = status === "failed";

  return (
    <header className="border-b border-slate-200 bg-white px-6 py-3.5 sticky top-0 z-30 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
          <Bot className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-semibold text-slate-900 tracking-tight">AutoDS Workspace</h1>
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 border border-slate-200 text-slate-700">
              {datasetId ? datasetName : "No Dataset Loaded"}
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
        {datasetId ? (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700">
            {isCompleted && (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700 font-medium">Pipeline Ready</span>
              </>
            )}
            {isProcessing && (
              <>
                <Clock className="w-3.5 h-3.5 text-amber-600 animate-spin" />
                <span>Processing Pipeline...</span>
              </>
            )}
            {isFailed && (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-red-600" />
                <span className="text-red-700 font-medium">Pipeline Failed</span>
              </>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-400">
            <span>Awaiting Upload</span>
          </div>
        )}

        {/* Report Download Buttons */}
        {datasetId && isCompleted && (
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
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm"
        >
          <Database className="w-3.5 h-3.5" />
          Upload Dataset
        </button>
      </div>
    </header>
  );
};
