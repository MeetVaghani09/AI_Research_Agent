import axios from 'axios';

// Backend URL
const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,

  headers: {
    'Content-Type': 'application/json',
  },

  timeout: 120000,
});

// Log all requests
api.interceptors.request.use(
  (config) => {
    console.log(
      '📤 API Request:',
      config.method.toUpperCase(),
      config.url
    );

    return config;
  },

  (error) => {
    console.error('❌ Request Error:', error);

    return Promise.reject(error);
  }
);

// Log all responses
api.interceptors.response.use(
  (response) => {
    console.log(
      '📥 API Response:',
      response.status,
      response.data
    );

    return response;
  },

  (error) => {
    console.error(
      '❌ Response Error:',
      error.response?.data || error.message
    );

    return Promise.reject(error);
  }
);

export const queryAPI = {

  // Send a research query
  sendQuery: async (
    question,
    sessionId = 'research-user'
  ) => {

    const formData = new FormData();

    formData.append('session_id', sessionId);
    formData.append('question', question);

    const response = await api.post(
      '/api/research',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  // Upload a PDF
  uploadPDF: async (
    file,
    sessionId = 'research-user'
  ) => {

    const formData = new FormData();

    formData.append('session_id', sessionId);
    formData.append('file', file);

    const response = await api.post(
      '/api/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  // Get uploaded documents
  getDocuments: async (
    sessionId = 'research-user'
  ) => {

    const response = await api.get(
      `/api/documents/${sessionId}`
    );

    return response.data;
  },

  // Get system status
  getStatus: async () => {

    const response = await api.get(
      '/api/status'
    );

    return response.data;
  },
  
  // Delete one uploaded PDF
  deleteDocument: async (
    filename,
    sessionId = 'research-user'
  ) => {

    const response = await api.delete(
      `/api/document/${encodeURIComponent(
        sessionId
      )}/${encodeURIComponent(filename)}`
    );

    return response.data;
  },



  // Clear session
  clearSession: async (
    sessionId = 'research-user'
  ) => {

    const response = await api.delete(
      `/api/clear/${sessionId}`
    );

    return response.data;
  },

};

export default api;