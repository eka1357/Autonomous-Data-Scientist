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
          content: "Sorry, an error occurred while querying the AI Assistant.",
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
    <div className="panel-card flex flex-col h-[650px] overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-blue-600 flex items-center justify-center text-white">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">AI Data Science Assistant</h3>
            <p className="text-xs text-slate-500">Ask natural language questions across dataset artifacts & metrics</p>
          </div>
        </div>

        <button
          onClick={handleClearHistory}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-md transition"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear Chat
        </button>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-white">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500">
            <Bot className="w-10 h-10 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-900">Ask a question about your dataset</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm">
              e.g., "What is the best performing model?", "How many missing values were filled?", or "Explain key findings."
            </p>
          </div>
        ) : (
          messages.map((m: any, idx: number) => {
            const isUser = m.role === "user";
            return (
              <div key={idx} className={`flex gap-2.5 ${isUser ? "justify-end" : "justify-start"}`}>
                {!isUser && (
                  <div className="w-7 h-7 rounded-md bg-slate-100 border border-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div className={`max-w-xl p-3.5 rounded-lg text-xs leading-relaxed ${isUser ? "bg-blue-600 text-white rounded-br-none" : "bg-slate-50 text-slate-800 border border-slate-200 rounded-bl-none"}`}>
                  <p className="whitespace-pre-wrap">{m.content}</p>

                  {/* Citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2.5 pt-2.5 border-t border-slate-200 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Sources:</span>
                      {m.citations.map((c: any, cIdx: number) => (
                        <span key={cIdx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-slate-200/80 text-slate-700 font-medium">
                          <FileText className="w-2.5 h-2.5" />
                          {c.source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {isUser && (
                  <div className="w-7 h-7 rounded-md bg-blue-100 text-blue-700 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Form */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 bg-white border border-slate-300 rounded-md px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-md bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

