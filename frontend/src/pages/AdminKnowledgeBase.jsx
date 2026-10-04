import React, { useState, useEffect } from 'react';
import { Database, Upload, Trash2, FileText, CheckCircle2, AlertCircle, Loader2, Layers, RefreshCw } from 'lucide-react';
import { fetchDocuments, uploadDocumentApi, deleteDocumentApi, fetchSchemes } from '../services/api';

export default function AdminKnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedSchemeId, setSelectedSchemeId] = useState('');
  const [category, setCategory] = useState('Education & Scholarships');
  const [statusMsg, setStatusMsg] = useState(null);

  const loadDocsAndSchemes = async () => {
    try {
      setLoading(true);
      const [docData, schemeData] = await Promise.all([fetchDocuments(), fetchSchemes()]);
      setDocuments(docData);
      setSchemes(schemeData);
    } catch (err) {
      console.error("Error loading knowledge base data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocsAndSchemes();
  }, []);

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please select a TXT or PDF file to upload.");
      return;
    }

    try {
      setUploading(true);
      setStatusMsg(null);
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (selectedSchemeId) formData.append('scheme_id', selectedSchemeId);
      formData.append('category', category);

      const res = await uploadDocumentApi(formData);
      setStatusMsg({ type: 'success', text: `Document '${res.document_name}' uploaded and indexed (${res.chunk_count} vector chunks).` });
      setSelectedFile(null);
      loadDocsAndSchemes();
    } catch (err) {
      console.error("Upload error:", err);
      setStatusMsg({ type: 'error', text: 'Document upload failed. Make sure the file is a valid TXT or PDF.' });
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDoc = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete '${name}' and purge its vector chunks from Qdrant?`)) return;
    try {
      await deleteDocumentApi(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      setStatusMsg({ type: 'success', text: `Deleted '${name}' from Qdrant vector database.` });
    } catch (err) {
      console.error("Delete document error:", err);
      setStatusMsg({ type: 'error', text: 'Failed to delete document.' });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <Database className="w-7 h-7 text-emerald-600" />
            <span>Admin RAG Knowledge Base</span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Manage official policy guidelines, PDF guidelines, and Qdrant vector embeddings indexing.
          </p>
        </div>

        <button
          onClick={loadDocsAndSchemes}
          className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
          title="Refresh List"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {statusMsg && (
        <div
          className={`p-4 rounded-xl text-xs font-semibold flex items-center space-x-2 ${
            statusMsg.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
              : 'bg-rose-50 text-rose-800 border border-rose-200'
          }`}
        >
          {statusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
          <span>{statusMsg.text}</span>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-lg space-y-4">
        <h3 className="font-bold text-base text-white flex items-center space-x-2">
          <Upload className="w-5 h-5 text-emerald-400" />
          <span>Ingest New Document into Vector Store</span>
        </h3>

        <form onSubmit={handleUploadSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Select File (TXT / PDF)</label>
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="w-full text-xs text-slate-300 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Link to Scheme (Optional)</label>
            <select
              value={selectedSchemeId}
              onChange={(e) => setSelectedSchemeId(e.target.value)}
              className="w-full p-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="">General Policy Document</option>
              {schemes.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full p-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="Education & Scholarships">Education & Scholarships</option>
              <option value="Agriculture & Farmer Welfare">Agriculture & Farmer Welfare</option>
              <option value="Housing & Urban Development">Housing & Urban Development</option>
              <option value="Healthcare & Insurance">Healthcare & Insurance</option>
              <option value="Business & Credit">Business & Credit</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={uploading || !selectedFile}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition-all shadow-md shadow-emerald-600/30 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Chunking & Embedding...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload & Index</span>
                </>
              )}
            </button>
          </div>

        </form>
      </div>

      {/* Documents List Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-2">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs font-bold text-slate-700">
          <span>Ingested Guideline Files</span>
          <span>Indexed Qdrant Vectors</span>
        </div>

        {loading ? (
          <div className="py-16 text-center space-y-2">
            <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
            <p className="text-xs text-slate-500 font-medium">Loading documents inventory...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs">
            No documents uploaded yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
                
                <div className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-slate-900">{doc.document_name}</h4>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-400 mt-0.5">
                      <span>Category: <strong>{doc.category}</strong></span>
                      <span>•</span>
                      <span>Uploaded {new Date(doc.upload_date).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 shrink-0">
                  <span className="px-2.5 py-1 rounded-md font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {doc.chunk_count} Chunks Indexed
                  </span>

                  <button
                    onClick={() => handleDeleteDoc(doc.id, doc.document_name)}
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Delete Document & Purge Vectors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
