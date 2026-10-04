import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatWithAgent = async (message, conversationId = null, userContext = null) => {
  const response = await api.post('/chat', {
    message,
    conversation_id: conversationId,
    user_context: userContext,
  });
  return response.data;
};

export const queryKnowledgeBase = async (query, topK = 5, category = null) => {
  const response = await api.post('/query', {
    query,
    top_k: topK,
    category,
  });
  return response.data;
};

export const fetchSchemes = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.category && filters.category !== 'All') params.append('category', filters.category);
  if (filters.state && filters.state !== 'All India') params.append('state', filters.state);
  if (filters.search) params.append('search', filters.search);

  const response = await api.get(`/schemes?${params.toString()}`);
  return response.data;
};

export const fetchSchemeById = async (id) => {
  const response = await api.get(`/schemes/${id}`);
  return response.data;
};

export const compareSchemesApi = async (schemeIds) => {
  const response = await api.post('/schemes/compare', {
    scheme_ids: schemeIds,
  });
  return response.data;
};

export const saveSchemeApi = async (schemeId, notes = '') => {
  const response = await api.post(`/schemes/${schemeId}/save`, {
    scheme_id: schemeId,
    notes,
  });
  return response.data;
};

export const fetchSavedSchemes = async () => {
  const response = await api.get('/saved-schemes');
  return response.data;
};

export const deleteSavedSchemeApi = async (savedId) => {
  const response = await api.delete(`/saved-schemes/${savedId}`);
  return response.data;
};

export const fetchChecklistByScheme = async (schemeId) => {
  const response = await api.get(`/checklist/${schemeId}`);
  return response.data;
};

export const updateChecklistItemApi = async (itemId, status, notes = null) => {
  const response = await api.put(`/checklist/items/${itemId}`, {
    id: itemId,
    status,
    notes,
  });
  return response.data;
};

export const fetchDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const uploadDocumentApi = async (formData) => {
  const uploadUrl = API_BASE_URL.endsWith('/') ? `${API_BASE_URL}documents/upload` : `${API_BASE_URL}/documents/upload`;
  const response = await axios.post(uploadUrl, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteDocumentApi = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export default api;
