"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Database, CheckCircle2, Clock, Bot, AlertCircle, LogIn, LogOut, User } from "lucide-react";
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
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const isCompleted = status === "completed";
  const isProcessing = status === "processing" || status === "uploaded";
  const isFailed = status === "failed";

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api.getMe()
        .then((res: any) => {
          if (res.data) setUser(res.data);
        })
        .catch(() => {
          // Token expired or invalid
          localStorage.removeItem("access_token");
          setUser(null);
        });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <header className="border-b border-slate-800/80 bg-[#0b0f19]/80 backdrop-blur-xl px-6 py-3.5 sticky top-0 z-30 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-500 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-blue-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <span className="font-bold text-base tracking-tight text-white hidden sm:inline-block">AutoDS</span>
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold text-white tracking-tight">Workspace</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300">
              {datasetId ? datasetName : "No Dataset Loaded"}
            </span>
          </div>
          {datasetId && (
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              ID: {datasetId}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Status Indicator */}
        {datasetId ? (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300">
            {isCompleted && (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-medium">Pipeline Ready</span>
              </>
            )}
            {isProcessing && (
              <>
                <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                <span>Processing Pipeline...</span>
              </>
            )}
            {isFailed && (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                <span className="text-red-400 font-medium">Pipeline Failed</span>
              </>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
            <span>Awaiting Upload</span>
          </div>
        )}

        <button
          onClick={onUploadClick}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 cursor-pointer"
        >
          <Database className="w-3.5 h-3.5" />
          Upload Dataset
        </button>

        {/* User Account / Auth Toggle */}
        {user ? (
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 font-medium">
              <User className="w-3.5 h-3.5 text-blue-400" />
              <span className="max-w-[100px] truncate">{user.name || user.email}</span>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="p-1.5 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <LogIn className="w-3.5 h-3.5 text-slate-400" />
            Log In
          </Link>
        )}
      </div>
    </header>
  );
};
