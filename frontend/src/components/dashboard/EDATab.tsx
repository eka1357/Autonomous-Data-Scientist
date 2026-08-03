"use client";

import React from "react";
import { BarChart3, Download, Eye, AlertOctagon } from "lucide-react";
import { api } from "@/lib/api";

interface EDATabProps {
  datasetId: string;
  eda: any;
}

export const EDATab: React.FC<EDATabProps> = ({ datasetId, eda }) => {
  if (!eda) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400 text-sm">
        Exploratory Data Analysis (EDA) has not been run yet.
      </div>
    );
  }

  const summary = eda.summary || "";
  const insights = eda.insights || {};
  const outliers = eda.outliers || {};

  return (
    <div className="space-y-6">
      {/* Header & Report Download */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            Exploratory Data Analysis (EDA) & Outliers
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            IQR outlier bounds, statistical moments, and correlation discovery.
          </p>
        </div>

        <a
          href={api.getEDAReportUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20"
        >
          <Download className="w-3.5 h-3.5" />
          Download EDA HTML Report
        </a>
      </div>

      {/* Summary Card */}
      {summary && (
        <div className="glass-card rounded-2xl p-5 space-y-2">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Executive Overview</h3>
          <p className="text-sm text-slate-200 leading-relaxed font-normal">{summary}</p>
        </div>
      )}

      {/* Insights */}
      {insights.key_findings && (
        <div className="glass-card rounded-2xl p-5 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-400" />
            Key Statistical Findings
          </h3>
          <ul className="space-y-2">
            {insights.key_findings.map((f: string, idx: number) => (
              <li key={idx} className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800 flex items-start gap-2">
                <span className="text-purple-400 font-bold">•</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Outliers Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-amber-400" />
          Interquartile Range (IQR) Outliers Detected
        </h3>
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Column</th>
                <th className="px-4 py-3">Outlier Count</th>
                <th className="px-4 py-3">Lower Bound</th>
                <th className="px-4 py-3">Upper Bound</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {Object.keys(outliers).length > 0 ? (
                Object.entries(outliers).map(([col, data]: [string, any]) => (
                  <tr key={col} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 font-semibold text-white">{col}</td>
                    <td className="px-4 py-3 font-bold text-amber-400">{data.count || 0}</td>
                    <td className="px-4 py-3 font-mono text-slate-400">{data.lower_bound ?? "-"}</td>
                    <td className="px-4 py-3 font-mono text-slate-400">{data.upper_bound ?? "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                    No extreme IQR outliers detected in numerical columns.
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
