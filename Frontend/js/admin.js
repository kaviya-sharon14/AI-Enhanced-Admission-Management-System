/**
 * Admin & Admission Officer Dashboard Logic
 */

let applicationsList = [];
let activeAppId = null;
let searchDebounceTimer = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth('admin')) return;

  await loadCourseFilters();
  await loadApplications();
});

function debounceLoad() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(loadApplications, 300);
}

async function loadCourseFilters() {
  try {
    const res = await api.getCourses();
    const select = document.getElementById('filter-course');
    if (!select) return;

    res.courses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.code;
      opt.textContent = `${c.name} (${c.code})`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Error fetching courses:', err);
  }
}

async function loadApplications() {
  const statusFilter = document.getElementById('filter-status').value;
  const courseFilter = document.getElementById('filter-course').value;
  const search = document.getElementById('filter-search').value.trim();

  const tbody = document.getElementById('applications-tbody');
  tbody.innerHTML = `
    <tr>
      <td colspan="9" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
        Refreshing student records...
      </td>
    </tr>
  `;

  try {
    const res = await api.getAllApplications({
      status: statusFilter,
      course: courseFilter,
      search: search
    });

    applicationsList = res.applications || [];
    renderApplicationsTable(applicationsList);
    updateKPICards(applicationsList);

  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 2rem; color: #ef4444;">
          Failed to load applications: ${err.message}
        </td>
      </tr>
    `;
    showToast('Failed to load applications', 'error');
  }
}

function updateKPICards(list) {
  const total = list.length;
  const approved = list.filter(a => a.status === 'Approved').length;
  const rejected = list.filter(a => a.status === 'Rejected').length;
  const pending = list.filter(a => a.status === 'Submitted' || a.status === 'Under Review').length;
  const mlEligible = list.filter(a => a.ml_prediction === 'Eligible for Admission').length;
  const mlRate = total > 0 ? ((mlEligible / total) * 100).toFixed(1) : '0.0';

  document.getElementById('adm-stat-total').innerText = total;
  document.getElementById('adm-stat-approved').innerText = approved;
  document.getElementById('adm-stat-rejected').innerText = rejected;
  document.getElementById('adm-stat-pending').innerText = pending;
  document.getElementById('adm-stat-ml-rate').innerText = `${mlRate}%`;
}

function renderApplicationsTable(list) {
  const tbody = document.getElementById('applications-tbody');
  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
          No admission applications match current criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(app => {
    const probPct = app.ml_probability ? (app.ml_probability * 100).toFixed(1) + '%' : 'N/A';
    const isEligible = app.ml_prediction === 'Eligible for Admission';
    const mlBadgeClass = isEligible ? 'badge-eligible' : 'badge-not-eligible';
    const statusBadgeClass = getBadgeClass(app.status);

    return `
      <tr>
        <td><strong>${app.application_no}</strong></td>
        <td>
          <div style="font-weight: 700;">${escapeHtml(app.full_name)}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted);">${escapeHtml(app.email)}</div>
        </td>
        <td style="max-width: 220px;">
          <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;">
            ${escapeHtml(app.course_name || app.course_code)}
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${app.course_code}</div>
        </td>
        <td><strong>${app.academic_gpa}%</strong></td>
        <td><strong>${app.entrance_score}</strong></td>
        <td><span style="font-size: 0.8rem; font-weight: 600;">${app.category}</span></td>
        <td>
          <span class="badge ${mlBadgeClass}">${app.ml_prediction || 'Evaluated'}</span>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">
            Prob: <strong>${probPct}</strong>
          </div>
        </td>
        <td>
          <span class="badge ${statusBadgeClass}">${app.status}</span>
        </td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="openApplicationModal(${app.id})">
            🔍 Review & AI Dossier
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function openApplicationModal(appId) {
  activeAppId = appId;
  const modal = document.getElementById('app-modal');
  modal.classList.add('active');

  try {
    const res = await api.getApplicationDetail(appId);
    const app = res.application;

    document.getElementById('modal-app-no').innerText = app.application_no;
    document.getElementById('modal-candidate-name').innerText = `(${app.full_name})`;
    document.getElementById('modal-course').innerText = `${app.course_name} (${app.course_code})`;
    document.getElementById('modal-date').innerText = new Date(app.submitted_at).toLocaleDateString();

    const statusBadge = document.getElementById('modal-status-badge');
    statusBadge.innerText = app.status;
    statusBadge.className = 'badge ' + getBadgeClass(app.status);

    // Profile table
    document.getElementById('m-email').innerText = app.email;
    document.getElementById('m-phone').innerText = app.phone;
    document.getElementById('m-dob-gender').innerText = `${app.dob} • ${app.gender}`;
    document.getElementById('m-category').innerText = app.category;
    document.getElementById('m-ec').innerText = app.extracurricular.replace('_', ' ');
    document.getElementById('m-gpa').innerText = `${app.academic_gpa}%`;
    document.getElementById('m-entrance').innerText = `${app.entrance_score} / 100`;
    document.getElementById('m-attendance').innerText = `${app.attendance_pct}%`;
    document.getElementById('m-prev').innerText = `${app.prev_academic_score}%`;

    // Doc preview
    const docBox = document.getElementById('m-doc-container');
    if (app.document_name) {
      docBox.innerHTML = `
        <a href="/uploads/${app.document_path ? app.document_path.split('\\').pop().split('/').pop() : ''}" target="_blank" class="btn btn-secondary btn-sm">
          📄 View ${escapeHtml(app.document_name)}
        </a>
      `;
    } else {
      docBox.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No files uploaded</span>';
    }

    // ML Module Info
    const probPct = (app.ml_probability ? (app.ml_probability * 100).toFixed(1) : '0.0') + '%';
    document.getElementById('m-ml-prob').innerText = probPct;
    document.getElementById('m-ml-meter').style.width = probPct;
    
    const mlBadge = document.getElementById('m-ml-badge');
    mlBadge.innerText = app.ml_prediction || 'Evaluated';
    mlBadge.className = 'badge ' + (app.ml_prediction === 'Eligible for Admission' ? 'badge-eligible' : 'badge-not-eligible');

    // GenAI Section
    document.getElementById('m-ai-summary').innerText = app.ai_evaluation_summary || 'No AI summary generated yet.';
    document.getElementById('m-ai-recommendation').innerText = app.ai_recommendation || 'Pending evaluation';
    document.getElementById('m-ai-explanation').innerText = app.ai_explanation || 'Pending evaluation';
    document.getElementById('m-ai-insights').innerText = app.ai_profile_insights || 'Pending evaluation';

    // Remarks field
    document.getElementById('m-admin-remarks').value = app.admin_remarks || '';

  } catch (err) {
    showToast(`Error opening application: ${err.message}`, 'error');
    closeModal();
  }
}

function closeModal() {
  const modal = document.getElementById('app-modal');
  modal.classList.remove('active');
  activeAppId = null;
}

async function regenerateAIEvaluation() {
  if (!activeAppId) return;

  const btn = document.getElementById('btn-regen-ai');
  const directive = document.getElementById('ai-custom-directive').value.trim();

  btn.disabled = true;
  btn.innerText = '✨ Generating Report...';

  try {
    const res = await api.evaluateApplication(activeAppId, directive);
    if (res.success) {
      const rep = res.report;
      document.getElementById('m-ai-summary').innerText = rep.evaluation_summary;
      document.getElementById('m-ai-recommendation').innerText = rep.admission_recommendation;
      document.getElementById('m-ai-explanation').innerText = rep.approval_rejection_explanation;
      document.getElementById('m-ai-insights').innerText = rep.profile_insights;

      showToast('AI Evaluation Dossier updated successfully!', 'success');
      await loadApplications();
    }
  } catch (err) {
    showToast(`AI generation failed: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerText = '🔄 Regenerate AI Evaluation';
  }
}

async function saveStatusChange(newStatus) {
  if (!activeAppId) return;

  const remarks = document.getElementById('m-admin-remarks').value.trim();

  try {
    const res = await api.updateApplicationStatus(activeAppId, newStatus, remarks);
    if (res.success) {
      showToast(`Admission status updated to "${newStatus}"!`, 'success');
      
      const badge = document.getElementById('modal-status-badge');
      badge.innerText = newStatus;
      badge.className = 'badge ' + getBadgeClass(newStatus);

      await loadApplications();
    }
  } catch (err) {
    showToast(`Status update failed: ${err.message}`, 'error');
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

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}
