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
      <div className="p-8 text-center text-slate-400">
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
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            Exploratory Data Analysis (EDA) & Outliers
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated IQR outlier bounds, statistical moments, and correlation discovery.
          </p>
        </div>

        <a
          href={api.getEDAReportUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition shadow-lg shadow-purple-600/20"
        >
          <Download className="w-4 h-4" />
          Download Full EDA HTML Report
        </a>
      </div>

      {/* Summary Card */}
      {summary && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-2">
          <h3 className="text-sm font-semibold text-purple-400 uppercase tracking-wider">Executive Overview</h3>
          <p className="text-sm text-slate-200 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Insights */}
      {insights.key_findings && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Eye className="w-4 h-4 text-blue-400" />
            Key Exploratory Findings
          </h3>
          <ul className="space-y-2">
            {insights.key_findings.map((item: string, idx: number) => (
              <li key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-sm text-slate-300">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Outliers Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-base font-semibold text-white flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-amber-400" />
          IQR Outlier Detection Summary
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Numeric Feature</th>
                <th className="px-4 py-3">Outlier Count</th>
                <th className="px-4 py-3">Outlier %</th>
                <th className="px-4 py-3">IQR Bounds [Lower, Upper]</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {Object.entries(outliers).map(([col, meta]: [string, any]) => (
                <tr key={col} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 font-medium text-white">{col}</td>
                  <td className="px-4 py-3">{meta.outlier_count ?? 0}</td>
                  <td className="px-4 py-3 font-semibold text-amber-400">
                    {meta.outlier_percentage ?? 0}%
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">
                    [{meta.lower_bound}, {meta.upper_bound}]
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
