/**
 * Centralized API Client & Seamless Client-Side Fallback Engine
 * Works 100% online with Flask Backend AND offline/standalone on Netlify!
 */

const API_BASE = (window.BACKEND_API_URL && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
  ? `${window.BACKEND_API_URL}/api`
  : '/api';

// ==============================================================================
// Client-Side Demo Database Initialization (for Netlify / Standalone Demo)
// ==============================================================================
const DEFAULT_MOCK_USERS = [
  {
    id: 1,
    name: 'Dr. Ramesh Kumar',
    email: 'admin@institution.edu',
    password: 'Admin@123',
    role: 'admin',
    phone: '+91 94440 12345'
  },
  {
    id: 2,
    name: 'Ananya Iyer',
    email: 'student@institution.edu',
    password: 'Student@123',
    role: 'student',
    phone: '+91 98401 23456'
  }
];

const DEFAULT_COURSES = [
  { code: 'CSE-101', name: 'B.Tech Computer Science & Engineering', department: 'Computer Science', seats: 120, min_gpa: 75.0, min_entrance: 70.0 },
  { code: 'AIDS-102', name: 'B.Tech Artificial Intelligence & Data Science', department: 'Data Science', seats: 60, min_gpa: 78.0, min_entrance: 72.0 },
  { code: 'IT-103', name: 'B.Tech Information Technology', department: 'Information Technology', seats: 90, min_gpa: 70.0, min_entrance: 65.0 },
  { code: 'ECE-104', name: 'B.Tech Electronics & Communication Engineering', department: 'Electronics', seats: 120, min_gpa: 70.0, min_entrance: 65.0 },
  { code: 'MECH-105', name: 'B.Tech Mechanical Engineering', department: 'Mechanical', seats: 60, min_gpa: 60.0, min_entrance: 55.0 }
];

const DEFAULT_APPLICATIONS = [
  {
    id: 1,
    application_no: 'APP-2026-9481',
    user_id: 2,
    full_name: 'Ananya Iyer',
    email: 'ananya.iyer@example.com',
    phone: '+91 98401 23456',
    dob: '2005-08-14',
    gender: 'Female',
    address: 'Anna Nagar, Chennai, Tamil Nadu',
    course_code: 'CSE-101',
    course_name: 'B.Tech Computer Science & Engineering',
    academic_gpa: 92.4,
    entrance_score: 88.0,
    attendance_pct: 94.5,
    prev_academic_score: 91.0,
    category: 'General',
    extracurricular: 'State_Level',
    document_name: 'Ananya_Iyer_Dossier.pdf',
    status: 'Under Review',
    ml_prediction: 'Eligible',
    ml_probability: 94.8,
    ai_evaluation_summary: 'Applicant shows outstanding academic consistency, superior entrance score, and state-level sports achievements.',
    ai_recommendation: 'Strongly Recommend Admission',
    ai_profile_insights: 'Core strength in analytical problem solving; exceptional secondary score trajectory.',
    ai_explanation: 'Meets 100% of institutional cutoff guidelines and program prerequisites.',
    admin_remarks: 'Verified qualifying certificates; provisional seat allocated.',
    submitted_at: '2026-11-10 10:30:00'
  },
  {
    id: 2,
    application_no: 'APP-2026-9482',
    user_id: 102,
    full_name: 'Rahul Verma',
    email: 'rahul.verma@example.com',
    phone: '+91 98112 34567',
    dob: '2005-03-22',
    gender: 'Male',
    address: 'Indiranagar, Bengaluru, Karnataka',
    course_code: 'IT-103',
    course_name: 'B.Tech Information Technology',
    academic_gpa: 88.5,
    entrance_score: 82.0,
    attendance_pct: 91.0,
    prev_academic_score: 86.0,
    category: 'OBC',
    extracurricular: 'School_Level',
    document_name: 'Rahul_Verma_Documents.pdf',
    status: 'Approved',
    ml_prediction: 'Eligible',
    ml_probability: 89.2,
    ai_evaluation_summary: 'Well-rounded academic profile with consistent grades exceeding threshold criteria.',
    ai_recommendation: 'Recommend Admission',
    ai_profile_insights: 'Strong technical aptitude; qualified under OBC quota norms.',
    ai_explanation: 'Approved under institutional merit list.',
    admin_remarks: 'Admission confirmed. Welcome to Apex Institute!',
    submitted_at: '2026-11-09 14:15:00'
  },
  {
    id: 3,
    application_no: 'APP-2026-9483',
    user_id: 103,
    full_name: 'Priya Sharma',
    email: 'priya.sharma@example.com',
    phone: '+91 97234 56789',
    dob: '2005-11-05',
    gender: 'Female',
    address: 'Banjara Hills, Hyderabad, Telangana',
    course_code: 'ECE-104',
    course_name: 'B.Tech Electronics & Communication Engineering',
    academic_gpa: 79.0,
    entrance_score: 74.0,
    attendance_pct: 88.0,
    prev_academic_score: 81.0,
    category: 'General',
    extracurricular: 'National_Level',
    document_name: 'Priya_Sharma_Marksheet.pdf',
    status: 'Approved',
    ml_prediction: 'Eligible',
    ml_probability: 76.5,
    ai_evaluation_summary: 'Strong national sports achievements elevate overall composite score.',
    ai_recommendation: 'Recommend Admission (Sports Quota)',
    ai_profile_insights: 'Demonstrated exceptional extracurricular leadership.',
    ai_explanation: 'Approved under sports quota concession rules.',
    admin_remarks: 'Sports quota concession applied; approved by Dean.',
    submitted_at: '2026-11-08 11:20:00'
  }
];

function getStoredUsers() {
  try {
    const raw = localStorage.getItem('adm_mock_users');
    if (!raw) {
      localStorage.setItem('adm_mock_users', JSON.stringify(DEFAULT_MOCK_USERS));
      return [...DEFAULT_MOCK_USERS];
    }
    return JSON.parse(raw);
  } catch (e) {
    return [...DEFAULT_MOCK_USERS];
  }
}

function saveStoredUsers(users) {
  localStorage.setItem('adm_mock_users', JSON.stringify(users));
}

function getStoredApplications() {
  try {
    const raw = localStorage.getItem('adm_mock_applications');
    if (!raw) {
      localStorage.setItem('adm_mock_applications', JSON.stringify(DEFAULT_APPLICATIONS));
      return [...DEFAULT_APPLICATIONS];
    }
    return JSON.parse(raw);
  } catch (e) {
    return [...DEFAULT_APPLICATIONS];
  }
}

function saveStoredApplications(apps) {
  localStorage.setItem('adm_mock_applications', JSON.stringify(apps));
}

// ==============================================================================
// Main API Client Object
// ==============================================================================
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
    
    let isJsonBody = false;
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(options.body);
      isJsonBody = true;
    }
    
    options.headers = headers;
    
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      
      // Check content-type to guard against HTML fallback pages (Netlify index.html)
      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        // Non-JSON response returned (e.g. Netlify 404 / SPA redirect to index.html)
        console.warn(`[API Client] Non-JSON response from server for ${endpoint}. Activating client-side demo fallback.`);
        return this.handleFallback(endpoint, options);
      }
      
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
      // If network failed (e.g. static host without running backend), use client-side demo fallback
      if (err.message && !err.message.includes('Request failed') && !err.message.includes('Invalid') && !err.message.includes('exists') && !err.message.includes('required')) {
        console.info(`[API Client] Live backend unreachable for ${endpoint}. Using browser local storage.`);
        return this.handleFallback(endpoint, options);
      }
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },
  
  // ============================================================================
  // Client-Side Fallback Handler (Executes when live Flask backend is not hosted)
  // ============================================================================
  handleFallback(endpoint, options = {}) {
    let body = {};
    if (options.body) {
      if (typeof options.body === 'string') {
        try { body = JSON.parse(options.body); } catch(e) {}
      } else if (options.body instanceof FormData) {
        body = Object.fromEntries(options.body.entries());
      } else {
        body = options.body;
      }
    }

    // 1. REGISTER
    if (endpoint === '/auth/register') {
      const { name, email, password, phone, role } = body;
      if (!name || !email || !password) {
        throw new Error('Name, email, and password are required.');
      }
      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters long.');
      }
      
      const users = getStoredUsers();
      const existing = users.find(u => u.email.toLowerCase() === email.toLowerCase());
      if (existing) {
        throw new Error('An account with this email address already exists.');
      }
      
      const newUser = {
        id: Date.now(),
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password: password,
        phone: phone ? phone.trim() : '',
        role: role || 'student'
      };
      users.push(newUser);
      saveStoredUsers(users);
      
      const token = `demo-token-${newUser.id}-${Date.now()}`;
      return {
        success: true,
        message: 'Account registered successfully.',
        token: token,
        user: {
          id: newUser.id,
          name: newUser.name,
          email: newUser.email,
          role: newUser.role,
          phone: newUser.phone
        }
      };
    }

    // 2. LOGIN
    if (endpoint === '/auth/login') {
      const email = (body.email || '').trim().toLowerCase();
      const password = body.password || '';
      
      if (!email || !password) {
        throw new Error('Email and password are required.');
      }
      
      const users = getStoredUsers();
      const user = users.find(u => u.email.toLowerCase() === email && u.password === password);
      
      if (!user) {
        throw new Error('Invalid credentials. Incorrect email or password.');
      }
      
      const token = `demo-token-${user.id}-${Date.now()}`;
      return {
        success: true,
        message: 'Logged in successfully.',
        token: token,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          phone: user.phone || ''
        }
      };
    }

    // 3. FORGOT PASSWORD
    if (endpoint === '/auth/forgot-password') {
      const email = (body.email || '').trim().toLowerCase();
      if (!email) throw new Error('Email address is required.');
      
      const users = getStoredUsers();
      const user = users.find(u => u.email.toLowerCase() === email);
      if (!user) {
        throw new Error('No registered account found with this email address.');
      }
      
      const code = String(Math.floor(100000 + Math.random() * 900000));
      localStorage.setItem('adm_demo_reset_code', code);
      localStorage.setItem('adm_demo_reset_email', email);
      
      return {
        success: true,
        message: `Verification code generated successfully for ${email}.`,
        email: email,
        reset_code: code,
        expires_in_minutes: 15
      };
    }

    // 4. RESET PASSWORD
    if (endpoint === '/auth/reset-password') {
      const email = (body.email || '').trim().toLowerCase();
      const code = String(body.reset_code || '').trim();
      const newPassword = body.new_password || '';
      
      if (!email || !code || !newPassword) {
        throw new Error('Email, reset code, and new password are required.');
      }
      if (newPassword.length < 6) {
        throw new Error('New password must be at least 6 characters.');
      }
      
      const savedCode = localStorage.getItem('adm_demo_reset_code');
      const savedEmail = localStorage.getItem('adm_demo_reset_email');
      
      if (!savedCode || savedCode !== code || (savedEmail && savedEmail !== email)) {
        throw new Error('Invalid or expired verification code. Please request a new code.');
      }
      
      const users = getStoredUsers();
      const userIdx = users.findIndex(u => u.email.toLowerCase() === email);
      if (userIdx !== -1) {
        users[userIdx].password = newPassword;
        saveStoredUsers(users);
      }
      
      localStorage.removeItem('adm_demo_reset_code');
      localStorage.removeItem('adm_demo_reset_email');
      
      return {
        success: true,
        message: 'Password has been reset successfully! You can now log in.'
      };
    }

    // 5. COURSES
    if (endpoint === '/auth/courses') {
      return { success: true, courses: DEFAULT_COURSES };
    }

    // 6. DB STATUS
    if (endpoint === '/auth/db-status') {
      const users = getStoredUsers();
      const apps = getStoredApplications();
      return {
        success: true,
        mongodb: { connected: false, database: 'admissions_db', uri: 'mongodb://localhost:27017/' },
        sqlite: { connected: true, file: 'admissions.db', counts: { users: users.length, applications: apps.length } }
      };
    }

    // 7. CURRENT USER
    if (endpoint === '/auth/me') {
      const u = this.getUser();
      return { success: true, user: u || DEFAULT_MOCK_USERS[1] };
    }

    // 8. ML PREDICT
    if (endpoint === '/ml/predict') {
      const gpa = parseFloat(body.academic_gpa || 80);
      const entrance = parseFloat(body.entrance_score || 75);
      const attendance = parseFloat(body.attendance_pct || 90);
      const isEligible = (gpa >= 70 && entrance >= 65);
      const prob = Math.min(99.4, Math.max(25.0, (gpa * 0.5 + entrance * 0.4 + attendance * 0.1) * 1.02)).toFixed(1);
      
      return {
        success: true,
        prediction: isEligible ? 'Eligible' : 'Not Eligible',
        probability: parseFloat(prob),
        key_factors: `Academic GPA: ${gpa}%, Entrance Score: ${entrance}/100, Attendance: ${attendance}%`
      };
    }

    // 9. SUBMIT APPLICATION
    if (endpoint === '/applications/apply') {
      const apps = getStoredApplications();
      const currentUser = this.getUser() || DEFAULT_MOCK_USERS[1];
      const gpa = parseFloat(body.academic_gpa || 85);
      const entrance = parseFloat(body.entrance_score || 80);
      const isEligible = (gpa >= 70 && entrance >= 65);
      const prob = Math.min(99.4, Math.max(25.0, (gpa * 0.5 + entrance * 0.4 + 9.0) * 1.02)).toFixed(1);

      const newApp = {
        id: Date.now(),
        application_no: `APP-2026-${Math.floor(1000 + Math.random() * 9000)}`,
        user_id: currentUser.id,
        full_name: body.full_name || currentUser.name,
        email: body.email || currentUser.email,
        phone: body.phone || currentUser.phone || '',
        dob: body.dob || '2005-06-15',
        gender: body.gender || 'Not Specified',
        address: body.address || 'Chennai, Tamil Nadu',
        course_code: body.course_code || 'CSE-101',
        course_name: (DEFAULT_COURSES.find(c => c.code === body.course_code) || DEFAULT_COURSES[0]).name,
        academic_gpa: gpa,
        entrance_score: entrance,
        attendance_pct: parseFloat(body.attendance_pct || 90),
        prev_academic_score: parseFloat(body.prev_academic_score || 85),
        category: body.category || 'General',
        extracurricular: body.extracurricular || 'None',
        document_name: 'Marksheet_Certificate.pdf',
        status: 'Submitted',
        ml_prediction: isEligible ? 'Eligible' : 'Not Eligible',
        ml_probability: parseFloat(prob),
        ai_evaluation_summary: `Candidate demonstrated solid academic records with ${gpa}% GPA and ${entrance} entrance score.`,
        ai_recommendation: isEligible ? 'Recommend Admission' : 'Conditional Review',
        ai_profile_insights: 'Consistent marks profile meeting prerequisite criteria.',
        ai_explanation: 'Standard admissions protocol criteria satisfied.',
        admin_remarks: 'Application under verification.',
        submitted_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
      };

      apps.unshift(newApp);
      saveStoredApplications(apps);
      
      return {
        success: true,
        message: 'Admission application submitted successfully!',
        application_no: newApp.application_no,
        ml_prediction: newApp.ml_prediction,
        ml_probability: newApp.ml_probability
      };
    }

    // 10. GET MY APPLICATIONS
    if (endpoint === '/applications/my') {
      const apps = getStoredApplications();
      const currentUser = this.getUser();
      const myApp = (currentUser && apps.find(a => a.email.toLowerCase() === currentUser.email.toLowerCase())) || apps[0];
      return { success: true, application: myApp };
    }

    // 11. GET ALL APPLICATIONS
    if (endpoint.startsWith('/applications')) {
      const apps = getStoredApplications();
      return {
        success: true,
        applications: apps,
        pagination: { total: apps.length, page: 1, limit: 10, pages: 1 }
      };
    }

    // 12. ANALYTICS
    if (endpoint === '/analytics/summary') {
      const apps = getStoredApplications();
      return {
        success: true,
        summary: {
          total_applications: apps.length,
          approved_count: apps.filter(a => a.status === 'Approved').length,
          under_review_count: apps.filter(a => a.status === 'Under Review' || a.status === 'Submitted').length,
          rejected_count: apps.filter(a => a.status === 'Rejected').length,
          average_gpa: 84.5,
          average_entrance: 79.2
        }
      };
    }

    // Default fallback
    return { success: true, message: 'Action completed.' };
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
