"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, Mail, Lock, ArrowRight, AlertCircle, Eye, EyeOff } from "lucide-react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    try {
      setLoading(true);
      setErrorMessage(null);
      const res: any = await api.login({ email, password });
      
      const tokenData = res.data || res;
      if (tokenData.access_token) {
        localStorage.setItem("access_token", tokenData.access_token);
        if (tokenData.refresh_token) {
          localStorage.setItem("refresh_token", tokenData.refresh_token);
        }
        router.push("/dashboard");
      } else {
        setErrorMessage("Authentication failed. No access token returned.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid email or password credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0b0f19] text-slate-100 font-sans flex flex-col items-center justify-center p-6 overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="pointer-events-none absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-gradient-to-b from-blue-600/15 to-purple-600/10 blur-3xl rounded-full opacity-60" />

      {/* Navigation Header Link */}
      <div className="absolute top-6 left-6 flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-500 flex items-center justify-center shadow-md shadow-blue-500/20">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-base tracking-tight text-white">AutoDS</span>
        </Link>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-md glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl space-y-6 z-10">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Welcome Back</h1>
          <p className="text-xs text-slate-400">
            Log in to access your Autonomous Data Science workspace and projects.
          </p>
        </div>

        {/* Error Banner */}
        {errorMessage && (
          <div className="p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2.5 text-xs text-red-400 font-medium">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300">Password</label>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
                className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/25 transition disabled:opacity-50 cursor-pointer"
          >
            <span>{loading ? "Authenticating..." : "Log In to Workspace"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-4 border-t border-slate-800 text-center text-xs text-slate-400 space-y-2">
          <p>
            Don't have an account yet?{" "}
            <Link href="/register" className="text-blue-400 font-semibold hover:underline">
              Create an Account
            </Link>
          </p>
          <p>
            Or proceed directly to{" "}
            <Link href="/dashboard" className="text-purple-400 font-semibold hover:underline">
              Dashboard Guest Mode
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
