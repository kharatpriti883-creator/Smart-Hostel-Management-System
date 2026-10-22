/* Smart Hostel Management & Resource Optimization System - Frontend REST Client */

// Helper: General Fetch API Wrapper
async function fetchAPI(endpoint, options = {}) {
  options.headers = options.headers || {};
  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(endpoint, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'An unexpected error occurred.');
    }
    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err.message);
    throw err;
  }
}

// Alert / Toast Notification Helper
function showAlert(message, type = 'success', elementId = 'alert-container') {
  const container = document.getElementById(elementId);
  if (!container) return;

  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type}`;
  alertDiv.style.padding = '0.75rem 1.25rem';
  alertDiv.style.marginBottom = '1rem';
  alertDiv.style.borderRadius = '6px';
  alertDiv.style.fontWeight = '500';
  
  if (type === 'success') {
    alertDiv.style.background = '#d1fae5';
    alertDiv.style.color = '#065f46';
    alertDiv.style.border = '1px solid #a7f3d0';
  } else {
    alertDiv.style.background = '#fee2e2';
    alertDiv.style.color = '#991b1b';
    alertDiv.style.border = '1px solid #fca5a5';
  }

  alertDiv.innerText = message;
  container.innerHTML = '';
  container.appendChild(alertDiv);

  setTimeout(() => {
    alertDiv.remove();
  }, 4000);
}

// Modal Control Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

// Global Logout Handler
async function handleLogout() {
  try {
    await fetchAPI('/api/logout', { method: 'POST' });
    window.location.href = '/';
  } catch (e) {
    window.location.href = '/';
  }
}

// Status Badge Formatter Helper
function getStatusBadge(status) {
  status = status ? status.trim() : '';
  let badgeClass = 'badge-info';
  if (['Paid', 'Approved', 'Resolved', 'Normal', 'Present', 'Available'].includes(status)) {
    badgeClass = 'badge-success';
  } else if (['Pending', 'Partial', 'In Progress', 'Warning', 'High Usage'].includes(status)) {
    badgeClass = 'badge-warning';
  } else if (['Rejected', 'Full', 'Absent', 'Maintenance Needed', 'Maintenance'].includes(status)) {
    badgeClass = 'badge-danger';
  }
  return `<span class="badge ${badgeClass}">${status}</span>`;
}


// ========================================================
// PAGE SPECIFIC INITIALIZERS
// ========================================================

// 1. Student Login Page Handler
function initStudentLogin() {
  const form = document.getElementById('student-login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = form.username.value;
    const password = form.password.value;

    try {
      const res = await fetchAPI('/api/login/student', {
        method: 'POST',
        body: { username, password }
      });
      showAlert('Login successful! Redirecting to Dashboard...', 'success', 'login-alert');
      setTimeout(() => {
        window.location.href = res.redirect || '/student/dashboard';
      }, 800);
    } catch (err) {
      showAlert(err.message, 'danger', 'login-alert');
    }
  });
}

// 2. Warden Login Page Handler
function initWardenLogin() {
  const form = document.getElementById('warden-login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = form.username.value;
    const password = form.password.value;

    try {
      const res = await fetchAPI('/api/login/warden', {
        method: 'POST',
        body: { username, password }
      });
      showAlert('Warden Authentication Verified! Redirecting...', 'success', 'login-alert');
      setTimeout(() => {
        window.location.href = res.redirect || '/warden/dashboard';
      }, 800);
    } catch (err) {
      showAlert(err.message, 'danger', 'login-alert');
    }
  });
}

// 3. Student Dashboard Loader
async function loadStudentDashboard() {
  const dashboardContainer = document.getElementById('student-dashboard-content');
  if (!dashboardContainer) return;

  try {
    const stats = await fetchAPI('/api/dashboard/stats');
    const info = stats.student_info || {};

    // Populate Cards
    document.getElementById('st-name').innerText = info.name || 'Student';
    document.getElementById('st-room').innerText = info.room_number ? `Room ${info.room_number}` : 'Unallocated';
    document.getElementById('st-fee-status').innerHTML = getStatusBadge(info.payment_status || 'Pending');
    document.getElementById('st-att-pct').innerText = `${stats.attendance_pct || 0}%`;
    document.getElementById('st-complaints-count').innerText = stats.pending_complaints || 0;
    
    const latestLeave = stats.latest_leave;
    document.getElementById('st-leave-status').innerHTML = latestLeave ? getStatusBadge(latestLeave.status) : 'No Requests';

    // Populate Notices Widget
    const noticeList = document.getElementById('recent-notices-list');
    if (noticeList && stats.active_notices) {
      if (stats.active_notices.length === 0) {
        noticeList.innerHTML = '<p class="text-muted">No active notices published.</p>';
      } else {
        noticeList.innerHTML = stats.active_notices.map(n => `
          <div style="padding: 0.85rem 0; border-bottom: 1px solid var(--border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h4 style="font-size: 0.95rem; font-weight: 600;">${n.title}</h4>
              <span style="font-size: 0.75rem; color: var(--text-muted);">${n.date}</span>
            </div>
            <p style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem;">${n.description}</p>
          </div>
        `).join('');
      }
    }
  } catch (e) {
    console.error('Failed loading student dashboard stats:', e);
  }
}

// 4. Student Profile Page
async function loadStudentProfile() {
  const profileForm = document.getElementById('student-profile-form');
  if (!profileForm) return;

  try {
    const me = await fetchAPI('/api/me');
    const details = me.details || {};

    document.getElementById('prof-name').innerText = details.name;
    document.getElementById('prof-roll').innerText = details.roll_number;
    document.getElementById('prof-branch').innerText = details.branch;
    document.getElementById('prof-year').innerText = `Year ${details.year}`;
    document.getElementById('prof-room').innerText = details.room_number ? `Room ${details.room_number}` : 'Unallocated';
    document.getElementById('prof-parent-name').innerText = details.parent_name;
    document.getElementById('prof-parent-phone').innerText = details.parent_phone;
    document.getElementById('prof-parent-email').innerText = details.parent_email;

    profileForm.phone.value = details.phone || '';
    profileForm.email.value = details.email || '';

    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI(`/api/students/${details.id}`, {
          method: 'PUT',
          body: {
            phone: profileForm.phone.value,
            email: profileForm.email.value
          }
        });
        showAlert('Contact details updated successfully!', 'success', 'profile-alert');
      } catch (err) {
        showAlert(err.message, 'danger', 'profile-alert');
      }
    });
  } catch (e) {
    console.error(e);
  }
}

// 5. Student Room Details Page
async function loadStudentRoomDetails() {
  const roomContainer = document.getElementById('student-room-details');
  if (!roomContainer) return;

  try {
    const rooms = await fetchAPI('/api/rooms');
    const me = await fetchAPI('/api/me');
    const myRoomId = me.details ? me.details.room_id : null;

    if (!myRoomId) {
      roomContainer.innerHTML = '<div class="card"><p class="text-muted">You are currently not assigned to any room. Please contact Warden Office.</p></div>';
      return;
    }

    const myRoom = rooms.find(r => r.id === myRoomId);
    if (!myRoom) return;

    document.getElementById('rm-number').innerText = myRoom.room_number;
    document.getElementById('rm-block').innerText = myRoom.block;
    document.getElementById('rm-floor').innerText = `Floor ${myRoom.floor}`;
    document.getElementById('rm-type').innerText = myRoom.room_type;
    document.getElementById('rm-capacity').innerText = myRoom.capacity;
    document.getElementById('rm-occupied').innerText = myRoom.occupied_beds;
    document.getElementById('rm-available').innerText = myRoom.available_beds;

    // Roommates list
    const roommatesTbody = document.getElementById('roommates-tbody');
    if (roommatesTbody && myRoom.occupants) {
      roommatesTbody.innerHTML = myRoom.occupants.map(o => `
        <tr>
          <td><strong>${o.name}</strong></td>
          <td>${o.roll_number}</td>
          <td>${o.branch}</td>
          <td>Year ${o.year}</td>
        </tr>
      `).join('');
    }
  } catch (e) {
    console.error(e);
  }
}

// 6. Student Fees Page & Printable Receipt
async function loadStudentFees() {
  const feesTable = document.getElementById('student-fees-tbody');
  if (!feesTable) return;

  try {
    const fees = await fetchAPI('/api/fees');
    const fee = fees[0];
    if (!fee) return;

    document.getElementById('fee-total').innerText = `₹${parseFloat(fee.total_amount).toLocaleString('en-IN')}`;
    document.getElementById('fee-paid').innerText = `₹${parseFloat(fee.paid_amount).toLocaleString('en-IN')}`;
    document.getElementById('fee-pending').innerText = `₹${parseFloat(fee.pending_amount).toLocaleString('en-IN')}`;
    document.getElementById('fee-status-badge').innerHTML = getStatusBadge(fee.payment_status);

    feesTable.innerHTML = `
      <tr>
        <td>Annual Hostel Term Fee</td>
        <td>₹${parseFloat(fee.total_amount).toLocaleString('en-IN')}</td>
        <td>₹${parseFloat(fee.paid_amount).toLocaleString('en-IN')}</td>
        <td>₹${parseFloat(fee.pending_amount).toLocaleString('en-IN')}</td>
        <td>${fee.payment_date || 'N/A'}</td>
        <td>${getStatusBadge(fee.payment_status)}</td>
        <td>
          <button class="btn btn-primary" onclick="viewFeeReceipt(${fee.student_id})">
            <i class="fas fa-file-invoice"></i> Receipt
          </button>
        </td>
      </tr>
    `;
  } catch (e) {
    console.error(e);
  }
}

async function viewFeeReceipt(studentId) {
  try {
    const rec = await fetchAPI(`/api/fees/receipt/${studentId}`);
    document.getElementById('rc-no').innerText = rec.receipt_number || `REC-2026-${rec.student_id}`;
    document.getElementById('rc-date').innerText = rec.payment_date ? new Date(rec.payment_date).toLocaleDateString() : new Date().toLocaleDateString();
    document.getElementById('rc-st-name').innerText = rec.student_name;
    document.getElementById('rc-roll').innerText = rec.roll_number;
    document.getElementById('rc-room').innerText = rec.room_number ? `Room ${rec.room_number}` : 'N/A';
    document.getElementById('rc-branch').innerText = `${rec.branch} (Year ${rec.year})`;
    document.getElementById('rc-total').innerText = `₹${parseFloat(rec.total_amount).toLocaleString('en-IN')}`;
    document.getElementById('rc-paid').innerText = `₹${parseFloat(rec.paid_amount).toLocaleString('en-IN')}`;
    document.getElementById('rc-pending').innerText = `₹${parseFloat(rec.pending_amount).toLocaleString('en-IN')}`;
    document.getElementById('rc-status').innerHTML = getStatusBadge(rec.payment_status);
    openModal('receipt-modal');
  } catch (err) {
    alert(err.message);
  }
}

function printReceipt() {
  window.print();
}

// 7. Student Complaints Page
async function loadStudentComplaints() {
  const tbody = document.getElementById('student-complaints-tbody');
  const form = document.getElementById('complaint-form');
  if (!tbody) return;

  const loadList = async () => {
    try {
      const list = await fetchAPI('/api/complaints');
      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No complaints lodged.</td></tr>';
        return;
      }
      tbody.innerHTML = list.map(c => `
        <tr>
          <td><span class="badge badge-info">${c.category}</span></td>
          <td><strong>${c.title}</strong><br><small style="color:var(--text-muted);">${c.description}</small></td>
          <td>${new Date(c.created_at).toLocaleDateString()}</td>
          <td>${getStatusBadge(c.status)}</td>
          <td>${c.warden_response ? c.warden_response : '<span class="text-muted">Awaiting response</span>'}</td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await loadList();

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/complaints', {
          method: 'POST',
          body: {
            category: form.category.value,
            title: form.title.value,
            description: form.description.value
          }
        });
        showAlert('Complaint submitted successfully to Warden office!', 'success', 'complaint-alert');
        form.reset();
        loadList();
      } catch (err) {
        showAlert(err.message, 'danger', 'complaint-alert');
      }
    });
  }
}

// 8. Student Leave Page
async function loadStudentLeave() {
  const tbody = document.getElementById('student-leave-tbody');
  const form = document.getElementById('leave-form');
  if (!tbody) return;

  const loadList = async () => {
    try {
      const list = await fetchAPI('/api/leaves');
      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No leave applications found.</td></tr>';
        return;
      }
      tbody.innerHTML = list.map(l => `
        <tr>
          <td>${l.start_date}</td>
          <td>${l.end_date}</td>
          <td>${l.reason}</td>
          <td>${getStatusBadge(l.status)}</td>
          <td>${l.warden_remark ? l.warden_remark : '-'}</td>
          <td>${new Date(l.created_at).toLocaleDateString()}</td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await loadList();

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/leaves', {
          method: 'POST',
          body: {
            start_date: form.start_date.value,
            end_date: form.end_date.value,
            reason: form.reason.value
          }
        });
        showAlert('Leave application lodged! Parent email notification queued upon Warden response.', 'success', 'leave-alert');
        form.reset();
        loadList();
      } catch (err) {
        showAlert(err.message, 'danger', 'leave-alert');
      }
    });
  }
}

// 9. Student Attendance Page & QR/Biometric Simulation
async function loadStudentAttendance() {
  const tbody = document.getElementById('student-attendance-tbody');
  if (!tbody) return;

  const loadList = async () => {
    try {
      const list = await fetchAPI('/api/attendance');
      const presentCount = list.filter(a => a.status === 'Present').length;
      const totalCount = list.length;
      const pct = totalCount > 0 ? ((presentCount / totalCount) * 100).toFixed(2) : 100.0;

      document.getElementById('att-summary-present').innerText = presentCount;
      document.getElementById('att-summary-total').innerText = totalCount;
      document.getElementById('att-summary-pct').innerText = `${pct}%`;

      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted" style="text-align:center;">No attendance records found.</td></tr>';
        return;
      }
      tbody.innerHTML = list.map(a => `
        <tr>
          <td>${a.date}</td>
          <td>${a.check_in_time || 'N/A'}</td>
          <td>${getStatusBadge(a.status)}</td>
          <td><span class="badge badge-info">${a.verification_method}</span></td>
          <td>${a.marked_by}</td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await loadList();
}

async function simulateQRAttendance() {
  try {
    const res = await fetchAPI('/api/attendance', {
      method: 'POST',
      body: { verification_method: 'QR_Hostel_WiFi' }
    });
    alert(res.message);
    loadStudentAttendance();
  } catch (err) {
    alert(err.message);
  }
}


// ========================================================
// WARDEN ADMIN MANAGEMENT FUNCTIONS
// ========================================================

// Warden Dashboard Loader with Chart.js Visualization
async function loadWardenDashboard() {
  const container = document.getElementById('warden-dashboard-content');
  if (!container) return;

  try {
    const stats = await fetchAPI('/api/dashboard/stats');

    document.getElementById('w-total-students').innerText = stats.total_students || 0;
    document.getElementById('w-total-rooms').innerText = stats.total_rooms || 0;
    document.getElementById('w-available-beds').innerText = stats.available_beds || 0;
    document.getElementById('w-pending-fees').innerText = stats.pending_fees_count || 0;
    document.getElementById('w-pending-complaints').innerText = stats.pending_complaints_count || 0;
    document.getElementById('w-pending-leaves').innerText = stats.pending_leaves_count || 0;
    document.getElementById('w-avg-attendance').innerText = `${stats.avg_attendance || 100}%`;

    // Render Resource Monitor Quick Feed
    const resFeed = document.getElementById('warden-resource-feed');
    if (resFeed && stats.resources) {
      resFeed.innerHTML = stats.resources.map(r => `
        <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.75rem 0; border-bottom:1px solid var(--border);">
          <div>
            <strong>${r.metric_name}</strong> (${r.resource_type})
            <div style="font-size:0.8rem; color:var(--text-muted);">${r.remarks || ''}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-weight:700; font-size:1.1rem;">${r.usage_value} ${r.unit}</div>
            ${getStatusBadge(r.status)}
          </div>
        </div>
      `).join('');
    }

    // Chart.js - Render Attendance & Room Occupancy Charts if canvas exists
    const attChartCtx = document.getElementById('attendanceChart');
    if (attChartCtx && window.Chart) {
      new Chart(attChartCtx, {
        type: 'doughnut',
        data: {
          labels: ['Present (%)', 'Absent (%)'],
          datasets: [{
            data: [stats.avg_attendance, (100 - stats.avg_attendance).toFixed(2)],
            backgroundColor: ['#10b981', '#ef4444']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  } catch (e) {
    console.error(e);
  }
}

// Warden Student Management
async function loadWardenStudents() {
  const tbody = document.getElementById('warden-students-tbody');
  const addForm = document.getElementById('add-student-form');
  const searchInput = document.getElementById('student-search-input');
  if (!tbody) return;

  let studentsList = [];

  const renderTable = (list) => {
    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-muted" style="text-align:center;">No student records found.</td></tr>';
      return;
    }
    tbody.innerHTML = list.map(s => `
      <tr>
        <td><strong>${s.name}</strong><br><small style="color:var(--text-muted);">${s.username}</small></td>
        <td>${s.roll_number}</td>
        <td>${s.branch} (Yr ${s.year})</td>
        <td>${s.room_number ? 'Room ' + s.room_number : '<span class="badge badge-warning">Unassigned</span>'}</td>
        <td>${s.phone}<br><small style="color:var(--text-muted);">${s.email}</small></td>
        <td>${getStatusBadge(s.payment_status || 'Pending')}</td>
        <td>
          <button class="btn btn-outline" style="padding:0.35rem 0.65rem;" onclick="openAllocateRoomModal(${s.id}, '${s.name.replace(/'/g, "\\'")}')">
            <i class="fas fa-bed"></i> Room
          </button>
          <button class="btn btn-danger" style="padding:0.35rem 0.65rem;" onclick="deleteStudent(${s.id}, '${s.name.replace(/'/g, "\\'")}')">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  };

  const fetchStudents = async () => {
    try {
      studentsList = await fetchAPI('/api/students');
      renderTable(studentsList);
    } catch (e) {
      console.error(e);
    }
  };

  await fetchStudents();

  // Search filter
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = studentsList.filter(s => 
        s.name.toLowerCase().includes(q) || 
        s.roll_number.toLowerCase().includes(q) || 
        s.username.toLowerCase().includes(q)
      );
      renderTable(filtered);
    });
  }

  // Add Student submit
  if (addForm) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/students', {
          method: 'POST',
          body: {
            name: addForm.name.value,
            username: addForm.username.value,
            password: addForm.password.value,
            roll_number: addForm.roll_number.value,
            branch: addForm.branch.value,
            year: addForm.year.value,
            phone: addForm.phone.value,
            email: addForm.email.value,
            parent_name: addForm.parent_name.value,
            parent_email: addForm.parent_email.value,
            parent_phone: addForm.parent_phone.value,
            room_id: addForm.room_id.value ? parseInt(addForm.room_id.value) : null
          }
        });
        showAlert('New student registered in PostgreSQL successfully!', 'success', 'student-modal-alert');
        addForm.reset();
        setTimeout(() => {
          closeModal('add-student-modal');
          fetchStudents();
        }, 1000);
      } catch (err) {
        showAlert(err.message, 'danger', 'student-modal-alert');
      }
    });
  }

  // Populate room dropdown in add modal
  try {
    const rooms = await fetchAPI('/api/rooms');
    const roomSelect = document.getElementById('add-st-room-select');
    if (roomSelect) {
      roomSelect.innerHTML = '<option value="">-- Assign Later --</option>' + rooms.map(r => `
        <option value="${r.id}" ${r.available_beds <= 0 ? 'disabled' : ''}>
          ${r.room_number} (${r.block}) - ${r.available_beds} beds free
        </option>
      `).join('');
    }
  } catch (e) {
    console.error(e);
  }
}

async function deleteStudent(id, name) {
  if (!confirm(`Are you sure you want to delete student "${name}"? This action will remove all student records from PostgreSQL.`)) return;
  try {
    await fetchAPI(`/api/students/${id}`, { method: 'DELETE' });
    alert('Student record deleted successfully.');
    loadWardenStudents();
  } catch (err) {
    alert(err.message);
  }
}

async function openAllocateRoomModal(studentId, studentName) {
  document.getElementById('alloc-st-id').value = studentId;
  document.getElementById('alloc-st-name').innerText = studentName;

  try {
    const rooms = await fetchAPI('/api/rooms');
    const select = document.getElementById('alloc-room-select');
    select.innerHTML = rooms.map(r => `
      <option value="${r.id}" ${r.available_beds <= 0 ? 'disabled' : ''}>
        Room ${r.room_number} (${r.block}, Floor ${r.floor}) - ${r.occupied_beds}/${r.capacity} beds (${r.available_beds} free)
      </option>
    `).join('');
    openModal('allocate-room-modal');
  } catch (err) {
    alert(err.message);
  }
}

async function submitRoomAllocation() {
  const studentId = document.getElementById('alloc-st-id').value;
  const roomId = document.getElementById('alloc-room-select').value;

  try {
    const res = await fetchAPI(`/api/rooms/${roomId}/allocate`, {
      method: 'POST',
      body: { student_id: parseInt(studentId) }
    });
    alert(res.message);
    closeModal('allocate-room-modal');
    loadWardenStudents();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Rooms Management
async function loadWardenRooms() {
  const container = document.getElementById('warden-rooms-grid');
  const addForm = document.getElementById('add-room-form');
  if (!container) return;

  const fetchRooms = async () => {
    try {
      const rooms = await fetchAPI('/api/rooms');
      container.innerHTML = rooms.map(r => `
        <div class="card" style="margin-bottom:0;">
          <div class="card-header" style="padding-bottom:0.5rem; margin-bottom:0.75rem;">
            <h3 style="font-size:1.2rem;">Room ${r.room_number}</h3>
            ${getStatusBadge(r.status)}
          </div>
          <div style="font-size:0.9rem; color:var(--text-muted); margin-bottom:0.75rem;">
            <div><strong>Block:</strong> ${r.block} | <strong>Floor:</strong> ${r.floor}</div>
            <div><strong>Type:</strong> ${r.room_type}</div>
            <div style="margin-top:0.35rem;">
              <strong>Bed Occupancy:</strong> ${r.occupied_beds} / ${r.capacity} 
              (${r.available_beds} beds available)
            </div>
          </div>
          <div>
            <h4 style="font-size:0.85rem; font-weight:600; text-transform:uppercase; margin-bottom:0.35rem; color:var(--text-dark);">Current Occupants:</h4>
            ${r.occupants && r.occupants.length > 0 ? 
              r.occupants.map(o => `<div style="font-size:0.85rem; background:#f1f5f9; padding:0.25rem 0.5rem; border-radius:4px; margin-bottom:0.25rem;">👤 ${o.name} (${o.roll_number})</div>`).join('') 
              : '<span class="text-muted" style="font-size:0.85rem;">Room is empty</span>'
            }
          </div>
        </div>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchRooms();

  if (addForm) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/rooms', {
          method: 'POST',
          body: {
            room_number: addForm.room_number.value,
            block: addForm.block.value,
            floor: parseInt(addForm.floor.value),
            room_type: addForm.room_type.value,
            capacity: parseInt(addForm.capacity.value)
          }
        });
        showAlert('New hostel room added successfully!', 'success', 'room-modal-alert');
        addForm.reset();
        setTimeout(() => {
          closeModal('add-room-modal');
          fetchRooms();
        }, 1000);
      } catch (err) {
        showAlert(err.message, 'danger', 'room-modal-alert');
      }
    });
  }
}

// Warden Fee Management
async function loadWardenFees() {
  const tbody = document.getElementById('warden-fees-tbody');
  if (!tbody) return;

  const fetchFees = async () => {
    try {
      const list = await fetchAPI('/api/fees');
      tbody.innerHTML = list.map(f => `
        <tr>
          <td><strong>${f.student_name}</strong><br><small style="color:var(--text-muted);">${f.roll_number}</small></td>
          <td>${f.room_number ? 'Room ' + f.room_number : 'Unassigned'}</td>
          <td>₹${parseFloat(f.total_amount).toLocaleString('en-IN')}</td>
          <td>₹${parseFloat(f.paid_amount).toLocaleString('en-IN')}</td>
          <td>₹${parseFloat(f.pending_amount).toLocaleString('en-IN')}</td>
          <td>${getStatusBadge(f.payment_status)}</td>
          <td>
            <button class="btn btn-outline" style="padding:0.35rem 0.65rem;" onclick="openUpdateFeeModal(${f.id}, '${f.student_name.replace(/'/g, "\\'")}', ${f.total_amount}, ${f.paid_amount})">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-primary" style="padding:0.35rem 0.65rem;" onclick="viewFeeReceipt(${f.student_id})">
              <i class="fas fa-receipt"></i> Receipt
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchFees();
}

function openUpdateFeeModal(feeId, studentName, totalAmount, paidAmount) {
  document.getElementById('edit-fee-id').value = feeId;
  document.getElementById('edit-fee-st-name').innerText = studentName;
  document.getElementById('edit-fee-paid').value = paidAmount;
  openModal('update-fee-modal');
}

async function submitFeeUpdate() {
  const feeId = document.getElementById('edit-fee-id').value;
  const paidAmount = parseFloat(document.getElementById('edit-fee-paid').value);

  try {
    const res = await fetchAPI(`/api/fees/${feeId}`, {
      method: 'PUT',
      body: { paid_amount: paidAmount }
    });
    alert(res.message);
    closeModal('update-fee-modal');
    loadWardenFees();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Complaints Desk
async function loadWardenComplaints() {
  const tbody = document.getElementById('warden-complaints-tbody');
  if (!tbody) return;

  const fetchComplaints = async () => {
    try {
      const list = await fetchAPI('/api/complaints');
      tbody.innerHTML = list.map(c => `
        <tr>
          <td><strong>${c.student_name}</strong><br><small style="color:var(--text-muted);">${c.roll_number} (${c.room_number ? 'Room ' + c.room_number : 'N/A'})</small></td>
          <td><span class="badge badge-info">${c.category}</span></td>
          <td><strong>${c.title}</strong><br><small style="color:var(--text-muted);">${c.description}</small></td>
          <td>${new Date(c.created_at).toLocaleDateString()}</td>
          <td>${getStatusBadge(c.status)}</td>
          <td>${c.warden_response ? c.warden_response : '<span class="text-muted">No response yet</span>'}</td>
          <td>
            <button class="btn btn-primary" style="padding:0.35rem 0.65rem;" onclick="openUpdateComplaintModal(${c.id}, '${c.title.replace(/'/g, "\\'")}', '${c.status}', '${(c.warden_response || '').replace(/'/g, "\\'")}')">
              <i class="fas fa-reply"></i> Update
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchComplaints();
}

function openUpdateComplaintModal(id, title, status, response) {
  document.getElementById('c-id').value = id;
  document.getElementById('c-title').innerText = title;
  document.getElementById('c-status-select').value = status;
  document.getElementById('c-response-text').value = response;
  openModal('update-complaint-modal');
}

async function submitComplaintUpdate() {
  const id = document.getElementById('c-id').value;
  const status = document.getElementById('c-status-select').value;
  const warden_response = document.getElementById('c-response-text').value;

  try {
    const res = await fetchAPI(`/api/complaints/${id}`, {
      method: 'PUT',
      body: { status, warden_response }
    });
    alert(res.message);
    closeModal('update-complaint-modal');
    loadWardenComplaints();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Leave Desk
async function loadWardenLeave() {
  const tbody = document.getElementById('warden-leave-tbody');
  if (!tbody) return;

  const fetchLeaves = async () => {
    try {
      const list = await fetchAPI('/api/leaves');
      tbody.innerHTML = list.map(l => `
        <tr>
          <td><strong>${l.student_name}</strong><br><small style="color:var(--text-muted);">${l.roll_number} (${l.room_number ? 'Room ' + l.room_number : 'N/A'})</small></td>
          <td>${l.start_date} to ${l.end_date}</td>
          <td>${l.reason}</td>
          <td><strong>${l.parent_name}</strong><br><small style="color:var(--text-muted);">${l.parent_email} (${l.parent_phone})</small></td>
          <td>${getStatusBadge(l.status)}</td>
          <td>
            ${l.status === 'Pending' ? `
              <button class="btn btn-success" style="padding:0.35rem 0.65rem;" onclick="processLeave(${l.id}, 'Approved')">
                <i class="fas fa-check"></i> Approve
              </button>
              <button class="btn btn-danger" style="padding:0.35rem 0.65rem;" onclick="processLeave(${l.id}, 'Rejected')">
                <i class="fas fa-times"></i> Reject
              </button>
            ` : `<span class="text-muted">${l.warden_remark || 'Processed'}</span>`}
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchLeaves();
}

async function processLeave(leaveId, targetStatus) {
  const remark = prompt(`Enter Warden remark for ${targetStatus} leave status:`);
  if (remark === null) return;

  try {
    const res = await fetchAPI(`/api/leaves/${leaveId}`, {
      method: 'PUT',
      body: { status: targetStatus, warden_remark: remark }
    });
    alert(res.message);
    loadWardenLeave();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Attendance Roster
async function loadWardenAttendance() {
  const tbody = document.getElementById('warden-attendance-tbody');
  const datePicker = document.getElementById('att-date-picker');
  if (!tbody) return;

  if (datePicker && !datePicker.value) {
    datePicker.value = new Date().toISOString().split('T')[0];
  }

  const fetchAttendance = async () => {
    const targetDate = datePicker ? datePicker.value : new Date().toISOString().split('T')[0];
    try {
      const list = await fetchAPI(`/api/attendance?date=${targetDate}`);
      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No attendance logged for selected date.</td></tr>';
        return;
      }
      tbody.innerHTML = list.map(a => `
        <tr>
          <td><strong>${a.student_name}</strong></td>
          <td>${a.roll_number}</td>
          <td>${a.room_number ? 'Room ' + a.room_number : 'N/A'}</td>
          <td>${a.check_in_time || '-'}</td>
          <td>${getStatusBadge(a.status)}</td>
          <td>
            <button class="btn btn-outline" style="padding:0.35rem 0.65rem;" onclick="toggleAttendanceStatus(${a.student_id}, '${targetDate}', '${a.status === 'Present' ? 'Absent' : 'Present'}')">
              Toggle to ${a.status === 'Present' ? 'Absent' : 'Present'}
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchAttendance();

  if (datePicker) {
    datePicker.addEventListener('change', fetchAttendance);
  }
}

async function toggleAttendanceStatus(studentId, dateStr, newStatus) {
  try {
    const res = await fetchAPI('/api/attendance', {
      method: 'POST',
      body: {
        student_id: studentId,
        date: dateStr,
        status: newStatus,
        verification_method: 'Manual'
      }
    });
    loadWardenAttendance();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Notice Management
async function loadWardenNotices() {
  const tbody = document.getElementById('warden-notices-tbody');
  const addForm = document.getElementById('add-notice-form');
  if (!tbody) return;

  const fetchNotices = async () => {
    try {
      const list = await fetchAPI('/api/notices');
      tbody.innerHTML = list.map(n => `
        <tr>
          <td><strong>${n.title}</strong></td>
          <td>${n.description}</td>
          <td>${n.date}</td>
          <td>${getStatusBadge(n.is_active ? 'Normal' : 'Inactive')}</td>
          <td>
            <button class="btn btn-outline" style="padding:0.35rem 0.65rem;" onclick="toggleNoticeActive(${n.id}, ${!n.is_active})">
              ${n.is_active ? 'Deactivate' : 'Activate'}
            </button>
            <button class="btn btn-danger" style="padding:0.35rem 0.65rem;" onclick="deleteNotice(${n.id})">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchNotices();

  if (addForm) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/notices', {
          method: 'POST',
          body: {
            title: addForm.title.value,
            description: addForm.description.value,
            is_active: addForm.is_active.checked
          }
        });
        showAlert('Hostel Notice published successfully!', 'success', 'notice-modal-alert');
        addForm.reset();
        setTimeout(() => {
          closeModal('add-notice-modal');
          fetchNotices();
        }, 1000);
      } catch (err) {
        showAlert(err.message, 'danger', 'notice-modal-alert');
      }
    });
  }
}

async function toggleNoticeActive(id, newStatus) {
  try {
    await fetchAPI(`/api/notices/${id}`, {
      method: 'PUT',
      body: { is_active: newStatus }
    });
    loadWardenNotices();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteNotice(id) {
  if (!confirm('Are you sure you want to delete this notice?')) return;
  try {
    await fetchAPI(`/api/notices/${id}`, { method: 'DELETE' });
    loadWardenNotices();
  } catch (err) {
    alert(err.message);
  }
}

// Warden Resource Monitoring
async function loadWardenResources() {
  const tbody = document.getElementById('warden-resources-tbody');
  const addForm = document.getElementById('add-resource-form');
  if (!tbody) return;

  const fetchResources = async () => {
    try {
      const list = await fetchAPI('/api/resources');
      tbody.innerHTML = list.map(r => `
        <tr>
          <td><span class="badge badge-info">${r.resource_type}</span></td>
          <td><strong>${r.metric_name}</strong></td>
          <td><strong>${r.usage_value}</strong> ${r.unit}</td>
          <td>${getStatusBadge(r.status)}</td>
          <td>${r.remarks || '-'}</td>
          <td>${r.recorded_date}</td>
          <td>
            <button class="btn btn-outline" style="padding:0.35rem 0.65rem;" onclick="openUpdateResourceModal(${r.id}, '${r.metric_name.replace(/'/g, "\\'")}', ${r.usage_value}, '${r.status}')">
              <i class="fas fa-edit"></i> Edit
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  };

  await fetchResources();

  if (addForm) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await fetchAPI('/api/resources', {
          method: 'POST',
          body: {
            resource_type: addForm.resource_type.value,
            metric_name: addForm.metric_name.value,
            usage_value: parseFloat(addForm.usage_value.value),
            unit: addForm.unit.value,
            status: addForm.status.value,
            remarks: addForm.remarks.value
          }
        });
        showAlert('Resource metric log added!', 'success', 'resource-modal-alert');
        addForm.reset();
        setTimeout(() => {
          closeModal('add-resource-modal');
          fetchResources();
        }, 1000);
      } catch (err) {
        showAlert(err.message, 'danger', 'resource-modal-alert');
      }
    });
  }
}

function openUpdateResourceModal(id, metricName, value, status) {
  document.getElementById('res-id').value = id;
  document.getElementById('res-metric-name').innerText = metricName;
  document.getElementById('res-usage-value').value = value;
  document.getElementById('res-status-select').value = status;
  openModal('update-resource-modal');
}

async function submitResourceUpdate() {
  const id = document.getElementById('res-id').value;
  const usage_value = parseFloat(document.getElementById('res-usage-value').value);
  const status = document.getElementById('res-status-select').value;
  const remarks = document.getElementById('res-remarks-text').value;

  try {
    const res = await fetchAPI(`/api/resources/${id}`, {
      method: 'PUT',
      body: { usage_value, status, remarks }
    });
    alert(res.message);
    closeModal('update-resource-modal');
    loadWardenResources();
  } catch (err) {
    alert(err.message);
  }
}


// Auto-Initialize Components based on active page DOM elements
document.addEventListener('DOMContentLoaded', () => {
  initStudentLogin();
  initWardenLogin();
  loadStudentDashboard();
  loadStudentProfile();
  loadStudentRoomDetails();
  loadStudentFees();
  loadStudentComplaints();
  loadStudentLeave();
  loadStudentAttendance();
  loadWardenDashboard();
  loadWardenStudents();
  loadWardenRooms();
  loadWardenFees();
  loadWardenComplaints();
  loadWardenLeave();
  loadWardenAttendance();
  loadWardenNotices();
  loadWardenResources();
});
