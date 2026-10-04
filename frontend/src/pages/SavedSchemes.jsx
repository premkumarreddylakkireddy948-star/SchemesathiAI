import React from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Trash2, ArrowRight, Building2, MapPin, CheckSquare, Loader2 } from 'lucide-react';
import { useSchemeContext } from '../context/SchemeContext';
import SchemeCard from '../components/SchemeCard';

export default function SavedSchemes() {
  const { savedSchemes, loadingSaved, toggleSaveScheme } = useSchemeContext();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
          <Bookmark className="w-7 h-7 text-amber-500 fill-amber-500" />
          <span>My Saved Schemes</span>
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Access your bookmarked government programs, scholarship applications, and checklists.
        </p>
      </div>

      {loadingSaved ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-500">Loading saved bookmarks...</p>
        </div>
      ) : savedSchemes.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm space-y-4">
          <Bookmark className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-lg font-bold text-slate-800">No Saved Schemes Yet</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            You haven't bookmarked any schemes. Browse the Scheme Explorer or ask the AI Navigator to find matching options.
          </p>
          <Link
            to="/explorer"
            className="inline-flex items-center space-x-2 px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20"
          >
            <span>Explore Schemes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedSchemes.map((item) => {
            const scheme = item.scheme;
            if (!scheme) return null;
            return (
              <div key={item.id} className="relative group">
                <SchemeCard scheme={scheme} />
                <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1">
                  <span>Saved on {new Date(item.saved_at).toLocaleDateString()}</span>
                  <span className="italic">{item.notes}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
