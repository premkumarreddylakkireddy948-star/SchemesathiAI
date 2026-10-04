import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import AINavigator from './pages/AINavigator';
import SchemeExplorer from './pages/SchemeExplorer';
import SchemeDetails from './pages/SchemeDetails';
import CompareSchemes from './pages/CompareSchemes';
import SavedSchemes from './pages/SavedSchemes';
import DocumentChecklist from './pages/DocumentChecklist';
import AdminKnowledgeBase from './pages/AdminKnowledgeBase';
import { SchemeProvider } from './context/SchemeContext';

export default function App() {
  return (
    <SchemeProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/navigator" element={<AINavigator />} />
              <Route path="/explorer" element={<SchemeExplorer />} />
              <Route path="/scheme/:id" element={<SchemeDetails />} />
              <Route path="/compare" element={<CompareSchemes />} />
              <Route path="/saved" element={<SavedSchemes />} />
              <Route path="/checklist" element={<DocumentChecklist />} />
              <Route path="/admin" element={<AdminKnowledgeBase />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </SchemeProvider>
  );
}
