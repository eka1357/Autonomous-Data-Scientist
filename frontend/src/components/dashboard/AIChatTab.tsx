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
    try {
      const res = await api.getChatHistory(datasetId);
      setMessages(res.data || []);
    } catch (err) {
      console.error("Chat history fetch error:", err);
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
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setLoading(true);

    // Optimistic UI update
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
          content: "Sorry, an error occurred while querying the RAG Assistant.",
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await api.clearChatHistory(datasetId);
      setMessages([]);
    } catch (err) {
      console.error("Clear chat error:", err);
    }
  };

  return (
    <div className="flex flex-col h-[700px] rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">AI Data Science RAG Assistant</h3>
            <p className="text-xs text-slate-400">Ask natural language questions across all project artifacts & metrics</p>
          </div>
        </div>

        <button
          onClick={handleClearHistory}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition border border-transparent hover:border-red-500/20"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear Chat
        </button>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500">
            <Bot className="w-12 h-12 text-purple-400/40 mb-3" />
            <p className="text-sm font-medium text-slate-300">Ask me anything about your dataset!</p>
            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              e.g., "What is the best performing model?", "How many missing values were filled?", or "Explain key EDA findings."
            </p>
          </div>
        ) : (
          messages.map((m: any, idx: number) => {
            const isUser = m.role === "user";
            return (
              <div key={idx} className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                {!isUser && (
                  <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 shrink-0 h-fit">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div className={`max-w-2xl p-4 rounded-2xl text-sm ${isUser ? "bg-blue-600 text-white rounded-br-none" : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none"}`}>
                  <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>

                  {/* Citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700/60 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Citations:</span>
                      {m.citations.map((c: any, cIdx: number) => (
                        <span key={cIdx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
                          <FileText className="w-2.5 h-2.5" />
                          {c.source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {isUser && (
                  <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0 h-fit">
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
            placeholder="Type your question..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="inline-flex items-center gap-2 px-5 py-3 text-xs font-semibold rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition shadow-lg shadow-purple-600/20 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
