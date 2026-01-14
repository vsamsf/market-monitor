import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Task API
export const taskAPI = {
  getAll: (includeCompleted = false) => 
    api.get(`/api/tasks?include_completed=${includeCompleted}`),
  getById: (id: number) => api.get(`/api/tasks/${id}`),
  create: (data: any) => api.post('/api/tasks', data),
  update: (id: number, data: any) => api.put(`/api/tasks/${id}`, data),
  complete: (id: number) => api.post(`/api/tasks/${id}/complete`),
  uncomplete: (id: number) => api.post(`/api/tasks/${id}/uncomplete`),
  delete: (id: number) => api.delete(`/api/tasks/${id}`),
  getToday: () => api.get('/api/tasks/filter/today'),
  getOverdue: () => api.get('/api/tasks/filter/overdue'),
};

// Reminder API
export const reminderAPI = {
  getAll: (activeOnly = true) => 
    api.get(`/api/reminders?active_only=${activeOnly}`),
  getById: (id: number) => api.get(`/api/reminders/${id}`),
  create: (data: any) => api.post('/api/reminders', data),
  update: (id: number, data: any) => api.put(`/api/reminders/${id}`, data),
  delete: (id: number) => api.delete(`/api/reminders/${id}`),
};

// Market API
export const marketAPI = {
  getSummary: () => api.get('/api/market/summary'),
  getIndices: () => api.get('/api/market/indices'),
  getSectors: () => api.get('/api/market/sectors'),
};

// System API
export const systemAPI = {
  getStatus: () => api.get('/api/system/status'),
  getDashboardStats: () => api.get('/api/dashboard/stats'),
};

export default api;
