import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  CheckSquare, 
  CheckCircle2, 
  XCircle, 
  MinusCircle, 
  FileText, 
  Loader2, 
  Building2, 
  Printer, 
  ArrowRight 
} from 'lucide-react';
import { fetchChecklistByScheme, updateChecklistItemApi, fetchSchemes } from '../services/api';

export default function DocumentChecklist() {
  const [searchParams, setSearchParams] = useSearchParams();
  const schemeIdParam = searchParams.get('scheme_id') || '1';

  const [schemes, setSchemes] = useState([]);
  const [selectedSchemeId, setSelectedSchemeId] = useState(Number(schemeIdParam));
  const [checklist, setChecklist] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSchemesList = async () => {
      try {
        const data = await fetchSchemes();
        setSchemes(data);
        if (data.length > 0 && !schemeIdParam) {
          setSelectedSchemeId(data[0].id);
        }
      } catch (err) {
        console.error("Error fetching schemes list for checklist:", err);
      }
    };
    loadSchemesList();
  }, []);

  useEffect(() => {
    if (selectedSchemeId) {
      const loadChecklist = async () => {
        try {
          setLoading(true);
          const data = await fetchChecklistByScheme(selectedSchemeId);
          setChecklist(data);
        } catch (err) {
          console.error("Error loading checklist:", err);
        } finally {
          setLoading(false);
        }
      };
      loadChecklist();
    }
  }, [selectedSchemeId]);

  const handleStatusChange = async (itemId, newStatus) => {
    try {
      setChecklist((prev) => ({
        ...prev,
        items: prev.items.map((it) => (it.id === itemId ? { ...it, status: newStatus } : it)),
      }));
      await updateChecklistItemApi(itemId, newStatus);
    } catch (err) {
      console.error("Error updating checklist item status:", err);
    }
  };

  const handleNotesChange = async (itemId, notes) => {
    try {
      await updateChecklistItemApi(itemId, checklist.items.find((it) => it.id === itemId).status, notes);
    } catch (err) {
      console.error("Error saving notes:", err);
    }
  };

  // Calculate readiness percentage
  const totalItems = checklist?.items?.length || 0;
  const readyItems = checklist?.items?.filter((it) => it.status === 'Available').length || 0;
  const progressPercent = totalItems > 0 ? Math.round((readyItems / totalItems) * 100) : 0;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <CheckSquare className="w-7 h-7 text-emerald-600" />
            <span>Document Checklist Tracker</span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Track required certificates, mark sheets, and identity proofs for your government scheme application.
          </p>
        </div>

        {/* Scheme Dropdown Selector */}
        <div className="w-full md:w-72">
          <label className="block text-xs font-semibold text-slate-500 mb-1">Select Scheme Checklist:</label>
          <select
            value={selectedSchemeId}
            onChange={(e) => {
              const val = Number(e.target.value);
              setSelectedSchemeId(val);
              setSearchParams({ scheme_id: val });
            }}
            className="w-full p-2.5 bg-white border border-slate-300 rounded-xl text-xs font-bold text-slate-900 focus:outline-none focus:border-emerald-500 shadow-sm"
          >
            {schemes.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-500">Loading document checklist...</p>
        </div>
      ) : !checklist ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
          <p className="text-sm text-slate-500">No checklist available for this scheme.</p>
        </div>
      ) : (
        <div className="space-y-6">
          
          {/* Progress Card */}
          <div className="bg-slate-900 text-white p-6 rounded-2xl border border-slate-800 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-mono uppercase tracking-widest text-emerald-400">Application Readiness</span>
                <h3 className="text-xl font-bold text-white mt-0.5">{checklist.scheme_name}</h3>
              </div>
              <div className="text-right">
                <span className="text-3xl font-extrabold text-emerald-400">{progressPercent}%</span>
                <span className="text-xs text-slate-400 block">{readyItems} of {totalItems} Documents Ready</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden p-0.5 border border-slate-700">
              <div
                className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* Checklist Items Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs font-bold text-slate-700">
              <span>Required Document Name</span>
              <span>Document Status Tracker</span>
            </div>

            <div className="divide-y divide-slate-100">
              {checklist.items.map((item) => (
                <div key={item.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/50 transition-colors">
                  <div className="flex items-start space-x-3">
                    <FileText className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-sm text-slate-900">{item.document_name}</h4>
                      <input
                        type="text"
                        placeholder="Add note (e.g. Issued by Mamlatdar Tahsildar Office)..."
                        defaultValue={item.notes || ''}
                        onBlur={(e) => handleNotesChange(item.id, e.target.value)}
                        className="text-xs text-slate-500 bg-transparent border-b border-slate-200 focus:border-emerald-500 focus:outline-none w-full max-w-sm mt-1"
                      />
                    </div>
                  </div>

                  {/* Status Toggle Buttons */}
                  <div className="flex items-center space-x-1.5 shrink-0">
                    <button
                      onClick={() => handleStatusChange(item.id, 'Available')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                        item.status === 'Available'
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Available</span>
                    </button>

                    <button
                      onClick={() => handleStatusChange(item.id, 'Missing')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                        item.status === 'Missing'
                          ? 'bg-rose-600 text-white shadow-sm'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Missing</span>
                    </button>

                    <button
                      onClick={() => handleStatusChange(item.id, 'Not Applicable')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                        item.status === 'Not Applicable'
                          ? 'bg-slate-700 text-white shadow-sm'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      <MinusCircle className="w-3.5 h-3.5" />
                      <span>N/A</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
