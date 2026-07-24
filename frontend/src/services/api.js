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

// Handle 403 (disabled/spam account) - force logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (detail.includes('disabled') || detail.includes('spam') || detail.includes('blocked')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login?reason=disabled';
      }
    }
    return Promise.reject(error);
  }
);

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

// Enterprise Data Engine API
export const datasourceAPI = {
  connect: async (data) => {
    const response = await api.post('/datasources/connect', data);
    return response.data;
  },
  list: async () => {
    const response = await api.get('/datasources/');
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/datasources/${id}`);
    return response.data;
  },
  test: async (id) => {
    const response = await api.post(`/datasources/${id}/test`);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/datasources/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/datasources/${id}`);
    return response.data;
  },
};

export const metadataAPI = {
  scan: async (datasourceId, background = false) => {
    const response = await api.post(`/metadata/scan/${datasourceId}?background=${background}`);
    return response.data;
  },
  get: async (datasourceId) => {
    const response = await api.get(`/metadata/${datasourceId}`);
    return response.data;
  },
  getTables: async (datasourceId) => {
    const response = await api.get(`/metadata/${datasourceId}/tables`);
    return response.data;
  },
  profile: async (datasourceId, background = false) => {
    const response = await api.post(`/metadata/profile/${datasourceId}?background=${background}`);
    return response.data;
  },
  getProfiles: async (datasourceId) => {
    const response = await api.get(`/metadata/profile/${datasourceId}`);
    return response.data;
  },
  getTableProfile: async (datasourceId, schema, table) => {
    const response = await api.get(`/metadata/profile/${datasourceId}/${schema}/${table}`);
    return response.data;
  },
  enrich: async (datasourceId, background = true) => {
    const response = await api.post(`/metadata/enrich/${datasourceId}?background=${background}`);
    return response.data;
  },
  getJobStatus: async (jobId) => {
    const response = await api.get(`/metadata/jobs/${jobId}`);
    return response.data;
  },
  listJobs: async () => {
    const response = await api.get('/metadata/jobs');
    return response.data;
  },
  search: async (datasourceId, query, limit = 10) => {
    const response = await api.post('/metadata/search', { datasource_id: datasourceId, query, limit });
    return response.data;
  },
  refresh: async (datasourceId) => {
    const response = await api.post(`/metadata/refresh/${datasourceId}`);
    return response.data;
  },
  detectRelationships: async (datasourceId) => {
    const response = await api.post(`/metadata/relationships/${datasourceId}`);
    return response.data;
  },
  getRelationships: async (datasourceId) => {
    const response = await api.get(`/metadata/relationships/${datasourceId}`);
    return response.data;
  },
  inferMetrics: async (datasourceId) => {
    const response = await api.post(`/metadata/metrics/${datasourceId}`);
    return response.data;
  },
  getMetrics: async (datasourceId) => {
    const response = await api.get(`/metadata/metrics/${datasourceId}`);
    return response.data;
  },
};

export const semanticAPI = {
  search: async (datasourceId, query, limit = 10) => {
    const response = await api.post('/semantic/search', { datasource_id: datasourceId, query, limit });
    return response.data;
  },
  createGlossaryTerm: async (data) => {
    const response = await api.post('/semantic/glossary', data);
    return response.data;
  },
  listGlossary: async (search = '') => {
    const response = await api.get(`/semantic/glossary?search=${search}`);
    return response.data;
  },
  updateGlossaryTerm: async (id, data) => {
    const response = await api.put(`/semantic/glossary/${id}`, data);
    return response.data;
  },
  deleteGlossaryTerm: async (id) => {
    const response = await api.delete(`/semantic/glossary/${id}`);
    return response.data;
  },
};

export const queryAPI = {
  plan: async (datasourceId, question) => {
    const response = await api.post('/query/plan', { datasource_id: datasourceId, question });
    return response.data;
  },
  validate: async (sql, dbType = 'postgresql') => {
    const response = await api.post('/query/validate', { sql, db_type: dbType });
    return response.data;
  },
  execute: async (datasourceId, sql, mode = 'hybrid', cacheTtl = 300) => {
    const response = await api.post('/query/execute', {
      datasource_id: datasourceId, sql, mode, cache_ttl: cacheTtl,
    });
    return response.data;
  },
  history: async (datasourceId = null, limit = 50) => {
    const params = new URLSearchParams({ limit });
    if (datasourceId) params.set('datasource_id', datasourceId);
    const response = await api.get(`/query/history?${params}`);
    return response.data;
  },
  clearCache: async (datasourceId) => {
    const response = await api.post(`/query/cache/clear/${datasourceId}`);
    return response.data;
  },
  cacheStats: async () => {
    const response = await api.get('/query/cache/stats');
    return response.data;
  },
};

export default api;
