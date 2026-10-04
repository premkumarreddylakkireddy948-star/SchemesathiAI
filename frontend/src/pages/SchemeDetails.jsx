import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  IndianRupee, 
  FileText, 
  Bookmark, 
  ExternalLink, 
  CheckSquare, 
  SlidersHorizontal,
  ArrowLeft,
  Loader2,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { fetchSchemeById } from '../services/api';
import { useSchemeContext } from '../context/SchemeContext';
import EligibilityBadge from '../components/EligibilityBadge';

export default function SchemeDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { savedSchemes, toggleSaveScheme, compareIds, toggleCompareScheme } = useSchemeContext();

  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('eligibility');

  useEffect(() => {
    const loadDetails = async () => {
      try {
        setLoading(true);
        const data = await fetchSchemeById(id);
        setScheme(data);
      } catch (err) {
        console.error("Error loading scheme details:", err);
      } finally {
        setLoading(false);
      }
    };
    loadDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3">
        <Loader2 className="w-10 h-10 text-emerald-600 animate-spin mx-auto" />
        <p className="text-sm font-medium text-slate-500">Loading scheme guidelines...</p>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-800">Scheme Not Found</h2>
        <p className="text-sm text-slate-500">The requested scheme ID could not be retrieved from the database.</p>
        <Link to="/explorer" className="inline-flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Explorer</span>
        </Link>
      </div>
    );
  }

  const isSaved = savedSchemes.some((s) => s.scheme_id === scheme.id) || scheme.is_saved;
  const isCompared = compareIds.includes(scheme.id);

  const parsedDocuments = scheme.required_documents
    ? scheme.required_documents.split('\n').filter((l) => l.strip && l.strip())
    : [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-emerald-700 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Directory</span>
      </button>

      {/* Main Header Banner */}
      <div className="bg-slate-900 text-white rounded-3xl p-8 border border-slate-800 shadow-xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-md text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              {scheme.scheme_code}
            </span>
            <span className="px-3 py-1 rounded-md text-xs font-semibold bg-slate-800 text-slate-300">
              {scheme.category}
            </span>
          </div>

          <span className="flex items-center space-x-1.5 text-xs font-semibold px-3 py-1 rounded-md bg-slate-800 text-slate-200">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <span>{scheme.state}</span>
          </span>
        </div>

        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-2">
            {scheme.name}
          </h1>
          <p className="text-sm font-medium text-slate-400 flex items-center space-x-2">
            <Building2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{scheme.ministry_or_department}</span>
          </p>
        </div>

        {/* Action Buttons Bar */}
        <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => toggleSaveScheme(scheme.id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                isSaved
                  ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
                  : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-slate-950' : ''}`} />
              <span>{isSaved ? 'Saved to Bookmarks' : 'Save Scheme'}</span>
            </button>

            <button
              onClick={() => toggleCompareScheme(scheme.id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                isCompared
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                  : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>{isCompared ? 'Comparing' : 'Add to Compare'}</span>
            </button>

            <Link
              to={`/checklist?scheme_id=${scheme.id}`}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-600/20 flex items-center space-x-2"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Document Checklist</span>
            </Link>
          </div>

          {scheme.official_portal_url && (
            <a
              href={scheme.official_portal_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-white text-slate-950 hover:bg-slate-100 text-xs font-bold transition-colors"
            >
              <span>Official Portal</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-2 flex overflow-x-auto gap-2 no-scrollbar">
        {[
          { id: 'overview', label: 'Summary & Overview' },
          { id: 'eligibility', label: 'Eligibility Criteria' },
          { id: 'benefits', label: 'Financial Benefits' },
          { id: 'documents', label: 'Required Documents' },
          { id: 'process', label: 'Application Process' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Section */}
      <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm space-y-6">
        
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Summary & Objectives</h3>
            <p className="text-sm text-slate-700 leading-relaxed font-sans">{scheme.summary}</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100 text-xs">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1">State Domicile</span>
                <span className="font-bold text-slate-800 text-sm">{scheme.state}</span>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1">Income Limit</span>
                <span className="font-bold text-slate-800 text-sm">
                  {scheme.income_limit ? `₹${scheme.income_limit.toLocaleString('en-IN')}/year` : 'No Income Cap'}
                </span>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1">Category</span>
                <span className="font-bold text-slate-800 text-sm">{scheme.category}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'eligibility' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-900">Official Eligibility Guidelines</h3>
              <EligibilityBadge isPotentiallyEligible={true} label="Verification Required" />
            </div>
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
              {scheme.eligibility_criteria}
            </div>
          </div>
        )}

        {activeTab === 'benefits' && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Welfare & Financial Assistance</h3>
            <div className="bg-emerald-50 p-6 rounded-xl border border-emerald-200 text-sm text-emerald-900 leading-relaxed whitespace-pre-wrap font-sans font-medium">
              {scheme.benefits}
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-900">Mandatory Required Documents</h3>
              <Link
                to={`/checklist?scheme_id=${scheme.id}`}
                className="text-xs font-bold text-emerald-600 hover:text-emerald-700 flex items-center space-x-1"
              >
                <CheckSquare className="w-4 h-4" />
                <span>Track in My Checklist</span>
              </Link>
            </div>
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
              <ul className="space-y-3 text-sm text-slate-800">
                {parsedDocuments.map((doc, idx) => (
                  <li key={idx} className="flex items-start space-x-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{doc.replace(/^[- *1234567890.]*/, '')}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'process' && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Application Workflow</h3>
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
              {scheme.application_process}
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
