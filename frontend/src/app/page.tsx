import Link from "next/link";
import {
  Database,
  Cpu,
  BarChart3,
  ShieldCheck,
  Bot,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
              <Bot className="w-4 h-4" />
            </div>
            <span className="font-semibold text-lg text-slate-900 tracking-tight">
              AutoDS
            </span>
            <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-slate-100 text-slate-600 border border-slate-200">
              Workspace
            </span>
          </div>

          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs transition"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-16 pb-12 px-6 max-w-4xl mx-auto text-center flex-1 flex flex-col justify-center">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-slate-900 leading-tight">
          Autonomous Data Science & Machine Learning Workspace
        </h1>

        <p className="mt-4 text-base md:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Upload tabular datasets to automatically execute profiling, human-in-the-loop cleaning, exploratory data analysis, ML preprocessing, and competitive model training.
        </p>

        <div className="mt-8 flex items-center justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm shadow-sm transition"
          >
            <span>Open Dashboard Workspace</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Key Features List */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-600 font-medium">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Automated Data Profiling</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Interactive Cleaning</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>AutoML Leaderboard & SHAP</span>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-12 px-6 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="panel-card p-5">
            <div className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center mb-4">
              <Database className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1">Data Cleaning</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Automated duplicate removal, whitespace trimming, and missing value strategy execution.
            </p>
          </div>

          <div className="panel-card p-5">
            <div className="w-9 h-9 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mb-4">
              <BarChart3 className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1">EDA & Reports</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Correlation analysis, distribution histograms, outlier detection, and HTML report exports.
            </p>
          </div>

          <div className="panel-card p-5">
            <div className="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center mb-4">
              <Cpu className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1">AutoML Training</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Model training for Logistic Regression, Random Forest, XGBoost, and LightGBM models.
            </p>
          </div>

          <div className="panel-card p-5">
            <div className="w-9 h-9 rounded-lg bg-amber-50 border border-amber-100 text-amber-600 flex items-center justify-center mb-4">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1">AI Assistant</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Context-aware assistant for dataset querying, summary insights, and model guidance.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 px-6 text-center text-xs text-slate-500 bg-white mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} AutoDS Platform. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="hover:text-slate-900 transition">
              Dashboard
            </Link>
            <a
              href="http://localhost:8000/api/v1/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-slate-900 transition"
            >
              API Docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

