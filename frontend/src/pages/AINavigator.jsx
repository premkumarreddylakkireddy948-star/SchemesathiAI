import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Bot, 
  User, 
  Send, 
  SlidersHorizontal, 
  Loader2
} from 'lucide-react';
import { chatWithAgent, API_BASE_URL } from '../services/api';
import { useSchemeContext } from '../context/SchemeContext';
import ConfigWarningBanner from '../components/ConfigWarningBanner';

export default function AINavigator() {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const { userProfile, setUserProfile } = useSchemeContext();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'agent',
      content: "Namaste! I am **SchemeSathi AI**, your intelligent guide for Indian government schemes, scholarships, and welfare benefits.\n\nTell me about your situation (e.g., your state, education level, category, or annual income), or ask any question about government programs, and I will find verified details for you.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle auto-send if query parameter is present from homepage search
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      handleSendMessage(initialQuery.trim());
    }
  }, [initialQuery]);

  const handleSendMessage = async (textToSend = null) => {
    const query = textToSend || inputMessage;
    if (!query || !query.trim() || loading) return;

    const userMsgId = Date.now().toString();
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage('');
    setLoading(true);

    try {
      const data = await chatWithAgent(query, conversationId, userProfile);
      setConversationId(data.conversation_id);

      const agentMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        content: data.message || data.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      console.error("Chat API error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'agent',
          content: `Sorry, I encountered a communication issue with the backend server (${API_BASE_URL}). Please verify that the backend service is healthy.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    "What is PM-KISAN and who can benefit from it? Give me the official government website.",
    "I am a college student from Tamil Nadu with a family income of ₹2.5 lakh per year. What government scholarships may be relevant to me? Give basic details and official application links.",
    "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process.",
    "What is the latest PM-KISAN update? Search official government sources.",
    "Create a document checklist for PM-KISAN."
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Header & Profile Controls */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6 text-emerald-600" />
            <h1 className="text-2xl font-extrabold text-slate-900">AI Navigator</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Verified Government Sources
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Grounded AI search & eligibility guide across official Indian government welfare programs
          </p>
        </div>

        {/* User Context Bar */}
        <div className="flex items-center space-x-2 text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
          <span className="font-semibold text-slate-700">Citizen Context:</span>
          <span className="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-800 font-medium">
            📍 {userProfile.state}
          </span>
          <span className="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-800 font-medium">
            🏷️ {userProfile.category}
          </span>
          <span className="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-800 font-medium">
            💰 ₹{userProfile.annual_income?.toLocaleString('en-IN')}/yr
          </span>
          <button
            onClick={() => setShowProfileModal(!showProfileModal)}
            className="p-1.5 rounded-lg text-emerald-700 hover:bg-emerald-50 font-bold transition-colors ml-1"
            title="Edit Context Profile"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {showProfileModal && (
        <div className="bg-slate-900 text-white p-5 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
          <h4 className="font-bold text-sm text-emerald-400 flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4" />
            <span>Customize Citizen Context Profile for AI Reasoning</span>
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">State Domicile</label>
              <select
                value={userProfile.state}
                onChange={(e) => setUserProfile({ ...userProfile, state: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Tamil Nadu">Tamil Nadu</option>
                <option value="Gujarat">Gujarat</option>
                <option value="All India">All India / Central</option>
                <option value="Maharashtra">Maharashtra</option>
                <option value="Karnataka">Karnataka</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Category</label>
              <select
                value={userProfile.category}
                onChange={(e) => setUserProfile({ ...userProfile, category: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="SC">Scheduled Caste (SC)</option>
                <option value="ST">Scheduled Tribe (ST)</option>
                <option value="OBC">Other Backward Class (OBC)</option>
                <option value="General">General Category</option>
                <option value="EWS">EWS</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Annual Family Income (₹)</label>
              <input
                type="number"
                value={userProfile.annual_income}
                onChange={(e) => setUserProfile({ ...userProfile, annual_income: Number(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Occupation / Status</label>
              <select
                value={userProfile.occupation}
                onChange={(e) => setUserProfile({ ...userProfile, occupation: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Student">Student (Higher Ed)</option>
                <option value="Farmer">Farmer / Agriculture</option>
                <option value="Worker">Worker / Labourer</option>
                <option value="Entrepreneur">Entrepreneur / Business</option>
              </select>
            </div>
          </div>
        </div>
      )}

      <ConfigWarningBanner />

      {/* Main Chat Interface Container */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[650px]">
        
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 bg-slate-50/50">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-slate-900 text-white'
                    : 'bg-emerald-600 text-white'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              {/* Message Content Container */}
              <div className={`max-w-3xl space-y-3 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                
                {/* Text Bubble */}
                <div
                  className={`p-4 sm:p-5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-slate-900 text-white rounded-tr-none'
                      : 'bg-white text-slate-900 border border-slate-200 rounded-tl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans space-y-2">
                    {msg.content}
                  </div>
                  <div className={`text-[10px] mt-2 flex items-center justify-end space-x-1 ${
                    msg.sender === 'user' ? 'text-slate-400' : 'text-slate-400'
                  }`}>
                    <span>{msg.timestamp}</span>
                  </div>
                </div>

              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex items-start space-x-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm animate-pulse">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center space-x-3 text-slate-600 text-xs font-medium">
                <Loader2 className="w-4 h-4 text-emerald-600 animate-spin" />
                <span>Searching official government schemes & analyzing details...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Box & Action Footer */}
        <div className="p-4 border-t border-slate-200 bg-white space-y-3">
          
          {/* Sample Chip Shortcuts */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
            <span className="text-slate-400 font-medium shrink-0">Sample Queries:</span>
            {sampleQueries.map((sample, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(sample)}
                className="px-3 py-1 rounded-full bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 transition-colors whitespace-nowrap shrink-0 border border-slate-200"
              >
                {sample.slice(0, 45)}...
              </button>
            ))}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask SchemeSathi AI about scholarships, farming grants, housing subsidies..."
              disabled={loading}
              className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold transition-all shadow-md shadow-emerald-600/30 disabled:opacity-50 shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>

        </div>

      </div>
    </div>
  );
}
