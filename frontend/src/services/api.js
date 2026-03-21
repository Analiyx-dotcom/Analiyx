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
  
  // User Management
  getAllUsersDetails: async () => {
    const response = await api.get('/admin/manage/users/details');
    return response.data;
  },
  
  updateUserStatus: async (userId, status) => {
    const response = await api.put(`/admin/manage/users/${userId}/status`, { status });
    return response.data;
  },
  
  extendTrial: async (userId, days = 7) => {
    const response = await api.post(`/admin/manage/users/${userId}/extend-trial`, { days });
    return response.data;
  },
  
  updateSubscription: async (userId, durationMonths) => {
    const response = await api.put(`/admin/manage/users/${userId}/subscription`, { duration_months: durationMonths });
    return response.data;
  },
  
  manageCredits: async (userId, credits, action) => {
    const response = await api.put(`/admin/manage/users/${userId}/credits`, { credits, action });
    return response.data;
  },
  
  getUserActivity: async (userId) => {
    const response = await api.get(`/admin/manage/users/${userId}/activity`);
    return response.data;
  },

  // Tickets
  getAllTickets: async () => {
    const response = await api.get('/admin/manage/tickets');
    return response.data;
  },

  replyToTicket: async (ticketId, reply) => {
    const response = await api.post(`/admin/manage/tickets/${ticketId}/reply`, { reply });
    return response.data;
  },

  closeTicket: async (ticketId) => {
    const response = await api.put(`/admin/manage/tickets/${ticketId}/status`);
    return response.data;
  },

  // Export
  exportUsersExcel: () => `${API}/admin/manage/users/export/excel`,
  exportUsersPDF: () => `${API}/admin/manage/users/export/pdf`,
};

// Data Source API
export const dataSourceAPI = {
  uploadFile: async (file, workspaceId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    const url = workspaceId ? `/data-sources/upload-file?workspace_id=${workspaceId}` : '/data-sources/upload-file';
    const response = await api.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  getUploadedFiles: async (workspaceId = null) => {
    const url = workspaceId ? `/data-sources/uploaded-files?workspace_id=${workspaceId}` : '/data-sources/uploaded-files';
    const response = await api.get(url);
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

// Workspace API
export const workspaceAPI = {
  create: async (name, dataSources) => {
    const response = await api.post('/workspaces/create', { name, data_sources: dataSources });
    return response.data;
  },
  list: async () => {
    const response = await api.get('/workspaces/list');
    return response.data;
  },
  delete: async (workspaceId) => {
    const response = await api.delete(`/workspaces/${workspaceId}`);
    return response.data;
  },
};

// Support API
export const supportAPI = {
  createTicket: async (subject, message, priority) => {
    const response = await api.post('/support/tickets', { subject, message, priority });
    return response.data;
  },
  getTickets: async () => {
    const response = await api.get('/support/tickets');
    return response.data;
  },
};

export default api;
