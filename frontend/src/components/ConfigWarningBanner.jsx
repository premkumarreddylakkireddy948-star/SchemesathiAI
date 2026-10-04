import React from 'react';
import { AlertCircle, Key, Server, Cpu, CheckCircle } from 'lucide-react';

export default function ConfigWarningBanner({ isLlmConfigured = true }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-6 shadow-md text-slate-300">
      <div className="flex items-start space-x-3">
        <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shrink-0 mt-0.5">
          <Cpu className="w-5 h-5" />
        </div>
        <div className="flex-1 text-xs space-y-1">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-sm text-white flex items-center space-x-2">
              <span>Agentic RAG Engine Active</span>
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            </h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              Qdrant + LangGraph
            </span>
          </div>
          <p className="text-slate-400">
            System is executing full vector search & LangGraph multi-tool grounding.
            {!isLlmConfigured && (
              <span className="text-amber-300 font-medium ml-1">
                (Note: GEMINI_API_KEY optional. Grounded local reasoning engine active).
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
