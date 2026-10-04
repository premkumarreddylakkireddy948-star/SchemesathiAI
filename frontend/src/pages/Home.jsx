import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Bot, 
  Search, 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  CheckCircle2, 
  FileText, 
  SlidersHorizontal, 
  Bookmark, 
  Database, 
  Layers, 
  ChevronRight,
  GraduationCap,
  Tractor,
  Home as HomeIcon,
  Briefcase,
  HeartPulse
} from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/navigator?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/navigator');
    }
  };

  const categories = [
    { name: 'Education & Scholarships', icon: GraduationCap, color: 'from-blue-500 to-indigo-600' },
    { name: 'Agriculture & Farming', icon: Tractor, color: 'from-emerald-500 to-teal-600' },
    { name: 'Housing & Urban Dev', icon: HomeIcon, color: 'from-amber-500 to-orange-600' },
    { name: 'Healthcare & Insurance', icon: HeartPulse, color: 'from-rose-500 to-pink-600' },
    { name: 'Business & Loans', icon: Briefcase, color: 'from-purple-500 to-indigo-600' },
  ];

  return (
    <div className="space-y-16 pb-16">
      
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-slate-950 text-white pt-20 pb-24 border-b border-slate-800">
        {/* Background glow graphics */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-500/15 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-[300px] h-[300px] bg-indigo-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-6 shadow-lg shadow-emerald-500/10 animate-fade-in">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agentic RAG-Powered Government Navigator</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight max-w-4xl mx-auto">
            Discover Government Schemes Tailored to Your Situation with{' '}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              SchemeSathi AI
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto mb-10 font-normal leading-relaxed">
            An intelligent AI platform using Vector RAG and Autonomous Tools to search official guidelines, evaluate potential eligibility criteria, and extract document checklists.
          </p>

          {/* Large AI Search Box */}
          <form onSubmit={handleSearchSubmit} className="max-w-3xl mx-auto mb-8">
            <div className="relative flex items-center bg-slate-900/90 border border-slate-700/80 rounded-2xl p-2 shadow-2xl focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-500/30 transition-all backdrop-blur-md">
              <Search className="w-6 h-6 text-slate-400 ml-3 shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., I am a college student from Tamil Nadu with ₹2.5 lakh family income..."
                className="w-full bg-transparent border-0 text-white placeholder-slate-400 text-sm sm:text-base focus:outline-none focus:ring-0 px-4 py-2.5"
              />
              <button
                type="submit"
                className="inline-flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold text-sm hover:from-emerald-600 hover:to-teal-700 transition-all shadow-lg shadow-emerald-500/25 shrink-0"
              >
                <span>Find My Schemes</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Sample Prompts */}
          <div className="flex flex-wrap justify-center items-center gap-2 text-xs text-slate-400 max-w-3xl mx-auto">
            <span className="font-semibold text-slate-500">Try searching:</span>
            {[
              "Tamil Nadu college SC scholarship",
              "PM KISAN farmer ₹6000 rules",
              "PMAY housing loan subsidy for EWS",
            ].map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => navigate(`/navigator?q=${encodeURIComponent(prompt)}`)}
                className="px-3 py-1 rounded-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-emerald-400 transition-colors"
              >
                "{prompt}"
              </button>
            ))}
          </div>

        </div>
      </section>

      {/* CATEGORY EXPLORER PILLS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Explore by Category</h2>
            <p className="text-sm text-slate-500">Browse verified government programs by sector</p>
          </div>
          <Link to="/explorer" className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center space-x-1">
            <span>View All Schemes</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {categories.map((cat, i) => {
            const Icon = cat.icon;
            return (
              <Link
                key={i}
                to={`/explorer?category=${encodeURIComponent(cat.name)}`}
                className="group bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all text-center flex flex-col items-center justify-center space-y-3"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cat.color} text-white flex items-center justify-center shadow-md group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6" />
                </div>
                <span className="font-bold text-xs text-slate-800 group-hover:text-emerald-700 transition-colors">
                  {cat.name}
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* FEATURE CARDS SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-slate-900 mb-3">
            Core AI Platform Capabilities
          </h2>
          <p className="text-slate-600 text-sm leading-relaxed">
            SchemeSathi AI integrates Retrieval-Augmented Generation (RAG) with LangGraph function calling tools to deliver verified answers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">AI Navigator Chat</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Describe your situation in natural language. The agent extracts key parameters, executes tools, and generates grounded responses.
            </p>
            <Link to="/navigator" className="inline-flex items-center space-x-1.5 text-xs font-bold text-emerald-600 hover:text-emerald-700">
              <span>Start Chatting</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-200 flex items-center justify-center">
              <SlidersHorizontal className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Scheme Comparison</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Select multiple schemes and compare eligibility, financial benefits, income caps, and application workflows side by side.
            </p>
            <Link to="/compare" className="inline-flex items-center space-x-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700">
              <span>Compare Schemes</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all space-y-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Document Checklist</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Keep track of mandatory certificates, mark sheets, income proofs, and land records with interactive status toggles.
            </p>
            <Link to="/checklist" className="inline-flex items-center space-x-1.5 text-xs font-bold text-amber-600 hover:text-amber-700">
              <span>Manage Checklist</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>
      </section>

      {/* RAG & ARCHITECTURE EXPLANATION */}
      <section className="bg-slate-900 text-white py-16 border-y border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-400">System Architecture</span>
            <h2 className="text-3xl font-extrabold text-white mt-1 mb-4">
              Real RAG Pipeline & Agentic Tool Execution
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              No hard-coded chatbot responses. Every answer is retrieved dynamically from vectorized official document guidelines using Qdrant & LangGraph.
            </p>
          </div>

          {/* Architecture diagram steps */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
            
            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold text-sm flex items-center justify-center mx-auto mb-2">1</div>
              <h4 className="font-bold text-sm text-white">Document Ingestion</h4>
              <p className="text-xs text-slate-400">PDF/TXT guidelines parsed, cleaned & chunked into 600-char segments.</p>
            </div>

            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold text-sm flex items-center justify-center mx-auto mb-2">2</div>
              <h4 className="font-bold text-sm text-white">Vector Embeddings</h4>
              <p className="text-xs text-slate-400">384-dimensional dense vectors stored in Qdrant Vector Database.</p>
            </div>

            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold text-sm flex items-center justify-center mx-auto mb-2">3</div>
              <h4 className="font-bold text-sm text-white">LangGraph Agent</h4>
              <p className="text-xs text-slate-400">Analyzes user prompt & routes execution to specialized agent tools.</p>
            </div>

            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold text-sm flex items-center justify-center mx-auto mb-2">4</div>
              <h4 className="font-bold text-sm text-white">Top-K Retrieval</h4>
              <p className="text-xs text-slate-400">Cosine similarity search retrieves exact policy chunks & metadata.</p>
            </div>

            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold text-sm flex items-center justify-center mx-auto mb-2">5</div>
              <h4 className="font-bold text-sm text-white">Grounded Response</h4>
              <p className="text-xs text-slate-400">LLM synthesizes response backed by official source citations.</p>
            </div>

          </div>
        </div>
      </section>

      {/* DISCLAIMER BANNER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6 text-amber-900">
          <ShieldCheck className="w-10 h-10 text-amber-600 shrink-0" />
          <div className="space-y-1">
            <h4 className="font-bold text-base">Important Government Eligibility Disclaimer</h4>
            <p className="text-xs leading-relaxed text-amber-800">
              SchemeSathi AI assists citizens by analyzing official documentation. We never definitively say "You are eligible." Instead, our AI states: 
              <em> "Based on the information provided, this scheme appears potentially relevant because..."</em> 
              Final eligibility, quota allocation, and sanctioning must be verified directly with the official government authority or designated portal.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}
