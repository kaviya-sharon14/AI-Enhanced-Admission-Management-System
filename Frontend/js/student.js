/**
 * Student Dashboard & Application Workflow Logic
 */

let myApplication = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  
  const user = api.getUser();
  if (user) {
    document.getElementById('welcome-title').innerText = `Welcome, ${user.name}`;
    document.getElementById('current-user-tag').innerText = `Role: ${user.role.toUpperCase()}`;
    
    // Auto fill form defaults
    const nameField = document.getElementById('form-fullname');
    const emailField = document.getElementById('form-email');
    const phoneField = document.getElementById('form-phone');
    if (nameField) nameField.value = user.name || '';
    if (emailField) emailField.value = user.email || '';
    if (phoneField) phoneField.value = user.phone || '';
  }

  await loadCoursesDropdown();
  await loadMyApplication();
});

function switchStudentTab(tab) {
  const statusSec = document.getElementById('section-status');
  const applySec = document.getElementById('section-apply');
  const statusBtn = document.getElementById('tab-status-btn');
  const applyBtn = document.getElementById('tab-apply-btn');

  if (tab === 'status') {
    statusSec.style.display = 'block';
    applySec.style.display = 'none';
    statusBtn.classList.add('active');
    applyBtn.classList.remove('active');
    loadMyApplication();
  } else {
    statusSec.style.display = 'none';
    applySec.style.display = 'block';
    statusBtn.classList.remove('active');
    applyBtn.classList.add('active');
  }
}

async function loadCoursesDropdown() {
  try {
    const res = await api.getCourses();
    const select = document.getElementById('form-course');
    if (!select) return;
    
    select.innerHTML = '<option value="">-- Choose Degree Program --</option>';
    res.courses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.code;
      opt.textContent = `${c.name} (${c.code}) - ${c.department}`;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error('Failed to load courses:', e);
  }
}

function handleFileSelected(input) {
  const label = document.getElementById('file-selected-name');
  if (input.files && input.files[0]) {
    label.innerHTML = `Selected Document: <strong>${input.files[0].name}</strong> (${(input.files[0].size / 1024).toFixed(1)} KB)`;
  } else {
    label.innerText = '';
  }
}

async function runLivePrecheck() {
  const gpa = parseFloat(document.getElementById('form-gpa').value);
  const entrance = parseFloat(document.getElementById('form-entrance').value);
  const attendance = parseFloat(document.getElementById('form-attendance').value);
  const prevScore = parseFloat(document.getElementById('form-prevscore').value);
  const category = document.getElementById('form-category').value;
  const extracurricular = document.getElementById('form-extracurricular').value;
  
  if (isNaN(gpa) || isNaN(entrance)) {
    showToast('Please enter at least Academic GPA and Entrance Score first.', 'warning');
    return;
  }
  
  const payload = {
    academic_gpa: gpa || 75,
    entrance_score: entrance || 70,
    attendance_pct: attendance || 80,
    prev_academic_score: prevScore || 75,
    category: category,
    extracurricular: extracurricular
  };
  
  const outBox = document.getElementById('precheck-result');
  outBox.style.display = 'block';
  outBox.innerHTML = '<em>Running Scikit-Learn Logistic Regression model inference...</em>';
  
  try {
    const res = await api.predictAdmission(payload);
    if (res.success) {
      const isEligible = res.is_eligible;
      outBox.style.background = isEligible ? '#ecfdf5' : '#fff1f2';
      outBox.style.border = `1px solid ${isEligible ? '#6ee7b7' : '#fda4af'}`;
      outBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <strong style="color: ${isEligible ? '#065f46' : '#991b1b'}; font-size: 1rem;">
            ${isEligible ? '✅ ' : '⚠️ '}${res.prediction}
          </strong>
          <span style="font-size: 0.95rem; font-weight: 800; color: ${isEligible ? '#059669' : '#e11d48'};">
            Probability: ${res.probability_percentage}%
          </span>
        </div>
        <p style="font-size: 0.85rem; color: #475569; margin: 0;">
          Algorithm: ${res.algorithm} • Decision Threshold: ${res.threshold * 100}%
        </p>
      `;
      showToast(`Pre-check completed: ${res.prediction} (${res.probability_percentage}%)`, isEligible ? 'success' : 'warning');
    }
  } catch (err) {
    outBox.innerHTML = `<span style="color: red;">Pre-check error: ${err.message}</span>`;
  }
}

async function handleApplicationSubmit(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('submit-app-btn');
  submitBtn.disabled = true;
  submitBtn.innerText = 'Submitting & Evaluating AI Models...';

  const formData = new FormData();
  formData.append('full_name', document.getElementById('form-fullname').value);
  formData.append('email', document.getElementById('form-email').value);
  formData.append('phone', document.getElementById('form-phone').value);
  formData.append('dob', document.getElementById('form-dob').value);
  formData.append('gender', document.getElementById('form-gender').value);
  formData.append('address', document.getElementById('form-address').value);
  formData.append('course_code', document.getElementById('form-course').value);
  formData.append('academic_gpa', document.getElementById('form-gpa').value);
  formData.append('entrance_score', document.getElementById('form-entrance').value);
  formData.append('attendance_pct', document.getElementById('form-attendance').value);
  formData.append('prev_academic_score', document.getElementById('form-prevscore').value);
  formData.append('category', document.getElementById('form-category').value);
  formData.append('extracurricular', document.getElementById('form-extracurricular').value);

  const fileInput = document.getElementById('form-document');
  if (fileInput.files[0]) {
    formData.append('document', fileInput.files[0]);
  }

  try {
    const res = await api.submitApplication(formData);
    if (res.success) {
      showToast(`Application ${res.application_no} submitted successfully!`, 'success');
      switchStudentTab('status');
      await loadMyApplication();
    }
  } catch (err) {
    showToast(err.message || 'Submission failed.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Submit Final Application 🚀';
  }
}

async function loadMyApplication() {
  const noAppBanner = document.getElementById('no-application-banner');
  const detailsContainer = document.getElementById('application-details-container');

  try {
    const res = await api.getMyApplications();
    const appList = (res && res.applications && res.applications.length > 0)
      ? res.applications
      : (res && res.application ? [res.application] : []);

    if (!res || !res.success || appList.length === 0 || !appList[0]) {
      if (noAppBanner) noAppBanner.style.display = 'block';
      if (detailsContainer) detailsContainer.style.display = 'none';
      return;
    }

    if (noAppBanner) noAppBanner.style.display = 'none';
    if (detailsContainer) detailsContainer.style.display = 'block';

    const app = appList[0]; // Most recent application
    myApplication = app;

    // Header info
    document.getElementById('app-number').innerText = app.application_no || 'APP-2026';
    document.getElementById('app-course-name').innerText = `${app.course_name || app.course_code || 'Degree Course'} (${app.course_code || ''})`;
    document.getElementById('app-submission-date').innerText = app.submitted_at 
      ? new Date(app.submitted_at).toLocaleDateString('en-US', {
          year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        })
      : 'Recently Submitted';

    // Status Badge
    const currentStatus = app.status || 'Submitted';
    const statusBadge = document.getElementById('app-status-badge');
    statusBadge.innerText = currentStatus;
    statusBadge.className = 'badge ' + getBadgeClass(currentStatus);

    // Stepper updates
    updateStepper(currentStatus);

    // ML Module Info
    const prob = app.ml_probability;
    const probPct = (prob !== undefined && prob !== null) 
      ? (prob > 1 ? Number(prob).toFixed(1) : (Number(prob) * 100).toFixed(1)) + '%' 
      : '0.0%';
    document.getElementById('ml-prob-val').innerText = probPct;
    document.getElementById('ml-meter-bar').style.width = probPct;
    
    const isEligible = app.ml_prediction && (app.ml_prediction.toLowerCase().includes('eligible') && !app.ml_prediction.toLowerCase().includes('not'));
    const mlBadge = document.getElementById('ml-status-badge');
    mlBadge.innerText = app.ml_prediction || (isEligible ? 'Eligible' : 'Not Eligible');
    mlBadge.className = 'badge ' + (isEligible ? 'badge-eligible' : 'badge-not-eligible');

    document.getElementById('val-gpa').innerText = `${app.academic_gpa || 0}%`;
    document.getElementById('val-entrance').innerText = `${app.entrance_score || 0} / 100`;
    document.getElementById('val-attendance').innerText = `${app.attendance_pct || 0}%`;
    document.getElementById('val-category').innerText = `${app.category || 'General'} (${(app.extracurricular || 'None').toString().replace('_', ' ')})`;

    // Decision info
    document.getElementById('decision-status-text').innerText = currentStatus;
    document.getElementById('decision-remarks-text').innerText = app.admin_remarks || 'Your application is currently being processed by the admissions committee.';

    // Document preview link
    const docPreview = document.getElementById('uploaded-doc-preview');
    if (app.document_name) {
      docPreview.innerHTML = `
        <a href="/uploads/${app.document_path ? app.document_path.split('\\').pop().split('/').pop() : ''}" target="_blank" class="btn btn-secondary btn-sm" style="margin-top: 0.35rem;">
          📄 View ${escapeHtml(app.document_name)}
        </a>
      `;
    } else {
      docPreview.innerHTML = '<span style="color: var(--text-muted);">No document uploaded</span>';
    }

    // AI Evaluation details
    document.getElementById('ai-summary-text').innerText = app.ai_evaluation_summary || 'AI evaluation report being synthesized...';
    document.getElementById('ai-recommendation-text').innerText = app.ai_recommendation || 'Recommendation pending final committee review.';
    document.getElementById('ai-insights-text').innerText = app.ai_profile_insights || 'Insights pending.';

  } catch (err) {
    console.error('Error fetching applications:', err);
    if (noAppBanner) noAppBanner.style.display = 'block';
    if (detailsContainer) detailsContainer.style.display = 'none';
  }
}

function getBadgeClass(status) {
  switch (status) {
    case 'Approved': return 'badge-approved';
    case 'Rejected': return 'badge-rejected';
    case 'Under Review': return 'badge-review';
    case 'Waitlisted': return 'badge-waitlist';
    default: return 'badge-submitted';
  }
}

function updateStepper(status) {
  const s1 = document.getElementById('step-1');
  const s2 = document.getElementById('step-2');
  const s3 = document.getElementById('step-3');
  const s4 = document.getElementById('step-4');

  if (!s1 || !s2 || !s3 || !s4) return;

  [s1, s2, s3, s4].forEach(s => {
    s.className = 'step-item';
  });

  const normStatus = (status || '').toLowerCase();

  if (normStatus === 'submitted') {
    s1.classList.add('active');
  } else if (normStatus === 'under review') {
    s1.classList.add('completed');
    s2.classList.add('active');
  } else if (normStatus === 'approved') {
    s1.classList.add('completed');
    s2.classList.add('completed');
    s3.classList.add('completed');
    s4.classList.add('completed');
    s4.classList.add('active');
  } else if (normStatus === 'rejected') {
    s1.classList.add('completed');
    s2.classList.add('completed');
    s3.classList.add('completed');
    s4.classList.add('completed');
  } else if (normStatus === 'waitlisted') {
    s1.classList.add('completed');
    s2.classList.add('completed');
    s3.classList.add('active');
  } else {
    s1.classList.add('active');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.toString().replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}
