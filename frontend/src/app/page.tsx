import Link from "next/link";
import { Sparkles, Database, Cpu, BarChart3, ShieldCheck } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-8 md:p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-800 bg-gradient-to-b from-zinc-900 pb-6 pt-8 backdrop-blur-2xl md:static md:w-auto md:rounded-xl md:border md:bg-gray-900/50 md:p-4">
          AutoDS Platform &nbsp;<code className="font-mono font-bold text-blue-400">v0.1.0-bootstrap</code>
        </p>
      </div>

      <div className="relative flex place-items-center flex-col text-center my-16">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          Autonomous Data Science Engine
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent max-w-3xl">
          Transform Raw Data into Actionable Insights
        </h1>
        <p className="mt-6 text-lg text-slate-400 max-w-2xl">
          Upload datasets, receive automated data cleaning proposals, EDA visualizations, AutoML benchmark comparisons, and executive reports without writing code.
        </p>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:grid-cols-4 lg:text-left gap-4">
        <div className="group rounded-xl border border-gray-800 bg-slate-900/40 p-6 transition-all hover:border-blue-500/50">
          <Database className="w-8 h-8 text-blue-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Data Cleaning</h2>
          <p className="text-sm text-slate-400">Automated profiling with human-in-the-loop diff approval.</p>
        </div>

        <div className="group rounded-xl border border-gray-800 bg-slate-900/40 p-6 transition-all hover:border-purple-500/50">
          <BarChart3 className="w-8 h-8 text-purple-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Out-of-Core EDA</h2>
          <p className="text-sm text-slate-400">High performance statistics powered by DuckDB.</p>
        </div>

        <div className="group rounded-xl border border-gray-800 bg-slate-900/40 p-6 transition-all hover:border-emerald-500/50">
          <Cpu className="w-8 h-8 text-emerald-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">AutoML Engine</h2>
          <p className="text-sm text-slate-400">Regression, classification, & SHAP explainability.</p>
        </div>

        <div className="group rounded-xl border border-gray-800 bg-slate-900/40 p-6 transition-all hover:border-cyan-500/50">
          <ShieldCheck className="w-8 h-8 text-cyan-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">RAG Dataset Chat</h2>
          <p className="text-sm text-slate-400">Ask natural language queries over vector embeddings.</p>
        </div>
      </div>
    </main>
  );
}
