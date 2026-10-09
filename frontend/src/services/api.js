import axios from 'axios';

// Base API URL configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const api = {
  // Health
  checkHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  // Files
  uploadFile: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post('/api/v1/files/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return res.data;
  },

  listFiles: async (limit = 50, offset = 0) => {
    const res = await client.get('/api/v1/files/', {
      params: { limit, offset },
    });
    return res.data;
  },

  getFile: async (fileId) => {
    const res = await client.get(`/api/v1/files/${fileId}`);
    return res.data;
  },

  deleteFile: async (fileId) => {
    const res = await client.delete(`/api/v1/files/${fileId}`);
    return res.data;
  },

  // Measurements & Analytics
  getMeasurements: async (fileId, params = {}) => {
    const res = await client.get(`/api/v1/files/${fileId}/measurements`, {
      params,
    });
    return res.data;
  },

  getSummary: async (fileId) => {
    const res = await client.get(`/api/v1/files/${fileId}/summary`);
    return res.data;
  },

  getGeoJSON: async (fileId) => {
    const res = await client.get(`/api/v1/files/${fileId}/geojson`);
    return res.data;
  },

  // Export URLs
  getExportUrl: (fileId, format) => {
    return `${API_BASE}/api/v1/files/${fileId}/export/${format}`;
  },
};

export default api;
