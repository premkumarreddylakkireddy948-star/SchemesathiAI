import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, SlidersHorizontal, RefreshCw, Building2, MapPin, Filter, Loader2 } from 'lucide-react';
import { fetchSchemes } from '../services/api';
import SchemeCard from '../components/SchemeCard';

export default function SchemeExplorer() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get('category') || 'All';
  const initialSearch = searchParams.get('search') || '';

  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(initialSearch);
  const [category, setCategory] = useState(initialCategory);
  const [state, setState] = useState('All India');

  const categories = [
    'All',
    'Education & Scholarships',
    'Agriculture & Farmer Welfare',
    'Housing & Urban Development',
    'Healthcare & Insurance',
    'School Education & Scholarships',
    'Higher Education & State Scholarship',
    'Entrepreneurship & Business Credit',
  ];

  const states = ['All India', 'Tamil Nadu', 'Gujarat', 'Maharashtra', 'Karnataka'];

  const loadSchemes = async () => {
    try {
      setLoading(true);
      const data = await fetchSchemes({ category, state, search });
      setSchemes(data);
    } catch (err) {
      console.error("Error loading schemes:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchemes();
  }, [category, state]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadSchemes();
  };

  const handleResetFilters = () => {
    setSearch('');
    setCategory('All');
    setState('All India');
    setSearchParams({});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Scheme Explorer</h1>
        <p className="text-slate-500 text-sm mt-1">
          Search and filter verified Indian government welfare programs, scholarships, and benefits.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-12 gap-4">
          
          {/* Search Box */}
          <div className="sm:col-span-5 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search scheme name, eligibility, keywords..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Category Filter */}
          <div className="sm:col-span-3">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 focus:outline-none focus:border-emerald-500"
            >
              <option value="All">All Categories</option>
              {categories.filter((c) => c !== 'All').map((c, i) => (
                <option key={i} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* State Filter */}
          <div className="sm:col-span-2">
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 focus:outline-none focus:border-emerald-500"
            >
              {states.map((st, i) => (
                <option key={i} value={st}>{st}</option>
              ))}
            </select>
          </div>

          {/* Search & Reset Buttons */}
          <div className="sm:col-span-2 flex items-center space-x-2">
            <button
              type="submit"
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm transition-colors shadow-sm"
            >
              Filter
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl transition-colors"
              title="Reset Filters"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>

        </form>
      </div>

      {/* Results Count & Loader */}
      {loading ? (
        <div className="py-16 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-500">Fetching government schemes catalog...</p>
        </div>
      ) : schemes.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm space-y-3">
          <Building2 className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-lg font-bold text-slate-800">No Schemes Match Your Filter</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Try broadening your category or state criteria, or reset your search parameters.
          </p>
          <button
            onClick={handleResetFilters}
            className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium px-1">
            <span>Showing {schemes.length} Government Schemes</span>
            <span>State Filter: {state}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schemes.map((scheme) => (
              <SchemeCard key={scheme.id} scheme={scheme} />
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
