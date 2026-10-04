import React from 'react';
import { Bot, ShieldCheck, Cpu, Code, Database, Scale } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                SchemeSathi AI
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-md">
              Agentic RAG-Based Government Scheme & Benefits Navigator. Helping citizens discover 
              potentially relevant Indian welfare programs, scholarships, and financial assistance using 
              vector search, grounding, and autonomous AI tools.
            </p>
            <div className="flex flex-wrap gap-2 text-xs font-mono text-emerald-400 pt-2">
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">React + Vite</span>
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">FastAPI</span>
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">LangGraph Agent</span>
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">Qdrant Vector DB</span>
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">Gemini LLM</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider">Features</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/navigator" className="hover:text-emerald-400 transition-colors">AI Navigator Chat</a></li>
              <li><a href="/explorer" className="hover:text-emerald-400 transition-colors">Browse Scheme Directory</a></li>
              <li><a href="/compare" className="hover:text-emerald-400 transition-colors">Side-by-Side Comparison</a></li>
              <li><a href="/checklist" className="hover:text-emerald-400 transition-colors">Document Checklist</a></li>
              <li><a href="/admin" className="hover:text-emerald-400 transition-colors">RAG Knowledge Base</a></li>
            </ul>
          </div>

          {/* Official Disclaimer */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span>Government Disclaimer</span>
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
              SchemeSathi AI provides recommendations based on indexed official guidelines. 
              <strong> Final scheme eligibility, quota allocations, and benefit disbursements must always be verified with the official government authority or department.</strong>
            </p>
          </div>

        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500">
          <p>© 2026 SchemeSathi AI. Academic & Full-Stack Capstone Project.</p>
          <p className="mt-2 md:mt-0 flex items-center space-x-2">
            <span>Powered by Grounded RAG & LangGraph Tools</span>
          </p>
        </div>

      </div>
    </footer>
  );
}
