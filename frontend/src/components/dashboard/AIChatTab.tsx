"use client";

import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Sparkles, Trash2, FileText } from "lucide-react";
import { api } from "@/lib/api";

interface AIChatTabProps {
  datasetId: string;
}

export const AIChatTab: React.FC<AIChatTabProps> = ({ datasetId }) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchHistory = async () => {
    if (!datasetId) return;
    try {
      const res = await api.getChatHistory(datasetId);
      setMessages(res.data || []);
    } catch {
      setMessages([]);
    }
  };

  useEffect(() => {
    if (datasetId) {
      fetchHistory();
    }
  }, [datasetId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading || !datasetId) return;
    const userMsg = input.trim();
    setInput("");
    setLoading(true);

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", content: userMsg, citations: [] },
    ]);

    try {
      const res = await api.sendChatMessage(datasetId, userMsg, false);
      setMessages((prev) => [...prev, res.data]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: err.message || "Sorry, an error occurred while querying the AI Assistant.",
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!datasetId) return;
    try {
      await api.clearChatHistory(datasetId);
      setMessages([]);
    } catch {
      setMessages([]);
    }
  };

  return (
    <div className="glass-card rounded-2xl flex flex-col h-[650px] overflow-hidden border border-slate-800">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">AI Data Science Assistant</h3>
            <p className="text-xs text-slate-400">Ask natural language questions across dataset artifacts & metrics</p>
          </div>
        </div>

        {datasetId && (
          <button
            onClick={handleClearHistory}
            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition border border-transparent hover:border-red-500/20"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-950/40">
        {!datasetId ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
            <Bot className="w-10 h-10 text-slate-600 mb-2" />
            <p className="text-sm font-bold text-white">No Dataset Loaded</p>
            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              Please upload a dataset to start chatting with the AI Data Science Assistant.
            </p>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
            <Bot className="w-10 h-10 text-blue-500/40 mb-2" />
            <p className="text-sm font-bold text-white">Ask a question about your dataset</p>
            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              e.g., "What is the best performing model?", "How many missing values were filled?", or "Explain key findings."
            </p>
          </div>
        ) : (
          messages.map((m: any, idx: number) => {
            const isUser = m.role === "user";
            return (
              <div key={idx} className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div className={`max-w-xl p-4 rounded-2xl text-xs leading-relaxed ${isUser ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-md shadow-blue-600/10" : "bg-slate-900/90 text-slate-200 border border-slate-800 rounded-bl-none"}`}>
                  <p className="whitespace-pre-wrap">{m.content}</p>

                  {/* Citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Sources:</span>
                      {m.citations.map((c: any, cIdx: number) => (
                        <span key={cIdx} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] bg-slate-800 text-blue-300 border border-slate-700 font-medium">
                          <FileText className="w-2.5 h-2.5" />
                          {c.source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/80">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!datasetId || loading}
            placeholder={datasetId ? "Ask a question..." : "Upload a dataset first..."}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || !datasetId}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white transition shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
