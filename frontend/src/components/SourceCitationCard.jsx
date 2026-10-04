import React from 'react';
import { FileText, ExternalLink, Tag, Calendar, Layers } from 'lucide-react';

export default function SourceCitationCard({ citation }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-300 shadow-sm text-xs hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center space-x-2 truncate">
          <FileText className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-semibold text-slate-100 truncate">
            {citation.scheme_name}
          </span>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-emerald-400 border border-slate-700 shrink-0">
          Page {citation.page_number} • Chunk {citation.chunk_index}
        </span>
      </div>

      <p className="text-slate-300 italic bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 mb-2.5 font-mono text-[11px] leading-relaxed">
        "{citation.snippet}"
      </p>

      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1">
            <Tag className="w-3 h-3 text-slate-500" />
            <span>{citation.document_name}</span>
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
            {citation.category}
          </span>
        </div>

        {citation.source_url && (
          <a
            href={citation.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 text-emerald-400 hover:text-emerald-300 hover:underline font-medium"
          >
            <span>Official Portal</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
}
