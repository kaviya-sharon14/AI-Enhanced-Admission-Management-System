/**
 * Centralized API Client & UI Toast Utility
 */

// Dynamic API base: automatically uses relative /api on localhost or custom BACKEND_API_URL on Netlify
const API_BASE = (window.BACKEND_API_URL && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
  ? `${window.BACKEND_API_URL}/api`
  : '/api';

const api = {
  getToken() {
    return localStorage.getItem('adm_token');
  },
  
  setToken(token) {
    localStorage.setItem('adm_token', token);
  },
  
  getUser() {
    try {
      const u = localStorage.getItem('adm_user');
      return u ? JSON.parse(u) : null;
    } catch (e) {
      return null;
    }
  },
  
  setUser(user) {
    localStorage.setItem('adm_user', JSON.stringify(user));
  },
  
  clearAuth() {
    localStorage.removeItem('adm_token');
    localStorage.removeItem('adm_user');
  },
  
  async request(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Auto JSON content type if body is object and not FormData
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(options.body);
    }
    
    options.headers = headers;
    
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 401 && !window.location.pathname.includes('login')) {
          this.clearAuth();
          window.location.href = '/login';
        }
        throw new Error(data.message || 'Request failed');
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },
  
  // Auth endpoints
  login(email, password) {
    return this.request('/auth/login', { method: 'POST', body: { email, password } });
  },
  
  register(userData) {
    return this.request('/auth/register', { method: 'POST', body: userData });
  },

  forgotPassword(email) {
    return this.request('/auth/forgot-password', { method: 'POST', body: { email } });
  },

  resetPassword(email, reset_code, new_password) {
    return this.request('/auth/reset-password', {
      method: 'POST',
      body: { email, reset_code, new_password }
    });
  },

  getDbStatus() {
    return this.request('/auth/db-status', { method: 'GET' });
  },

  syncMongo() {
    return this.request('/auth/sync-mongo', { method: 'POST' });
  },
  
  getCourses() {
    return this.request('/auth/courses', { method: 'GET' });
  },
  
  getCurrentUser() {
    return this.request('/auth/me', { method: 'GET' });
  },
  
  // Applications endpoints
  submitApplication(formData) {
    return this.request('/applications/apply', { method: 'POST', body: formData });
  },
  
  getMyApplications() {
    return this.request('/applications/my', { method: 'GET' });
  },
  
  getAllApplications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/applications${query ? '?' + query : ''}`, { method: 'GET' });
  },
  
  getApplicationDetail(id) {
    return this.request(`/applications/${id}`, { method: 'GET' });
  },
  
  updateApplicationStatus(id, status, remarks) {
    return this.request(`/applications/${id}/status`, {
      method: 'PUT',
      body: { status, remarks }
    });
  },
  
  // ML endpoints
  predictAdmission(payload) {
    return this.request('/ml/predict', { method: 'POST', body: payload });
  },
  
  getMLMetrics() {
    return this.request('/ml/metrics', { method: 'GET' });
  },
  
  // GenAI endpoints
  evaluateApplication(appId, instructions = '') {
    return this.request(`/genai/evaluate/${appId}`, {
      method: 'POST',
      body: { instructions }
    });
  },
  
  // Analytics
  getAnalyticsSummary() {
    return this.request('/analytics/summary', { method: 'GET' });
  }
};

/**
 * Toast Notification Dispatcher
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '⚠️';
  if (type === 'warning') icon = '🔔';
  
  toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
