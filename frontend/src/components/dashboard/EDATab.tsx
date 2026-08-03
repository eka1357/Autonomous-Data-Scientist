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
      <div className="panel-card p-12 text-center text-slate-500 text-sm">
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
      <div className="panel-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-600" />
            Exploratory Data Analysis (EDA) & Outliers
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            IQR outlier bounds, statistical moments, and correlation discovery.
          </p>
        </div>

        <a
          href={api.getEDAReportUrl(datasetId)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          Download EDA HTML Report
        </a>
      </div>

      {/* Summary Card */}
      {summary && (
        <div className="panel-card p-5 space-y-2">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Executive Overview</h3>
          <p className="text-xs text-slate-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Insights */}
      {insights.key_findings && (
        <div className="panel-card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
            <Eye className="w-4 h-4 text-blue-600" />
            Key Exploratory Findings
          </h3>
          <ul className="space-y-2">
            {insights.key_findings.map((item: string, idx: number) => (
              <li key={idx} className="p-2.5 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-700">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Outliers Table */}
      <div className="panel-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-amber-600" />
          IQR Outlier Detection Summary
        </h3>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Numeric Feature</th>
                <th className="px-4 py-2.5">Outlier Count</th>
                <th className="px-4 py-2.5">Outlier %</th>
                <th className="px-4 py-2.5">IQR Bounds [Lower, Upper]</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {Object.entries(outliers).map(([col, meta]: [string, any]) => (
                <tr key={col} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-2.5 font-medium text-slate-900">{col}</td>
                  <td className="px-4 py-2.5">{meta.outlier_count ?? 0}</td>
                  <td className="px-4 py-2.5 font-semibold text-amber-700">
                    {meta.outlier_percentage ?? 0}%
                  </td>
                  <td className="px-4 py-2.5 font-mono text-slate-500">
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

