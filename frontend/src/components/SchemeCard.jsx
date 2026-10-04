import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  IndianRupee, 
  FileText, 
  Bookmark, 
  ExternalLink, 
  CheckSquare, 
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';
import { useSchemeContext } from '../context/SchemeContext';

export default function SchemeCard({ scheme }) {
  const { savedSchemes, toggleSaveScheme, compareIds, toggleCompareScheme } = useSchemeContext();

  const isSaved = savedSchemes.some((s) => s.scheme_id === scheme.id) || scheme.is_saved;
  const isCompared = compareIds.includes(scheme.id);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col justify-between group">
      <div>
        {/* Badges Header */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
            {scheme.category}
          </span>
          <span className="flex items-center space-x-1 text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>{scheme.state}</span>
          </span>
        </div>

        {/* Title & Ministry */}
        <h3 className="text-lg font-bold text-slate-900 group-hover:text-emerald-700 transition-colors mb-1">
          {scheme.name}
        </h3>
        <p className="text-xs font-medium text-slate-500 mb-3 flex items-center space-x-1">
          <Building2 className="w-3.5 h-3.5" />
          <span>{scheme.ministry_or_department}</span>
        </p>

        {/* Summary */}
        <p className="text-sm text-slate-600 line-clamp-3 mb-4 leading-relaxed">
          {scheme.summary}
        </p>

        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-100 mb-4">
          <div>
            <span className="text-slate-400 block mb-0.5">Income Limit</span>
            <span className="font-semibold text-slate-800 flex items-center">
              {scheme.income_limit ? (
                <>₹{scheme.income_limit.toLocaleString('en-IN')}/yr</>
              ) : (
                'No Income Limit'
              )}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Scheme Code</span>
            <span className="font-mono text-slate-700">{scheme.scheme_code}</span>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-1">
          <button
            onClick={() => toggleSaveScheme(scheme.id)}
            className={`p-2 rounded-lg text-xs font-medium border transition-colors flex items-center space-x-1 ${
              isSaved
                ? 'bg-amber-50 text-amber-700 border-amber-300'
                : 'text-slate-600 hover:bg-slate-100 border-slate-200'
            }`}
            title={isSaved ? 'Remove from Saved' : 'Save Scheme'}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-amber-500 text-amber-600' : ''}`} />
          </button>

          <button
            onClick={() => toggleCompareScheme(scheme.id)}
            className={`p-2 rounded-lg text-xs font-medium border transition-colors flex items-center space-x-1 ${
              isCompared
                ? 'bg-indigo-50 text-indigo-700 border-indigo-300'
                : 'text-slate-600 hover:bg-slate-100 border-slate-200'
            }`}
            title={isCompared ? 'Remove from Compare' : 'Add to Compare'}
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>

          <Link
            to={`/checklist?scheme_id=${scheme.id}`}
            className="p-2 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200 transition-colors"
            title="View Document Checklist"
          >
            <CheckSquare className="w-4 h-4" />
          </Link>
        </div>

        <Link
          to={`/scheme/${scheme.id}`}
          className="inline-flex items-center space-x-1 text-xs font-semibold px-3.5 py-2 rounded-lg bg-slate-900 text-white hover:bg-emerald-600 transition-colors"
        >
          <span>View Details</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
