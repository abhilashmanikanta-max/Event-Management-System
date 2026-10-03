/**
 * EVENT MANAGEMENT SYSTEM - REST API Client
 * Connects Frontend directly to Flask + SQL Backend
 */

const API = {
  // Toast Notification Helper
  showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(50px)';
      setTimeout(() => toast.remove(), 250);
    }, 4500);
  },

  async request(endpoint, options = {}) {
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(endpoint, config);
      const data = await response.json();

      if (!response.ok || data.status === 'error') {
        const errorMsg = data.message || `Request failed with status ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      API.showToast('Database / API Error', err.message, 'error');
      throw err;
    }
  },

  // Health & Database Status
  getHealth: () => API.request('/api/health'),
  getDbStatus: () => API.request('/api/database/status'),
  getDatabaseTables: () => API.request('/api/database/tables'),
  getTableDetails: (tableName, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/api/database/tables/${tableName}?${query}`);
  },
  resetDatabase: () => API.request('/api/database/reset', { method: 'POST' }),

  // Dashboard
  getDashboardStats: () => API.request('/api/dashboard/stats'),

  // Events
  getEvents: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/api/events?${query}`);
  },
  getEvent: (id) => API.request(`/api/events/${id}`),
  createEvent: (data) => API.request('/api/events', { method: 'POST', body: data }),
  updateEvent: (id, data) => API.request(`/api/events/${id}`, { method: 'PUT', body: data }),
  deleteEvent: (id) => API.request(`/api/events/${id}`, { method: 'DELETE' }),

  // Organizers
  getOrganizers: (search = '') => API.request(`/api/organizers?search=${encodeURIComponent(search)}`),
  getOrganizer: (id) => API.request(`/api/organizers/${id}`),
  createOrganizer: (data) => API.request('/api/organizers', { method: 'POST', body: data }),
  updateOrganizer: (id, data) => API.request(`/api/organizers/${id}`, { method: 'PUT', body: data }),
  deleteOrganizer: (id) => API.request(`/api/organizers/${id}`, { method: 'DELETE' }),

  // Venues
  getVenues: (search = '') => API.request(`/api/venues?search=${encodeURIComponent(search)}`),
  getVenue: (id) => API.request(`/api/venues/${id}`),
  createVenue: (data) => API.request('/api/venues', { method: 'POST', body: data }),
  updateVenue: (id, data) => API.request(`/api/venues/${id}`, { method: 'PUT', body: data }),
  deleteVenue: (id) => API.request(`/api/venues/${id}`, { method: 'DELETE' }),

  // Categories
  getCategories: (search = '') => API.request(`/api/categories?search=${encodeURIComponent(search)}`),
  getCategory: (id) => API.request(`/api/categories/${id}`),
  createCategory: (data) => API.request('/api/categories', { method: 'POST', body: data }),
  updateCategory: (id, data) => API.request(`/api/categories/${id}`, { method: 'PUT', body: data }),
  deleteCategory: (id) => API.request(`/api/categories/${id}`, { method: 'DELETE' }),

  // Participants
  getParticipants: (search = '') => API.request(`/api/participants?search=${encodeURIComponent(search)}`),
  getParticipant: (id) => API.request(`/api/participants/${id}`),
  createParticipant: (data) => API.request('/api/participants', { method: 'POST', body: data }),
  updateParticipant: (id, data) => API.request(`/api/participants/${id}`, { method: 'PUT', body: data }),
  deleteParticipant: (id) => API.request(`/api/participants/${id}`, { method: 'DELETE' }),

  // Registrations
  getRegistrations: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/api/registrations?${query}`);
  },
  getRegistration: (id) => API.request(`/api/registrations/${id}`),
  createRegistration: (data) => API.request('/api/registrations', { method: 'POST', body: data }),
  updateRegistration: (id, data) => API.request(`/api/registrations/${id}`, { method: 'PUT', body: data }),
  cancelRegistration: (id) => API.request(`/api/registrations/${id}/cancel`, { method: 'POST' }),
  deleteRegistration: (id) => API.request(`/api/registrations/${id}`, { method: 'DELETE' }),

  // Payments
  getPayments: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/api/payments?${query}`);
  },
  getPaymentSummary: () => API.request('/api/payments/summary'),
  getPayment: (id) => API.request(`/api/payments/${id}`),
  createPayment: (data) => API.request('/api/payments', { method: 'POST', body: data }),
  updatePayment: (id, data) => API.request(`/api/payments/${id}`, { method: 'PUT', body: data }),
  deletePayment: (id) => API.request(`/api/payments/${id}`, { method: 'DELETE' }),

  // Reports
  getReport: (type, format = 'json') => {
    if (format === 'csv') {
      window.location.href = `/api/reports/${type}?format=csv`;
      return;
    }
    return API.request(`/api/reports/${type}`);
  },

  // SQL Query Console
  getPresets: () => API.request('/api/admin/presets'),
  executeQuery: (sql) => API.request('/api/admin/execute', { method: 'POST', body: { query: sql } })
};
