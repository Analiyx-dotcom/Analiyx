import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${API_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },
  
  getUsers: async (page = 1, limit = 10) => {
    const response = await api.get(`/admin/users?page=${page}&limit=${limit}`);
    return response.data;
  },
  
  getUserGrowth: async () => {
    const response = await api.get('/admin/charts/user-growth');
    return response.data;
  },
  
  getRevenue: async () => {
    const response = await api.get('/admin/charts/revenue');
    return response.data;
  },
};

// Data Source API
export const dataSourceAPI = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/data-sources/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getUploadedFiles: async () => {
    const response = await api.get('/data-sources/uploaded-files');
    return response.data;
  },
  
  getFileDetails: async (fileId) => {
    const response = await api.get(`/data-sources/file-details/${fileId}`);
    return response.data;
  },
  
  deleteFile: async (fileId) => {
    const response = await api.delete(`/data-sources/file/${fileId}`);
    return response.data;
  },
};

export default api;
