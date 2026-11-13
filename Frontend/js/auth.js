/**
 * Authentication and Navigation State Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  renderNavbarAuth();
});

function renderNavbarAuth() {
  const user = api.getUser();
  const token = api.getToken();
  const navContainer = document.getElementById('nav-auth-container');
  
  if (!navContainer) return;
  
  if (token && user) {
    const isCurrentAdmin = user.role === 'admin';
    navContainer.innerHTML = `
      <div class="user-badge">
        <div class="user-avatar">${user.name.charAt(0).toUpperCase()}</div>
        <span>${user.name} (${user.role.toUpperCase()})</span>
      </div>
      ${isCurrentAdmin 
        ? '<a href="/admin" class="btn btn-sm btn-primary">Admin Portal</a>'
        : '<a href="/student" class="btn btn-sm btn-primary">My Portal</a>'
      }
      <button onclick="handleLogout()" class="btn btn-sm btn-secondary">Logout</button>
    `;
  } else {
    navContainer.innerHTML = `
      <a href="/login" class="btn btn-sm btn-primary">Sign In / Register</a>
    `;
  }
}

function handleLogout() {
  api.clearAuth();
  showToast('Logged out successfully', 'info');
  setTimeout(() => {
    window.location.href = '/login';
  }, 400);
}

function requireAuth(roleRequired = null) {
  const token = api.getToken();
  const user = api.getUser();
  
  if (!token || !user) {
    window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
    return false;
  }
  
  if (roleRequired && user.role !== roleRequired) {
    showToast(`Access restricted to ${roleRequired}s only.`, 'error');
    if (user.role === 'admin') window.location.href = '/admin';
    else window.location.href = '/student';
    return false;
  }
  return true;
}
