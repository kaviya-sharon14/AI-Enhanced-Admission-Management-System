/**
 * Reports & Analytics Dashboard Charts Logic (Chart.js)
 */

let coursesChartInstance = null;
let statusChartInstance = null;
let categoryChartInstance = null;
let ecChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadAnalytics();
});

async function loadAnalytics() {
  try {
    const res = await api.getAnalyticsSummary();
    if (!res.success) return;

    const summary = res.summary;
    const courses = res.courses;
    const statusData = res.status_breakdown;
    const catData = res.category_stats;
    const ecData = res.extracurricular_stats;

    // Update KPI cards
    document.getElementById('stat-kpi-total').innerText = summary.total_applications;
    document.getElementById('stat-kpi-acceptance').innerText = `${summary.acceptance_rate}%`;
    document.getElementById('stat-kpi-gpa').innerText = `${summary.avg_gpa}%`;
    document.getElementById('stat-kpi-entrance').innerText = `${summary.avg_entrance_score} / 100`;
    document.getElementById('stat-kpi-ml').innerText = `${summary.ml_eligible_rate}%`;

    // Render Charts
    renderCoursesChart(courses);
    renderStatusChart(statusData);
    renderCategoryChart(catData);
    renderECChart(ecData);

  } catch (err) {
    console.error('Failed to load analytics:', err);
    showToast('Failed to load analytics data', 'error');
  }
}

function renderCoursesChart(courses) {
  const ctx = document.getElementById('coursesChart').getContext('2d');
  if (coursesChartInstance) coursesChartInstance.destroy();

  const labels = courses.map(c => c.name.length > 25 ? c.name.substring(0, 22) + '...' : c.name);
  const data = courses.map(c => c.count);

  coursesChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Applications Received',
        data: data,
        backgroundColor: '#4361ee',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  });
}

function renderStatusChart(statusData) {
  const ctx = document.getElementById('statusChart').getContext('2d');
  if (statusChartInstance) statusChartInstance.destroy();

  const colorMap = {
    'Approved': '#10b981',
    'Rejected': '#ef4444',
    'Under Review': '#f59e0b',
    'Submitted': '#0ea5e9',
    'Waitlisted': '#8b5cf6'
  };

  const labels = statusData.map(s => s.status);
  const data = statusData.map(s => s.count);
  const bgColors = labels.map(l => colorMap[l] || '#94a3b8');

  statusChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: bgColors,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });
}

function renderCategoryChart(catData) {
  const ctx = document.getElementById('categoryChart').getContext('2d');
  if (categoryChartInstance) categoryChartInstance.destroy();

  const labels = catData.map(c => c.category);
  const data = catData.map(c => c.count);

  categoryChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });
}

function renderECChart(ecData) {
  const ctx = document.getElementById('ecChart').getContext('2d');
  if (ecChartInstance) ecChartInstance.destroy();

  const labels = ecData.map(e => e.extracurricular.replace('_', ' '));
  const data = ecData.map(e => e.count);

  ecChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: ['#64748b', '#3b82f6', '#10b981', '#ec4899'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right'
        }
      }
    }
  });
}
