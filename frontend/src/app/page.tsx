"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  Database,
  Cpu,
  BarChart3,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  FileSpreadsheet,
  Layers,
  Bot,
  X,
  Zap,
  TrendingUp,
  Activity,
} from "lucide-react";

export default function Home() {
  const [showAssistantPopover, setShowAssistantPopover] = useState(false);

  return (
    <div className="relative min-h-screen bg-[#0b0f19] text-slate-100 font-sans selection:bg-blue-500 selection:text-white overflow-x-hidden">
      {/* Background Ambient Glows */}
      <div className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-blue-600/15 via-purple-600/10 to-transparent blur-3xl rounded-full opacity-60" />
      <div className="pointer-events-none absolute top-[450px] -right-[150px] w-[500px] h-[500px] bg-cyan-500/10 blur-3xl rounded-full opacity-40" />

      {/* Navigation Header */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#0b0f19]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-500 flex items-center justify-center shadow-md shadow-blue-500/20">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                AutoDS
              </span>
              <span className="px-2.5 py-0.5 text-[11px] font-mono font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0 Production
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="http://localhost:8000/api/v1/docs"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:inline-block text-xs font-medium text-slate-400 hover:text-white transition focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none rounded-md px-2 py-1"
            >
              API Docs
            </a>
            <Link
              href="/login"
              className="text-xs font-semibold text-slate-300 hover:text-white transition px-2.5 py-1.5"
            >
              Log In
            </Link>
            <Link
              href="/register"
              className="hidden sm:inline-block text-xs font-semibold text-blue-400 hover:text-blue-300 transition px-2.5 py-1.5"
            >
              Register
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition-all hover:scale-[1.02] active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none"
            >
              <span>Open Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-12 px-6 max-w-7xl mx-auto z-10">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-mono font-semibold uppercase tracking-wider mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Data Science Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-b from-white via-slate-100 to-slate-300 bg-clip-text text-transparent leading-[1.15]">
            Upload Any Tabular CSV. Get Cleaned Data, Outlier Charts, and AutoML Leaderboards in{" "}
            <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              60 Seconds.
            </span>
          </h1>

          <p className="mt-5 text-base sm:text-lg text-slate-400 leading-relaxed font-normal">
            AutoDS profiles raw files, sanitizes currency symbols, executes out-of-core DuckDB EDA, trains competitive models, and builds interactive SHAP reports without writing Python.
          </p>

          <div className="mt-8 flex items-center justify-center">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:opacity-95 text-white font-semibold text-sm shadow-xl shadow-blue-600/25 transition-all hover:scale-[1.02] focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none"
            >
              <span>Open Dashboard Workspace</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Product In Action Workspace Preview Mockup */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800/80 shadow-2xl space-y-5 max-w-5xl mx-auto motion-reduce:transition-none">
          {/* Workspace Preview Header Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white font-mono">concert_tours_sales.csv</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Pipeline Ready
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                  ID: 4a2d8f9e-11b3-4c5a-8e2b • <span className="text-slate-300 font-bold">25,480 rows</span> • <span className="text-slate-300 font-bold">18 columns</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="text-slate-400">Task: <strong className="text-purple-400">Regression</strong></span>
              <span className="text-slate-400">Target: <strong className="text-blue-400">Actual gross</strong></span>
            </div>
          </div>

          {/* Representative Workspace Visual Snippets */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Snippet 1: Profiling & Coercion */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-blue-400" />
                  Numeric Coercion
                </span>
                <span className="text-emerald-400 font-mono text-[11px]">float64</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] font-mono space-y-1">
                <p className="text-slate-500 line-through">"$736,421,584"</p>
                <p className="text-emerald-400 font-bold">736421584.0</p>
              </div>
              <span className="text-[10px] text-slate-400 block font-mono">100% rows retained (0 deleted)</span>
            </div>

            {/* Snippet 2: AutoML Leaderboard Winner */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-purple-400" />
                  AutoML Benchmark
                </span>
                <span className="text-amber-400 font-mono text-[11px]">🏆 #1 Rank</span>
              </div>
              <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-[11px] font-mono flex items-center justify-between">
                <span className="font-bold text-white">XGBoost Regressor</span>
                <span className="text-emerald-400 font-bold">R²: 0.9420</span>
              </div>
              <span className="text-[10px] text-slate-400 block font-mono">5-Fold CV Mean: 0.9380 ± 0.004</span>
            </div>

            {/* Snippet 3: SHAP Feature Importance */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  SHAP Explainability
                </span>
                <span className="text-cyan-400 font-mono text-[11px]">Top Driver</span>
              </div>
              <div className="space-y-1.5 text-[11px] font-mono">
                <div className="flex justify-between text-slate-300">
                  <span>Actual gross</span>
                  <span className="text-purple-400 font-bold">0.8420</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full w-[84%]" />
                </div>
              </div>
              <span className="text-[10px] text-slate-400 block font-mono">Explainer: shap.TreeExplainer</span>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Feature Cards With Real Artifact Previews */}
      <section className="py-16 px-6 max-w-7xl mx-auto z-10 relative">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Real Pipeline Artifacts Built Automatically
          </h2>
          <p className="mt-2 text-slate-400 text-sm">
            Inspect concrete outputs generated across every phase of the autonomous pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Data Cleaning */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-blue-500/40 transition-all duration-300">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-blue-400 text-xs font-mono font-bold uppercase">
                <Database className="w-4 h-4" />
                <span>Data Cleaning</span>
              </div>
              <h3 className="text-base font-bold text-white">Smart Coercion & Imputation</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Strips currency symbols and commas. Imputes small datasets ($&lt;200$ rows) with median/mode instead of gutting rows.
              </p>
            </div>

            {/* Visual Artifact: Cleaning Diff */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono space-y-1.5">
              <div className="flex justify-between text-slate-400 pb-1 border-b border-slate-800/60 text-[10px]">
                <span>Column</span>
                <span>Before $\rightarrow$ After</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span className="truncate max-w-[80px]">Gross</span>
                <span className="text-emerald-400 font-bold">$124K $\rightarrow$ 124000.0</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span className="truncate max-w-[80px]">Missing</span>
                <span className="text-blue-400 font-bold">Imputed (Median)</span>
              </div>
            </div>
          </div>

          {/* Card 2: EDA & Reports */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-purple-500/40 transition-all duration-300">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-purple-400 text-xs font-mono font-bold uppercase">
                <BarChart3 className="w-4 h-4" />
                <span>EDA & Reports</span>
              </div>
              <h3 className="text-base font-bold text-white">DuckDB EDA & Outliers</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Computes IQR outlier bounds, statistical moments, correlation heatmaps, and downloadable Jinja2 HTML executive reports.
              </p>
            </div>

            {/* Visual Artifact: IQR Bounds */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono space-y-1.5">
              <div className="flex justify-between text-slate-400 pb-1 border-b border-slate-800/60 text-[10px]">
                <span>IQR Bound</span>
                <span>Metric Value</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Lower / Upper</span>
                <span className="text-purple-400 font-bold">24.5 / 88.0</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Outliers Found</span>
                <span className="text-amber-400 font-bold">3 rows (1.2%)</span>
              </div>
            </div>
          </div>

          {/* Card 3: AutoML Training */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-emerald-500/40 transition-all duration-300">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold uppercase">
                <Cpu className="w-4 h-4" />
                <span>AutoML Training</span>
              </div>
              <h3 className="text-base font-bold text-white">Multi-Model Benchmarks</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Trains XGBoost, LightGBM, Random Forest, & Linear models with 5-fold CV and exception diagnostics.
              </p>
            </div>

            {/* Visual Artifact: Leaderboard Snippet */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono space-y-1.5">
              <div className="flex justify-between text-emerald-400 font-bold">
                <span>🏆 XGBoost</span>
                <span>0.9580</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>LightGBM</span>
                <span>0.9440</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>RandomForest</span>
                <span>0.9210</span>
              </div>
            </div>
          </div>

          {/* Card 4: AI Assistant */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition-all duration-300">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold uppercase">
                <ShieldCheck className="w-4 h-4" />
                <span>AI Assistant</span>
              </div>
              <h3 className="text-base font-bold text-white">RAG Chat Assistant</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Queries multi-stage context across profiling, cleaning, EDA, AutoML, and SHAP with real-time SSE streaming citations.
              </p>
            </div>

            {/* Visual Artifact: Chat Snippet */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] space-y-1.5">
              <p className="text-slate-400 font-mono text-[10px]">Q: What drove the model?</p>
              <p className="text-cyan-300 text-[11px] leading-snug">
                "According to <span className="bg-slate-800 px-1 py-0.5 rounded text-blue-300 font-mono">[Model Evaluation]</span>, Actual Gross drove 84% variance."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Floating AI Assistant Chat Icon & Context Popover (Bottom-Right) */}
      <div className="fixed bottom-6 right-6 z-50">
        {/* Context Popover Window */}
        {showAssistantPopover && (
          <div className="mb-3 w-80 glass-card rounded-2xl p-5 border border-slate-800 shadow-2xl space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-500 flex items-center justify-center text-white">
                  <Sparkles className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-white">AI Data Science Assistant</span>
              </div>
              <button
                onClick={() => setShowAssistantPopover(false)}
                className="text-slate-400 hover:text-white transition focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              The AI Assistant operates with full context over uploaded datasets (profiling metrics, cleaning logs, EDA charts, AutoML leaderboards, and SHAP explainability).
            </p>

            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-[11px] text-blue-300 font-mono">
              Please upload a dataset in the workspace to activate real-time chat.
            </div>

            <Link
              href="/dashboard"
              onClick={() => setShowAssistantPopover(false)}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition"
            >
              <span>Open Workspace & Upload File</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {/* Floating Button matching Dashboard AI Assistant Accent (Sparkle/Pulse detail) */}
        <button
          onClick={() => setShowAssistantPopover(!showAssistantPopover)}
          aria-label="Open AI Data Science Assistant Info"
          className="relative group w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 text-blue-400 hover:text-blue-300 hover:border-blue-500/50 flex items-center justify-center shadow-xl shadow-black/40 opacity-85 hover:opacity-100 transition-all duration-300 focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none"
        >
          <Sparkles className="w-6 h-6 transition-transform group-hover:scale-110" />
          {/* Distinct Sparkle / Pulse Badge */}
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-blue-500 border-2 border-[#0b0f19] animate-pulse" />
        </button>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-8 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} AutoDS Autonomous Platform. All rights reserved.</p>
          <div className="flex items-center gap-6 font-mono">
            <Link href="/dashboard" className="hover:text-slate-300 transition">
              Dashboard
            </Link>
            <a
              href="http://localhost:8000/api/v1/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-slate-300 transition"
            >
              API Docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
