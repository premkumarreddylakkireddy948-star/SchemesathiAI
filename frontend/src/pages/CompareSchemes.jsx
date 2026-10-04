import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { SlidersHorizontal, Plus, X, Building2, CheckCircle2, ArrowRight, Loader2 } from 'lucide-react';
import { useSchemeContext } from '../context/SchemeContext';
import { compareSchemesApi, fetchSchemes } from '../services/api';

export default function CompareSchemes() {
  const { compareIds, setCompareIds, toggleCompareScheme } = useSchemeContext();
  const [allSchemes, setAllSchemes] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSelector, setShowSelector] = useState(false);

  useEffect(() => {
    const loadAll = async () => {
      try {
        const data = await fetchSchemes();
        setAllSchemes(data);
        
        // Auto select first 2 if none selected yet
        if (compareIds.length === 0 && data.length >= 2) {
          setCompareIds([data[0].id, data[1].id]);
        }
      } catch (err) {
        console.error("Error loading schemes for comparison:", err);
      }
    };
    loadAll();
  }, []);

  useEffect(() => {
    if (compareIds.length > 0) {
      const loadTable = async () => {
        try {
          setLoading(true);
          const res = await compareSchemesApi(compareIds);
          setTableData(res.comparison_table || []);
        } catch (err) {
          console.error("Error generating comparison matrix:", err);
        } finally {
          setLoading(false);
        }
      };
      loadTable();
    } else {
      setTableData([]);
    }
  }, [compareIds]);

  const selectedSchemes = allSchemes.filter((s) => compareIds.includes(s.id));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <SlidersHorizontal className="w-7 h-7 text-emerald-600" />
            <span>Compare Schemes Side-by-Side</span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Evaluate key parameters, benefits, eligibility caps, and document prerequisites across multiple schemes.
          </p>
        </div>

        <button
          onClick={() => setShowSelector(!showSelector)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white hover:bg-slate-800 text-xs font-bold transition-all shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>{showSelector ? 'Close Scheme Selector' : 'Add Scheme to Compare'}</span>
        </button>
      </div>

      {/* Scheme Selector Drawer */}
      {showSelector && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-md space-y-4">
          <h3 className="font-bold text-sm text-slate-900">Select Schemes to Include in Comparison (Max 4):</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {allSchemes.map((scheme) => {
              const isSelected = compareIds.includes(scheme.id);
              return (
                <button
                  key={scheme.id}
                  onClick={() => toggleCompareScheme(scheme.id)}
                  className={`p-3 rounded-xl border text-left text-xs transition-all flex items-start justify-between space-x-2 ${
                    isSelected
                      ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-semibold shadow-sm'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <div>
                    <span className="font-bold block text-slate-900">{scheme.name}</span>
                    <span className="text-[11px] text-slate-500">{scheme.category}</span>
                  </div>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected Schemes Badges Bar */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-bold text-slate-500 mr-2">Comparing:</span>
        {selectedSchemes.map((s) => (
          <span
            key={s.id}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-white border border-slate-300 text-slate-800 shadow-sm"
          >
            <span>{s.name}</span>
            <button
              onClick={() => toggleCompareScheme(s.id)}
              className="text-slate-400 hover:text-rose-600 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </span>
        ))}
        {compareIds.length === 0 && (
          <span className="text-xs text-slate-400 italic">No schemes selected. Click "Add Scheme to Compare" above.</span>
        )}
      </div>

      {/* Comparison Table */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-500">Generating comparison matrix...</p>
        </div>
      ) : tableData.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm space-y-3">
          <SlidersHorizontal className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-lg font-bold text-slate-800">Select Schemes to Compare</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Choose at least 2 government schemes to view side-by-side eligibility and benefit feature comparisons.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-slate-900 text-white text-xs uppercase tracking-wider">
                <th className="p-4 border-b border-slate-800 w-1/5 font-bold">Feature</th>
                {selectedSchemes.map((s) => (
                  <th key={s.id} className="p-4 border-b border-slate-800 font-bold">
                    <Link to={`/scheme/${s.id}`} className="hover:text-emerald-400 transition-colors block">
                      {s.name}
                    </Link>
                    <span className="text-[10px] text-slate-400 font-normal block mt-0.5">{s.category}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-800">
              {tableData.map((row, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/60'}>
                  <td className="p-4 font-bold text-slate-900 bg-slate-100/50">{row["Feature"]}</td>
                  {selectedSchemes.map((s) => (
                    <td key={s.id} className="p-4 leading-relaxed font-sans whitespace-pre-wrap">
                      {row[s.name] || 'N/A'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}
