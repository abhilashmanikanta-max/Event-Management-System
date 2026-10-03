/**
 * EVENT MANAGEMENT SYSTEM - Complete Full-Stack Frontend Logic
 * College DBMS Project
 */

// Application State
const AppState = {
  currentPage: 'dashboard',
  currentTable: 'Event',
  currentReport: 'event-report',
  events: { page: 1, limit: 10, search: '', category: '', date: '', sortBy: 'Date', order: 'ASC' },
  dbTable: { page: 1, limit: 15, search: '', sortBy: '', order: 'ASC' },
  lookupData: {
    organizers: [],
    venues: [],
    categories: [],
    events: [],
    participants: []
  }
};

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initModals();
  initFormSubmissions();
  initGlobalListeners();
  
  // Initial check & load
  checkDbConnection();
  navigateTo('dashboard');
});

// ========================================================
// NAVIGATION & ROUTING
// ========================================================
function initNavigation() {
  document.querySelectorAll('.nav-item').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = link.getAttribute('data-page');
      if (page) navigateTo(page);
    });
  });

  // Mobile menu toggle
  const menuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

function navigateTo(pageId) {
  AppState.currentPage = pageId;

  // Update nav active classes
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.getAttribute('data-page') === pageId);
  });

  // Update section views
  document.querySelectorAll('.page-section').forEach(sec => {
    sec.classList.toggle('active', sec.id === `section-${pageId}`);
  });

  // Close mobile sidebar if open
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.remove('open');

  // Update page header
  const titleElem = document.getElementById('headerTitle');
  const descElem = document.getElementById('headerDesc');
  const titles = {
    'dashboard': { title: 'Dashboard Overview', desc: 'Real-time DBMS statistics, metrics and visualizations calculated from SQL' },
    'events': { title: 'Event Management', desc: 'Manage event schedules, venues, organizers and categories' },
    'organizers': { title: 'Organizers', desc: 'Manage event hosts and view hosted schedules' },
    'venues': { title: 'Venues & Locations', desc: 'Manage locations, seating capacities and bookings' },
    'categories': { title: 'Event Categories', desc: 'Manage classifications and event genres' },
    'participants': { title: 'Participants', desc: 'Manage registered attendees and registration records' },
    'registrations': { title: 'Event Registrations', desc: 'Manage bookings, attendee attendance and confirmation statuses' },
    'payments': { title: 'Payment Transactions', desc: 'Track 1:1 registration payments, billing status and receipts' },
    'reports': { title: 'SQL Aggregation Reports', desc: 'Multi-table join reports, revenue analysis and CSV export' },
    'database-tables': { title: 'Database Tables (Live SQL)', desc: 'Direct two-way inspection of the SQL tables, schema DDL and live records' },
    'er-diagram': { title: 'ER Diagram & Relational Schema', desc: 'Entity-relationship diagram, cardinalities, primary & foreign keys' },
    'sql-console': { title: 'SQL Query Console & Admin', desc: 'Execute real SQL queries, run preset DBMS queries and test query plans' }
  };

  if (titles[pageId]) {
    if (titleElem) titleElem.textContent = titles[pageId].title;
    if (descElem) descElem.textContent = titles[pageId].desc;
  }

  // Route Handler
  switch (pageId) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'events':
      loadEvents();
      break;
    case 'organizers':
      loadOrganizers();
      break;
    case 'venues':
      loadVenues();
      break;
    case 'categories':
      loadCategories();
      break;
    case 'participants':
      loadParticipants();
      break;
    case 'registrations':
      loadRegistrations();
      break;
    case 'payments':
      loadPayments();
      break;
    case 'reports':
      loadReports();
      break;
    case 'database-tables':
      loadDatabaseTables();
      break;
    case 'er-diagram':
      loadERDiagram();
      break;
    case 'sql-console':
      loadSqlConsole();
      break;
  }
}

// ========================================================
// DATABASE CONNECTION CHECK
// ========================================================
async function checkDbConnection() {
  try {
    const res = await API.getDbStatus();
    const badgeText = document.getElementById('dbBadgeText');
    const badgeDot = document.getElementById('dbBadgeDot');
    if (badgeText) {
      badgeText.textContent = `${res.engine} Connected`;
    }
  } catch (e) {
    console.error("DB Status check failed", e);
  }
}

// Pre-fetch lookup data for modal dropdowns
async function refreshLookupData() {
  try {
    const [orgs, venues, cats, evts, parts] = await Promise.all([
      API.getOrganizers(),
      API.getVenues(),
      API.getCategories(),
      API.getEvents({ limit: 100 }),
      API.getParticipants()
    ]);
    AppState.lookupData.organizers = orgs.data || [];
    AppState.lookupData.venues = venues.data || [];
    AppState.lookupData.categories = cats.data || [];
    AppState.lookupData.events = evts.data || [];
    AppState.lookupData.participants = parts.data || [];
  } catch (e) {
    console.error("Failed to load lookup data for dropdowns", e);
  }
}

// ========================================================
// 1. DASHBOARD PAGE
// ========================================================
async function loadDashboard() {
  try {
    const res = await API.getDashboardStats();
    const { counts, charts, upcoming_events } = res;

    // Update Stats Cards
    document.getElementById('statEvents').textContent = counts.events;
    document.getElementById('statOrganizers').textContent = counts.organizers;
    document.getElementById('statVenues').textContent = counts.venues;
    document.getElementById('statCategories').textContent = counts.categories;
    document.getElementById('statParticipants').textContent = counts.participants;
    document.getElementById('statRegistrations').textContent = counts.registrations;
    document.getElementById('statPayments').textContent = `$${counts.total_revenue.toLocaleString()}`;

    // Render Charts
    AppCharts.renderDashboardCharts(charts);

    // Upcoming Events Table
    const tbody = document.getElementById('dashboardUpcomingTable');
    if (tbody) {
      if (!upcoming_events || upcoming_events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No upcoming events scheduled.</td></tr>`;
      } else {
        tbody.innerHTML = upcoming_events.map(evt => `
          <tr>
            <td><strong>${escapeHtml(evt.Event_Name)}</strong></td>
            <td><span class="badge badge-primary">${escapeHtml(evt.Category_Name)}</span></td>
            <td>${escapeHtml(evt.Date)} at ${escapeHtml(evt.Time)}</td>
            <td>${escapeHtml(evt.Venue_Name)}</td>
            <td>${escapeHtml(evt.Organizer_Name)}</td>
          </tr>
        `).join('');
      }
    }
  } catch (e) {
    console.error("Dashboard load failed", e);
  }
}

// ========================================================
// 2. EVENTS PAGE
// ========================================================
async function loadEvents() {
  await refreshLookupData();
  populateCategoryFilter();

  const tbody = document.getElementById('eventsTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center" style="padding: 2rem;">Loading SQL records...</td></tr>`;

  try {
    const params = {
      page: AppState.events.page,
      limit: AppState.events.limit,
      search: AppState.events.search,
      category_id: AppState.events.category,
      date: AppState.events.date,
      sort_by: AppState.events.sortBy,
      order: AppState.events.order
    };
    const res = await API.getEvents(params);
    const events = res.data;
    const pagination = res.pagination;

    if (!events || events.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><h4>No Events Found</h4><p>No event records match your filter criteria.</p><button class="btn btn-primary" onclick="openAddEventModal()">+ Create First Event</button></div></td></tr>`;
      renderPagination('eventsPagination', pagination, (p) => { AppState.events.page = p; loadEvents(); });
      return;
    }

    tbody.innerHTML = events.map(evt => `
      <tr>
        <td><strong>#${evt.Event_ID}</strong></td>
        <td>
          <a href="#" style="color: var(--primary); font-weight: 600; text-decoration: none;" onclick="viewEventDetails(${evt.Event_ID}); return false;">
            ${escapeHtml(evt.Event_Name)}
          </a>
        </td>
        <td>${escapeHtml(evt.Date)}</td>
        <td>${escapeHtml(evt.Time)}</td>
        <td>${escapeHtml(evt.Organizer_Name)}</td>
        <td>${escapeHtml(evt.Venue_Name)} <span class="badge badge-secondary">${evt.Capacity} cap</span></td>
        <td><span class="badge badge-primary">${escapeHtml(evt.Category_Name)}</span></td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="viewEventDetails(${evt.Event_ID})" title="View Details">👁️</button>
            <button class="btn btn-sm btn-secondary" onclick="openEditEventModal(${evt.Event_ID})" title="Edit Event">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteEvent(${evt.Event_ID}, '${escapeJs(evt.Event_Name)}')" title="Delete Event">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');

    renderPagination('eventsPagination', pagination, (p) => {
      AppState.events.page = p;
      loadEvents();
    });
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-danger text-center">Failed to load events from SQL: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function populateCategoryFilter() {
  const sel = document.getElementById('eventsCategoryFilter');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = `<option value="">All Categories</option>` + AppState.lookupData.categories.map(c => `
    <option value="${c.Category_ID}" ${currentVal == c.Category_ID ? 'selected' : ''}>${escapeHtml(c.Category_Name)}</option>
  `).join('');
}

// Add/Edit Event Modal
function openAddEventModal() {
  populateEventFormDropdowns();
  document.getElementById('eventModalTitle').textContent = 'Create New Event';
  document.getElementById('eventId').value = '';
  document.getElementById('eventName').value = '';
  document.getElementById('eventDate').value = new Date().toISOString().split('T')[0];
  document.getElementById('eventTime').value = '10:00 AM';
  openModal('eventModal');
}

async function openEditEventModal(id) {
  try {
    const res = await API.getEvent(id);
    const evt = res.data;
    populateEventFormDropdowns();

    document.getElementById('eventModalTitle').textContent = `Edit Event #${evt.Event_ID}`;
    document.getElementById('eventId').value = evt.Event_ID;
    document.getElementById('eventName').value = evt.Event_Name;
    document.getElementById('eventDate').value = evt.Date;
    document.getElementById('eventTime').value = evt.Time;
    document.getElementById('eventOrganizer').value = evt.Organizer_ID;
    document.getElementById('eventVenue').value = evt.Venue_ID;
    document.getElementById('eventCategory').value = evt.Category_ID;

    openModal('eventModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function populateEventFormDropdowns() {
  const orgSel = document.getElementById('eventOrganizer');
  const venSel = document.getElementById('eventVenue');
  const catSel = document.getElementById('eventCategory');

  if (orgSel) {
    orgSel.innerHTML = `<option value="">-- Select Organizer (FK) --</option>` + AppState.lookupData.organizers.map(o => `
      <option value="${o.Organizer_ID}">${escapeHtml(o.Name)} (${escapeHtml(o.Email)})</option>
    `).join('');
  }
  if (venSel) {
    venSel.innerHTML = `<option value="">-- Select Venue (FK) --</option>` + AppState.lookupData.venues.map(v => `
      <option value="${v.Venue_ID}">${escapeHtml(v.Venue_Name)} (Capacity: ${v.Capacity})</option>
    `).join('');
  }
  if (catSel) {
    catSel.innerHTML = `<option value="">-- Select Category (FK) --</option>` + AppState.lookupData.categories.map(c => `
      <option value="${c.Category_ID}">${escapeHtml(c.Category_Name)}</option>
    `).join('');
  }
}

async function viewEventDetails(id) {
  try {
    const res = await API.getEvent(id);
    const evt = res.data;

    let content = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; background: #f8fafc; padding: 1.25rem; border-radius: var(--radius-md);">
        <div><strong>Event Name:</strong> ${escapeHtml(evt.Event_Name)}</div>
        <div><strong>Category:</strong> <span class="badge badge-primary">${escapeHtml(evt.Category_Name)}</span></div>
        <div><strong>Date & Time:</strong> ${escapeHtml(evt.Date)} at ${escapeHtml(evt.Time)}</div>
        <div><strong>Venue:</strong> ${escapeHtml(evt.Venue_Name)} (Max: ${evt.Venue_Capacity})</div>
        <div><strong>Location:</strong> ${escapeHtml(evt.Venue_Location)}</div>
        <div><strong>Organizer:</strong> ${escapeHtml(evt.Organizer_Name)} (${escapeHtml(evt.Organizer_Email)})</div>
      </div>

      <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">Registered Attendees (${evt.Total_Registrations})</h4>
    `;

    if (!evt.Registrations || evt.Registrations.length === 0) {
      content += `<p class="text-muted">No attendees registered yet for this event.</p>`;
    } else {
      content += `
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Reg ID</th>
                <th>Participant</th>
                <th>Email</th>
                <th>Reg Date</th>
                <th>Status</th>
                <th>Payment</th>
              </tr>
            </thead>
            <tbody>
              ${evt.Registrations.map(r => `
                <tr>
                  <td>#${r.Registration_ID}</td>
                  <td><strong>${escapeHtml(r.Participant_Name)}</strong></td>
                  <td>${escapeHtml(r.Participant_Email)}</td>
                  <td>${escapeHtml(r.Registration_Date)}</td>
                  <td><span class="badge ${r.Registration_Status === 'Confirmed' ? 'badge-success' : 'badge-warning'}">${escapeHtml(r.Registration_Status)}</span></td>
                  <td><span class="badge ${r.Payment_Status === 'Completed' ? 'badge-success' : 'badge-danger'}">$${r.Paid_Amount || 0} (${escapeHtml(r.Payment_Status || 'Unpaid')})</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    document.getElementById('detailsModalTitle').textContent = `Event #${evt.Event_ID}: ${evt.Event_Name}`;
    document.getElementById('detailsModalBody').innerHTML = content;
    openModal('detailsModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeleteEvent(id, name) {
  openConfirmModal(`Delete Event #${id}`, `Are you sure you want to delete event "${name}"? If attendees are registered, DBMS foreign key constraints will prevent deletion.`, async () => {
    try {
      const res = await API.deleteEvent(id);
      API.showToast('Success', res.message, 'success');
      loadEvents();
    } catch (e) {
      // Toast already shown by API client
    }
  });
}

// ========================================================
// 3. ORGANIZERS PAGE
// ========================================================
async function loadOrganizers() {
  const search = document.getElementById('searchOrganizers')?.value || '';
  const tbody = document.getElementById('organizersTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center">Loading SQL records...</td></tr>`;

  try {
    const res = await API.getOrganizers(search);
    const orgs = res.data;

    if (!orgs || orgs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No Organizers found.</td></tr>`;
      return;
    }

    tbody.innerHTML = orgs.map(o => `
      <tr>
        <td><strong>#${o.Organizer_ID}</strong></td>
        <td><strong>${escapeHtml(o.Name)}</strong></td>
        <td>${escapeHtml(o.Email)}</td>
        <td>${escapeHtml(o.Phone)}</td>
        <td><span class="badge badge-primary">${o.Total_Events} Events</span></td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="viewOrganizerEvents(${o.Organizer_ID})" title="View Events">📅</button>
            <button class="btn btn-sm btn-secondary" onclick="openEditOrganizerModal(${o.Organizer_ID})" title="Edit">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteOrganizer(${o.Organizer_ID}, '${escapeJs(o.Name)}')" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function openAddOrganizerModal() {
  document.getElementById('orgModalTitle').textContent = 'Add Organizer';
  document.getElementById('orgId').value = '';
  document.getElementById('orgName').value = '';
  document.getElementById('orgEmail').value = '';
  document.getElementById('orgPhone').value = '';
  openModal('organizerModal');
}

async function openEditOrganizerModal(id) {
  try {
    const res = await API.getOrganizer(id);
    const org = res.data;
    document.getElementById('orgModalTitle').textContent = `Edit Organizer #${org.Organizer_ID}`;
    document.getElementById('orgId').value = org.Organizer_ID;
    document.getElementById('orgName').value = org.Name;
    document.getElementById('orgEmail').value = org.Email;
    document.getElementById('orgPhone').value = org.Phone;
    openModal('organizerModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

async function viewOrganizerEvents(id) {
  try {
    const res = await API.getOrganizer(id);
    const org = res.data;
    let html = `<h4>Events Hosted by ${escapeHtml(org.Name)} (${org.events.length})</h4><br>`;
    if (org.events.length === 0) {
      html += `<p class="text-muted">No events currently scheduled by this organizer.</p>`;
    } else {
      html += `
        <div class="table-responsive">
          <table class="data-table">
            <thead><tr><th>Event ID</th><th>Event Name</th><th>Date</th><th>Venue</th><th>Category</th></tr></thead>
            <tbody>
              ${org.events.map(e => `
                <tr>
                  <td>#${e.Event_ID}</td>
                  <td><strong>${escapeHtml(e.Event_Name)}</strong></td>
                  <td>${escapeHtml(e.Date)} ${escapeHtml(e.Time)}</td>
                  <td>${escapeHtml(e.Venue_Name)}</td>
                  <td><span class="badge badge-primary">${escapeHtml(e.Category_Name)}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
    document.getElementById('detailsModalTitle').textContent = `Organizer: ${org.Name}`;
    document.getElementById('detailsModalBody').innerHTML = html;
    openModal('detailsModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeleteOrganizer(id, name) {
  openConfirmModal(`Delete Organizer #${id}`, `Are you sure you want to delete "${name}"? If events are linked to this organizer, DBMS Foreign Key constraints will restrict deletion.`, async () => {
    try {
      const res = await API.deleteOrganizer(id);
      API.showToast('Success', res.message, 'success');
      loadOrganizers();
    } catch (e) {}
  });
}

// ========================================================
// 4. VENUES PAGE
// ========================================================
async function loadVenues() {
  const search = document.getElementById('searchVenues')?.value || '';
  const tbody = document.getElementById('venuesTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center">Loading SQL records...</td></tr>`;

  try {
    const res = await API.getVenues(search);
    const venues = res.data;

    if (!venues || venues.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No Venues found.</td></tr>`;
      return;
    }

    tbody.innerHTML = venues.map(v => `
      <tr>
        <td><strong>#${v.Venue_ID}</strong></td>
        <td><strong>${escapeHtml(v.Venue_Name)}</strong></td>
        <td>${escapeHtml(v.Location)}</td>
        <td><span class="badge badge-success">${v.Capacity.toLocaleString()} seats</span></td>
        <td><span class="badge badge-primary">${v.Total_Events} Events</span></td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="viewVenueEvents(${v.Venue_ID})" title="View Events">📅</button>
            <button class="btn btn-sm btn-secondary" onclick="openEditVenueModal(${v.Venue_ID})" title="Edit">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteVenue(${v.Venue_ID}, '${escapeJs(v.Venue_Name)}')" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function openAddVenueModal() {
  document.getElementById('venueModalTitle').textContent = 'Add Venue';
  document.getElementById('venueId').value = '';
  document.getElementById('venueName').value = '';
  document.getElementById('venueLocation').value = '';
  document.getElementById('venueCapacity').value = '500';
  openModal('venueModal');
}

async function openEditVenueModal(id) {
  try {
    const res = await API.getVenue(id);
    const venue = res.data;
    document.getElementById('venueModalTitle').textContent = `Edit Venue #${venue.Venue_ID}`;
    document.getElementById('venueId').value = venue.Venue_ID;
    document.getElementById('venueName').value = venue.Venue_Name;
    document.getElementById('venueLocation').value = venue.Location;
    document.getElementById('venueCapacity').value = venue.Capacity;
    openModal('venueModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

async function viewVenueEvents(id) {
  try {
    const res = await API.getVenue(id);
    const venue = res.data;
    let html = `<h4>Events Conducted at ${escapeHtml(venue.Venue_Name)} (Capacity: ${venue.Capacity})</h4><br>`;
    if (venue.events.length === 0) {
      html += `<p class="text-muted">No events currently scheduled at this venue.</p>`;
    } else {
      html += `
        <div class="table-responsive">
          <table class="data-table">
            <thead><tr><th>Event ID</th><th>Event Name</th><th>Date</th><th>Time</th><th>Organizer</th><th>Category</th></tr></thead>
            <tbody>
              ${venue.events.map(e => `
                <tr>
                  <td>#${e.Event_ID}</td>
                  <td><strong>${escapeHtml(e.Event_Name)}</strong></td>
                  <td>${escapeHtml(e.Date)}</td>
                  <td>${escapeHtml(e.Time)}</td>
                  <td>${escapeHtml(e.Organizer_Name)}</td>
                  <td><span class="badge badge-primary">${escapeHtml(e.Category_Name)}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
    document.getElementById('detailsModalTitle').textContent = `Venue: ${venue.Venue_Name}`;
    document.getElementById('detailsModalBody').innerHTML = html;
    openModal('detailsModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeleteVenue(id, name) {
  openConfirmModal(`Delete Venue #${id}`, `Are you sure you want to delete venue "${name}"? If events are booked at this venue, foreign key constraints will block deletion.`, async () => {
    try {
      const res = await API.deleteVenue(id);
      API.showToast('Success', res.message, 'success');
      loadVenues();
    } catch (e) {}
  });
}

// ========================================================
// 5. CATEGORIES PAGE
// ========================================================
async function loadCategories() {
  const search = document.getElementById('searchCategories')?.value || '';
  const tbody = document.getElementById('categoriesTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="5" class="text-center">Loading SQL records...</td></tr>`;

  try {
    const res = await API.getCategories(search);
    const categories = res.data;

    if (!categories || categories.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No Categories found.</td></tr>`;
      return;
    }

    tbody.innerHTML = categories.map(c => `
      <tr>
        <td><strong>#${c.Category_ID}</strong></td>
        <td><strong>${escapeHtml(c.Category_Name)}</strong></td>
        <td>${escapeHtml(c.Description || 'N/A')}</td>
        <td><span class="badge badge-primary">${c.Total_Events} Events</span></td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="openEditCategoryModal(${c.Category_ID})" title="Edit">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteCategory(${c.Category_ID}, '${escapeJs(c.Category_Name)}')" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function openAddCategoryModal() {
  document.getElementById('catModalTitle').textContent = 'Add Category';
  document.getElementById('catId').value = '';
  document.getElementById('catName').value = '';
  document.getElementById('catDesc').value = '';
  openModal('categoryModal');
}

async function openEditCategoryModal(id) {
  try {
    const res = await API.getCategory(id);
    const cat = res.data;
    document.getElementById('catModalTitle').textContent = `Edit Category #${cat.Category_ID}`;
    document.getElementById('catId').value = cat.Category_ID;
    document.getElementById('catName').value = cat.Category_Name;
    document.getElementById('catDesc').value = cat.Description || '';
    openModal('categoryModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeleteCategory(id, name) {
  openConfirmModal(`Delete Category #${id}`, `Are you sure you want to delete category "${name}"? Foreign key protection prevents deleting categories that have events.`, async () => {
    try {
      const res = await API.deleteCategory(id);
      API.showToast('Success', res.message, 'success');
      loadCategories();
    } catch (e) {}
  });
}

// ========================================================
// 6. PARTICIPANTS PAGE
// ========================================================
async function loadParticipants() {
  const search = document.getElementById('searchParticipants')?.value || '';
  const tbody = document.getElementById('participantsTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center">Loading SQL records...</td></tr>`;

  try {
    const res = await API.getParticipants(search);
    const parts = res.data;

    if (!parts || parts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No Participants found.</td></tr>`;
      return;
    }

    tbody.innerHTML = parts.map(p => `
      <tr>
        <td><strong>#${p.Participant_ID}</strong></td>
        <td><strong>${escapeHtml(p.Name)}</strong></td>
        <td>${escapeHtml(p.Email)}</td>
        <td>${escapeHtml(p.Phone)}</td>
        <td><span class="badge badge-primary">${p.Total_Registrations} Registrations</span></td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="viewParticipantRegistrations(${p.Participant_ID})" title="View Registrations">📋</button>
            <button class="btn btn-sm btn-secondary" onclick="openEditParticipantModal(${p.Participant_ID})" title="Edit">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteParticipant(${p.Participant_ID}, '${escapeJs(p.Name)}')" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function openAddParticipantModal() {
  document.getElementById('partModalTitle').textContent = 'Add Participant';
  document.getElementById('partId').value = '';
  document.getElementById('partName').value = '';
  document.getElementById('partEmail').value = '';
  document.getElementById('partPhone').value = '';
  openModal('participantModal');
}

async function openEditParticipantModal(id) {
  try {
    const res = await API.getParticipant(id);
    const part = res.data;
    document.getElementById('partModalTitle').textContent = `Edit Participant #${part.Participant_ID}`;
    document.getElementById('partId').value = part.Participant_ID;
    document.getElementById('partName').value = part.Name;
    document.getElementById('partEmail').value = part.Email;
    document.getElementById('partPhone').value = part.Phone;
    openModal('participantModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

async function viewParticipantRegistrations(id) {
  try {
    const res = await API.getParticipant(id);
    const part = res.data;
    let html = `<h4>Registered Events for ${escapeHtml(part.Name)} (${part.Email})</h4><br>`;
    if (part.registrations.length === 0) {
      html += `<p class="text-muted">No event registrations found for this participant.</p>`;
    } else {
      html += `
        <div class="table-responsive">
          <table class="data-table">
            <thead><tr><th>Reg ID</th><th>Event</th><th>Date</th><th>Venue</th><th>Status</th><th>Payment</th></tr></thead>
            <tbody>
              ${part.registrations.map(r => `
                <tr>
                  <td>#${r.Registration_ID}</td>
                  <td><strong>${escapeHtml(r.Event_Name)}</strong></td>
                  <td>${escapeHtml(r.Event_Date)}</td>
                  <td>${escapeHtml(r.Venue_Name)}</td>
                  <td><span class="badge ${r.Registration_Status === 'Confirmed' ? 'badge-success' : 'badge-warning'}">${escapeHtml(r.Registration_Status)}</span></td>
                  <td><span class="badge ${r.Payment_Status === 'Completed' ? 'badge-success' : 'badge-danger'}">$${r.Amount || 0} (${escapeHtml(r.Payment_Status || 'Unpaid')})</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
    document.getElementById('detailsModalTitle').textContent = `Participant: ${part.Name}`;
    document.getElementById('detailsModalBody').innerHTML = html;
    openModal('detailsModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeleteParticipant(id, name) {
  openConfirmModal(`Delete Participant #${id}`, `Are you sure you want to delete participant "${name}"? If event registrations exist, DBMS FK constraints will block deletion.`, async () => {
    try {
      const res = await API.deleteParticipant(id);
      API.showToast('Success', res.message, 'success');
      loadParticipants();
    } catch (e) {}
  });
}

// ========================================================
// 7. REGISTRATIONS PAGE
// ========================================================
async function loadRegistrations() {
  await refreshLookupData();
  populateRegistrationEventFilter();

  const search = document.getElementById('searchRegistrations')?.value || '';
  const eventId = document.getElementById('filterRegEvent')?.value || '';
  const status = document.getElementById('filterRegStatus')?.value || '';
  const tbody = document.getElementById('registrationsTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center">Loading SQL records...</td></tr>`;

  try {
    const res = await API.getRegistrations({ search, event_id: eventId, status });
    const regs = res.data;

    if (!regs || regs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No registrations found.</td></tr>`;
      return;
    }

    tbody.innerHTML = regs.map(r => `
      <tr>
        <td><strong>#${r.Registration_ID}</strong></td>
        <td>
          <strong>${escapeHtml(r.Participant_Name)}</strong><br>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(r.Participant_Email)}</span>
        </td>
        <td>
          <strong>${escapeHtml(r.Event_Name)}</strong><br>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(r.Event_Date)}</span>
        </td>
        <td>${escapeHtml(r.Registration_Date)}</td>
        <td>
          <span class="badge ${r.Status === 'Confirmed' ? 'badge-success' : (r.Status === 'Cancelled' ? 'badge-danger' : 'badge-warning')}">
            ${escapeHtml(r.Status)}
          </span>
        </td>
        <td>
          <span class="badge ${r.Payment_Status === 'Completed' ? 'badge-success' : 'badge-warning'}">
            $${r.Payment_Amount || 0} (${escapeHtml(r.Payment_Status)})
          </span>
        </td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            ${r.Status !== 'Cancelled' ? `
              <button class="btn btn-sm btn-secondary" onclick="updateRegStatus(${r.Registration_ID}, 'Cancelled')" title="Cancel Registration">❌</button>
            ` : `
              <button class="btn btn-sm btn-secondary" onclick="updateRegStatus(${r.Registration_ID}, 'Confirmed')" title="Re-confirm">✅</button>
            `}
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteRegistration(${r.Registration_ID})" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function populateRegistrationEventFilter() {
  const sel = document.getElementById('filterRegEvent');
  if (!sel) return;
  const current = sel.value;
  sel.innerHTML = `<option value="">All Events</option>` + AppState.lookupData.events.map(e => `
    <option value="${e.Event_ID}" ${current == e.Event_ID ? 'selected' : ''}>${escapeHtml(e.Event_Name)}</option>
  `).join('');
}

function openAddRegistrationModal() {
  const pSel = document.getElementById('regParticipant');
  const eSel = document.getElementById('regEvent');

  if (pSel) {
    pSel.innerHTML = `<option value="">-- Select Participant (FK) --</option>` + AppState.lookupData.participants.map(p => `
      <option value="${p.Participant_ID}">${escapeHtml(p.Name)} (${escapeHtml(p.Email)})</option>
    `).join('');
  }
  if (eSel) {
    eSel.innerHTML = `<option value="">-- Select Event (FK) --</option>` + AppState.lookupData.events.map(e => `
      <option value="${e.Event_ID}">${escapeHtml(e.Event_Name)} (${escapeHtml(e.Date)})</option>
    `).join('');
  }

  document.getElementById('regDate').value = new Date().toISOString().split('T')[0];
  document.getElementById('regStatus').value = 'Confirmed';
  document.getElementById('regAmount').value = '100.00';
  openModal('registrationModal');
}

async function updateRegStatus(id, newStatus) {
  try {
    const res = await API.updateRegistration(id, { Status: newStatus });
    API.showToast('Status Updated', res.message, 'success');
    loadRegistrations();
  } catch (e) {}
}

function confirmDeleteRegistration(id) {
  openConfirmModal(`Delete Registration #${id}`, `Are you sure you want to delete Registration #${id}? Note: If a payment record is attached, payment must be deleted first (FK constraint).`, async () => {
    try {
      const res = await API.deleteRegistration(id);
      API.showToast('Success', res.message, 'success');
      loadRegistrations();
    } catch (e) {}
  });
}

// ========================================================
// 8. PAYMENTS PAGE
// ========================================================
async function loadPayments() {
  const search = document.getElementById('searchPayments')?.value || '';
  const status = document.getElementById('filterPaymentStatus')?.value || '';
  const tbody = document.getElementById('paymentsTableBody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center">Loading SQL records...</td></tr>`;

  try {
    // Summary counts
    const summaryRes = await API.getPaymentSummary();
    const stats = summaryRes.data;
    document.getElementById('payTotalAmount').textContent = `$${parseFloat(stats.total_amount).toLocaleString()}`;
    document.getElementById('payCompletedCount').textContent = `${stats.completed_count} (${stats.completed_amount.toLocaleString()}$)`;
    document.getElementById('payPendingCount').textContent = stats.pending_count;
    document.getElementById('payFailedCount').textContent = stats.failed_count;

    // Payments list
    const res = await API.getPayments({ search, status });
    const payments = res.data;

    if (!payments || payments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No payment records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = payments.map(p => `
      <tr>
        <td><strong>#${p.Payment_ID}</strong></td>
        <td><span class="badge badge-primary">Reg #${p.Registration_ID}</span></td>
        <td>
          <strong>${escapeHtml(p.Participant_Name)}</strong><br>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(p.Participant_Email)}</span>
        </td>
        <td>${escapeHtml(p.Event_Name)}</td>
        <td><strong style="color: var(--primary);">$${parseFloat(p.Amount).toFixed(2)}</strong></td>
        <td>${escapeHtml(p.Payment_Date)}</td>
        <td>
          <span class="badge ${p.Payment_Status === 'Completed' ? 'badge-success' : (p.Payment_Status === 'Failed' ? 'badge-danger' : 'badge-warning')}">
            ${escapeHtml(p.Payment_Status)}
          </span>
        </td>
        <td>
          <div style="display: flex; gap: 0.35rem;">
            <button class="btn btn-sm btn-secondary" onclick="openEditPaymentModal(${p.Payment_ID})" title="Edit">✏️</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeletePayment(${p.Payment_ID})" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-danger text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

async function openAddPaymentModal() {
  // Populate registration dropdown with unpaid registrations
  try {
    const regsRes = await API.getRegistrations();
    const rSel = document.getElementById('payRegistrationId');
    if (rSel) {
      rSel.innerHTML = `<option value="">-- Select Registration (1:1 FK) --</option>` + regsRes.data.map(r => `
        <option value="${r.Registration_ID}">Reg #${r.Registration_ID} - ${escapeHtml(r.Participant_Name)} (${escapeHtml(r.Event_Name)})</option>
      `).join('');
    }

    document.getElementById('paymentModalTitle').textContent = 'Record Payment';
    document.getElementById('payId').value = '';
    document.getElementById('payAmount').value = '100.00';
    document.getElementById('payDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('payStatus').value = 'Completed';
    document.getElementById('payRegGroup').style.display = 'block';

    openModal('paymentModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

async function openEditPaymentModal(id) {
  try {
    const res = await API.getPayment(id);
    const pay = res.data;

    document.getElementById('paymentModalTitle').textContent = `Edit Payment #${pay.Payment_ID}`;
    document.getElementById('payId').value = pay.Payment_ID;
    document.getElementById('payAmount').value = pay.Amount;
    document.getElementById('payDate').value = pay.Payment_Date;
    document.getElementById('payStatus').value = pay.Payment_Status;
    document.getElementById('payRegGroup').style.display = 'none';

    openModal('paymentModal');
  } catch (e) {
    API.showToast('Error', e.message, 'error');
  }
}

function confirmDeletePayment(id) {
  openConfirmModal(`Delete Payment #${id}`, `Are you sure you want to delete Payment record #${id}?`, async () => {
    try {
      const res = await API.deletePayment(id);
      API.showToast('Success', res.message, 'success');
      loadPayments();
    } catch (e) {}
  });
}

// ========================================================
// 9. REPORTS PAGE
// ========================================================
async function loadReports() {
  const type = document.getElementById('reportTypeSelect')?.value || AppState.currentReport;
  AppState.currentReport = type;

  const thead = document.getElementById('reportTableHead');
  const tbody = document.getElementById('reportTableBody');
  const titleElem = document.getElementById('reportActiveTitle');
  const rowCountElem = document.getElementById('reportRowCount');

  if (tbody) tbody.innerHTML = `<tr><td colspan="10" class="text-center" style="padding: 2rem;">Executing SQL aggregation report...</td></tr>`;

  try {
    const res = await API.getReport(type);
    if (titleElem) titleElem.textContent = res.title;
    if (rowCountElem) rowCountElem.textContent = `${res.total_rows} Records Returned`;

    if (!res.data || res.data.length === 0) {
      if (thead) thead.innerHTML = '';
      if (tbody) tbody.innerHTML = `<tr><td colspan="10" class="empty-state">No report records found.</td></tr>`;
      return;
    }

    // Render Table Headers
    if (thead) {
      thead.innerHTML = `<tr>` + res.columns.map(col => `<th>${escapeHtml(col.replace(/_/g, ' '))}</th>`).join('') + `</tr>`;
    }

    // Render Table Rows
    if (tbody) {
      tbody.innerHTML = res.data.map(row => `
        <tr>
          ${res.columns.map(col => {
            const val = row[col];
            if (typeof val === 'number' && col.toLowerCase().includes('revenue') || col.toLowerCase().includes('fees') || col.toLowerCase().includes('amount')) {
              return `<td><strong>$${parseFloat(val).toFixed(2)}</strong></td>`;
            }
            if (col.toLowerCase().includes('status')) {
              const badgeClass = val === 'Confirmed' || val === 'Completed' ? 'badge-success' : 'badge-warning';
              return `<td><span class="badge ${badgeClass}">${escapeHtml(val || 'N/A')}</span></td>`;
            }
            return `<td>${escapeHtml(val !== null && val !== undefined ? String(val) : 'N/A')}</td>`;
          }).join('')}
        </tr>
      `).join('');
    }
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="10" class="text-danger text-center">Report Error: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function exportCurrentReport() {
  API.getReport(AppState.currentReport, 'csv');
}

function printCurrentReport() {
  window.print();
}

// ========================================================
// 10. DATABASE TABLES PAGE (VERY IMPORTANT)
// ========================================================
async function loadDatabaseTables() {
  try {
    // 1. Fetch tables summary
    const res = await API.getDatabaseTables();
    const tables = res.tables;

    // Render Tab Buttons
    const tabsContainer = document.getElementById('dbTableTabs');
    if (tabsContainer) {
      tabsContainer.innerHTML = tables.map(t => `
        <button class="db-tab-btn ${t.table_name === AppState.currentTable ? 'active' : ''}" onclick="switchDatabaseTable('${t.table_name}')">
          📁 ${t.table_name} <span class="nav-badge">${t.total_records}</span>
        </button>
      `).join('');
    }

    // Load active table details
    await fetchActiveTableData();
  } catch (e) {
    console.error("Failed to load database tables", e);
  }
}

async function switchDatabaseTable(tableName) {
  AppState.currentTable = tableName;
  AppState.dbTable.page = 1;
  AppState.dbTable.search = '';
  document.getElementById('searchDbTable').value = '';

  // Update tabs active state
  document.querySelectorAll('.db-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.includes(tableName));
  });

  await fetchActiveTableData();
}

async function fetchActiveTableData() {
  const tableTitle = document.getElementById('activeDbTableName');
  const countBadge = document.getElementById('activeDbTableRowCount');
  const columnsPreview = document.getElementById('dbSchemaColumnsPreview');
  const thead = document.getElementById('dbTableThead');
  const tbody = document.getElementById('dbTableTbody');

  if (tbody) tbody.innerHTML = `<tr><td colspan="15" class="text-center" style="padding: 2rem;">Fetching SQL table '${AppState.currentTable}' records...</td></tr>`;

  try {
    const res = await API.getTableDetails(AppState.currentTable, {
      page: AppState.dbTable.page,
      limit: AppState.dbTable.limit,
      search: AppState.dbTable.search,
      sort_by: AppState.dbTable.sortBy,
      order: AppState.dbTable.order
    });

    const { metadata, data, pagination } = res;

    if (tableTitle) tableTitle.textContent = `${metadata.table_name} Table`;
    if (countBadge) countBadge.textContent = `${pagination.total} Rows in SQL Database`;

    // Render Schema Columns with PK & FK Badges
    if (columnsPreview) {
      columnsPreview.innerHTML = metadata.columns.map(c => `
        <div class="column-pill ${c.pk ? 'pk' : ''}">
          ${c.pk ? '🔑 PK' : ''} ${escapeHtml(c.name)}: <span style="color: var(--text-muted);">${escapeHtml(c.type)}</span>
          ${c.notnull ? '<span style="color: var(--danger);">*</span>' : ''}
        </div>
      `).join('') + (metadata.foreign_keys ? metadata.foreign_keys.map(fk => `
        <div class="column-pill fk">
          🔗 FK: ${fk.from} &rarr; ${fk.table}(${fk.to})
        </div>
      `).join('') : '');
    }

    // Render Table Headers
    if (thead) {
      thead.innerHTML = `<tr>` + metadata.columns.map(c => `
        <th class="sortable" onclick="sortDbTable('${c.name}')">
          ${escapeHtml(c.name)} ${c.pk ? '🔑' : ''} ${AppState.dbTable.sortBy === c.name ? (AppState.dbTable.order === 'ASC' ? '▲' : '▼') : ''}
        </th>
      `).join('') + `</tr>`;
    }

    // Render Data Rows
    if (tbody) {
      if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${metadata.columns.length}" class="empty-state">No records found in SQL table '${metadata.table_name}'.</td></tr>`;
      } else {
        tbody.innerHTML = data.map(row => `
          <tr>
            ${metadata.columns.map(c => {
              const val = row[c.name];
              if (c.pk) return `<td><strong>#${val}</strong></td>`;
              return `<td>${escapeHtml(val !== null && val !== undefined ? String(val) : 'NULL')}</td>`;
            }).join('')}
          </tr>
        `).join('');
      }
    }

    // Pagination
    renderPagination('dbTablePagination', pagination, (p) => {
      AppState.dbTable.page = p;
      fetchActiveTableData();
    });
  } catch (e) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="15" class="text-danger text-center">Failed to load table: ${escapeHtml(e.message)}</td></tr>`;
  }
}

function sortDbTable(columnName) {
  if (AppState.dbTable.sortBy === columnName) {
    AppState.dbTable.order = AppState.dbTable.order === 'ASC' ? 'DESC' : 'ASC';
  } else {
    AppState.dbTable.sortBy = columnName;
    AppState.dbTable.order = 'ASC';
  }
  fetchActiveTableData();
}

function refreshDbTable() {
  API.showToast('Refreshing', `Fetching latest records directly from SQL database...`, 'info');
  fetchActiveTableData();
}

// ========================================================
// 11. ER DIAGRAM & SCHEMA PAGE
// ========================================================
function loadERDiagram() {
  // Highlights active schema info
  const inspector = document.getElementById('erInspectorDetails');
  if (inspector) {
    selectEREntity('Event');
  }
}

const ENTITY_DETAILS = {
  'Organizer': {
    table: 'Organizer',
    desc: 'Stores event organizers, agencies, or hosting companies.',
    attributes: [
      { name: 'Organizer_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Organizer Identifier' },
      { name: 'Name', type: 'VARCHAR(100)', key: '', desc: 'Organizer Name' },
      { name: 'Email', type: 'VARCHAR(100)', key: 'UNIQUE', desc: 'Contact Email' },
      { name: 'Phone', type: 'VARCHAR(20)', key: '', desc: 'Contact Phone Number' }
    ],
    relationships: ['1:N with Event (One organizer can host many events)']
  },
  'Venue': {
    table: 'Venue',
    desc: 'Stores halls, stadiums, auditoriums, and convention centers.',
    attributes: [
      { name: 'Venue_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Venue Identifier' },
      { name: 'Venue_Name', type: 'VARCHAR(100)', key: '', desc: 'Venue / Hall Name' },
      { name: 'Location', type: 'VARCHAR(200)', key: '', desc: 'Address / Campus Location' },
      { name: 'Capacity', type: 'INTEGER', key: 'CHECK (>0)', desc: 'Maximum Allowed Occupancy' }
    ],
    relationships: ['1:N with Event (One venue can host multiple events over time)']
  },
  'Category': {
    table: 'Category',
    desc: 'Event genres (Technology, Business, Arts, Sports, Science).',
    attributes: [
      { name: 'Category_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Category Identifier' },
      { name: 'Category_Name', type: 'VARCHAR(100)', key: 'UNIQUE', desc: 'Genre Name' },
      { name: 'Description', type: 'TEXT', key: '', desc: 'Detailed Genre Description' }
    ],
    relationships: ['1:N with Event (One category classifies many events)']
  },
  'Participant': {
    table: 'Participant',
    desc: 'Students, attendees, or delegates registered in system.',
    attributes: [
      { name: 'Participant_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Participant Identifier' },
      { name: 'Name', type: 'VARCHAR(100)', key: '', desc: 'Attendee Full Name' },
      { name: 'Email', type: 'VARCHAR(100)', key: 'UNIQUE', desc: 'Attendee Email Address' },
      { name: 'Phone', type: 'VARCHAR(20)', key: '', desc: 'Mobile / Phone Number' }
    ],
    relationships: ['1:N with Registration (One participant can register for many events)']
  },
  'Event': {
    table: 'Event',
    desc: 'The central entity representing scheduled events.',
    attributes: [
      { name: 'Event_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Event Identifier' },
      { name: 'Event_Name', type: 'VARCHAR(150)', key: '', desc: 'Title of the Event' },
      { name: 'Date', type: 'DATE', key: '', desc: 'Event Scheduled Date' },
      { name: 'Time', type: 'VARCHAR(10)', key: '', desc: 'Start Time (e.g. 10:00 AM)' },
      { name: 'Organizer_ID', type: 'INTEGER', key: 'FK', desc: 'References Organizer(Organizer_ID)' },
      { name: 'Venue_ID', type: 'INTEGER', key: 'FK', desc: 'References Venue(Venue_ID)' },
      { name: 'Category_ID', type: 'INTEGER', key: 'FK', desc: 'References Category(Category_ID)' }
    ],
    relationships: [
      'N:1 with Organizer (Each event belongs to one organizer)',
      'N:1 with Venue (Each event is held at one venue)',
      'N:1 with Category (Each event belongs to one category)',
      '1:N with Registration (One event has many attendee registrations)'
    ]
  },
  'Registration': {
    table: 'Registration',
    desc: 'Associative entity managing attendee bookings for events.',
    attributes: [
      { name: 'Registration_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Booking Identifier' },
      { name: 'Participant_ID', type: 'INTEGER', key: 'FK', desc: 'References Participant(Participant_ID)' },
      { name: 'Event_ID', type: 'INTEGER', key: 'FK', desc: 'References Event(Event_ID)' },
      { name: 'Registration_Date', type: 'DATE', key: '', desc: 'Date booking occurred' },
      { name: 'Status', type: 'VARCHAR(20)', key: 'CHECK', desc: 'Confirmed, Pending, Cancelled' }
    ],
    relationships: [
      'N:1 with Participant',
      'N:1 with Event',
      '1:1 with Payment (Each registration has exactly one payment record)'
    ]
  },
  'Payment': {
    table: 'Payment',
    desc: 'Financial transaction details for event registration.',
    attributes: [
      { name: 'Payment_ID', type: 'INTEGER', key: 'PK', desc: 'Unique Payment Identifier' },
      { name: 'Registration_ID', type: 'INTEGER', key: 'FK UNIQUE', desc: 'References Registration(Registration_ID) - 1:1' },
      { name: 'Amount', type: 'DECIMAL(10,2)', key: 'CHECK (>=0)', desc: 'Transaction Amount' },
      { name: 'Payment_Date', type: 'DATE', key: '', desc: 'Timestamp of transaction' },
      { name: 'Payment_Status', type: 'VARCHAR(20)', key: 'CHECK', desc: 'Completed, Pending, Failed' }
    ],
    relationships: ['1:1 with Registration (Enforced via UNIQUE constraint on Registration_ID)']
  }
};

function selectEREntity(entityName) {
  document.querySelectorAll('.er-entity-card').forEach(c => {
    c.classList.toggle('selected', c.getAttribute('data-entity') === entityName);
  });

  const info = ENTITY_DETAILS[entityName];
  if (!info) return;

  const inspector = document.getElementById('erInspectorDetails');
  if (inspector) {
    inspector.innerHTML = `
      <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.25rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
          <h4 style="font-size: 1.15rem; color: var(--primary);">Entity: ${info.table}</h4>
          <span class="badge badge-primary">${info.attributes.length} Attributes</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">${info.desc}</p>
        
        <h5 style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem;">Attributes & Constraints:</h5>
        <div class="table-responsive" style="margin-bottom: 1rem;">
          <table class="data-table">
            <thead><tr><th>Attribute</th><th>Data Type</th><th>Key / Constraint</th><th>Description</th></tr></thead>
            <tbody>
              ${info.attributes.map(a => `
                <tr>
                  <td><strong>${escapeHtml(a.name)}</strong></td>
                  <td><code>${escapeHtml(a.type)}</code></td>
                  <td><span class="badge ${a.key.includes('PK') ? 'badge-warning' : (a.key.includes('FK') ? 'badge-primary' : 'badge-secondary')}">${escapeHtml(a.key || 'None')}</span></td>
                  <td>${escapeHtml(a.desc)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <h5 style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem;">Cardinality & Relationships:</h5>
        <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--text-sub);">
          ${info.relationships.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
        </ul>
      </div>
    `;
  }
}

// ========================================================
// 12. SQL QUERY CONSOLE PAGE
// ========================================================
async function loadSqlConsole() {
  try {
    const res = await API.getPresets();
    const presetsContainer = document.getElementById('sqlPresetsContainer');
    if (presetsContainer) {
      presetsContainer.innerHTML = res.presets.map(p => `
        <div class="preset-query-btn" onclick="selectPresetQuery('${p.id}')">
          <h5>${escapeHtml(p.title)}</h5>
          <p>${escapeHtml(p.description)}</p>
        </div>
      `).join('');
      window._sqlPresets = res.presets;
    }
  } catch (e) {
    console.error("Failed to load SQL presets", e);
  }
}

function selectPresetQuery(id) {
  if (!window._sqlPresets) return;
  const preset = window._sqlPresets.find(p => p.id === id);
  if (preset) {
    const textarea = document.getElementById('sqlQueryInput');
    if (textarea) textarea.value = preset.sql;
  }
}

async function runSqlQuery() {
  const query = document.getElementById('sqlQueryInput')?.value.trim();
  if (!query) {
    API.showToast('Validation Error', 'Please enter a SQL query to execute.', 'warning');
    return;
  }

  const resultMeta = document.getElementById('sqlResultMeta');
  const thead = document.getElementById('sqlResultThead');
  const tbody = document.getElementById('sqlResultTbody');

  if (resultMeta) resultMeta.textContent = 'Executing query on SQL engine...';
  if (tbody) tbody.innerHTML = `<tr><td colspan="15" class="text-center" style="padding: 2rem;">Running query...</td></tr>`;

  try {
    const res = await API.executeQuery(query);
    if (resultMeta) {
      resultMeta.innerHTML = `<span style="color: var(--success); font-weight: 700;">✓ Query Executed in ${res.duration_ms} ms</span> | Returned <strong>${res.row_count}</strong> rows`;
    }

    if (!res.data || res.data.length === 0) {
      if (thead) thead.innerHTML = '';
      if (tbody) tbody.innerHTML = `<tr><td colspan="15" class="empty-state">Query returned 0 rows.</td></tr>`;
      return;
    }

    // Headers
    if (thead) {
      thead.innerHTML = `<tr>` + res.columns.map(c => `<th>${escapeHtml(c)}</th>`).join('') + `</tr>`;
    }

    // Rows
    if (tbody) {
      tbody.innerHTML = res.data.map(row => `
        <tr>
          ${res.columns.map(c => `<td>${escapeHtml(row[c] !== null && row[c] !== undefined ? String(row[c]) : 'NULL')}</td>`).join('')}
        </tr>
      `).join('');
    }
  } catch (e) {
    if (resultMeta) resultMeta.innerHTML = `<span style="color: var(--danger); font-weight: 700;">✗ Execution Error</span>`;
    if (tbody) tbody.innerHTML = `<tr><td colspan="15" class="text-danger text-center" style="padding: 1.5rem;">${escapeHtml(e.message)}</td></tr>`;
  }
}

function clearSqlConsole() {
  const textarea = document.getElementById('sqlQueryInput');
  if (textarea) textarea.value = '';
  const thead = document.getElementById('sqlResultThead');
  const tbody = document.getElementById('sqlResultTbody');
  const resultMeta = document.getElementById('sqlResultMeta');
  if (thead) thead.innerHTML = '';
  if (tbody) tbody.innerHTML = '';
  if (resultMeta) resultMeta.textContent = 'Results will appear below.';
}

// ========================================================
// GLOBAL MODAL & FORM HANDLERS
// ========================================================
function initModals() {
  // Modal Close buttons
  document.querySelectorAll('.modal-close-btn, .btn-modal-cancel').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal-overlay');
      if (modal) closeModal(modal.id);
    });
  });

  // Close when clicking overlay backdrop
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

let _confirmCallback = null;
function openConfirmModal(title, message, callback) {
  document.getElementById('confirmModalTitle').textContent = title;
  document.getElementById('confirmModalMessage').textContent = message;
  _confirmCallback = callback;
  openModal('confirmModal');
}

document.getElementById('confirmModalOkBtn')?.addEventListener('click', () => {
  closeModal('confirmModal');
  if (_confirmCallback) {
    _confirmCallback();
    _confirmCallback = null;
  }
});

function initFormSubmissions() {
  // 1. Event Form
  document.getElementById('eventForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('eventId').value;
    const payload = {
      Event_Name: document.getElementById('eventName').value.trim(),
      Date: document.getElementById('eventDate').value,
      Time: document.getElementById('eventTime').value.trim(),
      Organizer_ID: parseInt(document.getElementById('eventOrganizer').value),
      Venue_ID: parseInt(document.getElementById('eventVenue').value),
      Category_ID: parseInt(document.getElementById('eventCategory').value)
    };

    try {
      if (id) {
        const res = await API.updateEvent(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createEvent(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('eventModal');
      loadEvents();
    } catch (err) {}
  });

  // 2. Organizer Form
  document.getElementById('organizerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('orgId').value;
    const payload = {
      Name: document.getElementById('orgName').value.trim(),
      Email: document.getElementById('orgEmail').value.trim(),
      Phone: document.getElementById('orgPhone').value.trim()
    };

    try {
      if (id) {
        const res = await API.updateOrganizer(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createOrganizer(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('organizerModal');
      loadOrganizers();
    } catch (err) {}
  });

  // 3. Venue Form
  document.getElementById('venueForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('venueId').value;
    const payload = {
      Venue_Name: document.getElementById('venueName').value.trim(),
      Location: document.getElementById('venueLocation').value.trim(),
      Capacity: parseInt(document.getElementById('venueCapacity').value)
    };

    try {
      if (id) {
        const res = await API.updateVenue(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createVenue(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('venueModal');
      loadVenues();
    } catch (err) {}
  });

  // 4. Category Form
  document.getElementById('categoryForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('catId').value;
    const payload = {
      Category_Name: document.getElementById('catName').value.trim(),
      Description: document.getElementById('catDesc').value.trim()
    };

    try {
      if (id) {
        const res = await API.updateCategory(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createCategory(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('categoryModal');
      loadCategories();
    } catch (err) {}
  });

  // 5. Participant Form
  document.getElementById('participantForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('partId').value;
    const payload = {
      Name: document.getElementById('partName').value.trim(),
      Email: document.getElementById('partEmail').value.trim(),
      Phone: document.getElementById('partPhone').value.trim()
    };

    try {
      if (id) {
        const res = await API.updateParticipant(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createParticipant(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('participantModal');
      loadParticipants();
    } catch (err) {}
  });

  // 6. Registration Form
  document.getElementById('registrationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      Participant_ID: parseInt(document.getElementById('regParticipant').value),
      Event_ID: parseInt(document.getElementById('regEvent').value),
      Registration_Date: document.getElementById('regDate').value,
      Status: document.getElementById('regStatus').value,
      Amount: parseFloat(document.getElementById('regAmount').value || 0),
      Payment_Status: 'Completed'
    };

    try {
      const res = await API.createRegistration(payload);
      API.showToast('Success', res.message, 'success');
      closeModal('registrationModal');
      loadRegistrations();
    } catch (err) {}
  });

  // 7. Payment Form
  document.getElementById('paymentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('payId').value;
    const payload = {
      Registration_ID: parseInt(document.getElementById('payRegistrationId')?.value),
      Amount: parseFloat(document.getElementById('payAmount').value),
      Payment_Date: document.getElementById('payDate').value,
      Payment_Status: document.getElementById('payStatus').value
    };

    try {
      if (id) {
        const res = await API.updatePayment(id, payload);
        API.showToast('Success', res.message, 'success');
      } else {
        const res = await API.createPayment(payload);
        API.showToast('Success', res.message, 'success');
      }
      closeModal('paymentModal');
      loadPayments();
    } catch (err) {}
  });
}

function initGlobalListeners() {
  // Events Filters
  document.getElementById('eventsSearch')?.addEventListener('input', debounce(() => {
    AppState.events.search = document.getElementById('eventsSearch').value.trim();
    AppState.events.page = 1;
    loadEvents();
  }, 300));

  document.getElementById('eventsCategoryFilter')?.addEventListener('change', () => {
    AppState.events.category = document.getElementById('eventsCategoryFilter').value;
    AppState.events.page = 1;
    loadEvents();
  });

  document.getElementById('eventsDateFilter')?.addEventListener('change', () => {
    AppState.events.date = document.getElementById('eventsDateFilter').value;
    AppState.events.page = 1;
    loadEvents();
  });

  // Search in other tables
  document.getElementById('searchOrganizers')?.addEventListener('input', debounce(loadOrganizers, 300));
  document.getElementById('searchVenues')?.addEventListener('input', debounce(loadVenues, 300));
  document.getElementById('searchCategories')?.addEventListener('input', debounce(loadCategories, 300));
  document.getElementById('searchParticipants')?.addEventListener('input', debounce(loadParticipants, 300));
  document.getElementById('searchRegistrations')?.addEventListener('input', debounce(loadRegistrations, 300));
  document.getElementById('filterRegEvent')?.addEventListener('change', loadRegistrations);
  document.getElementById('filterRegStatus')?.addEventListener('change', loadRegistrations);
  document.getElementById('searchPayments')?.addEventListener('input', debounce(loadPayments, 300));
  document.getElementById('filterPaymentStatus')?.addEventListener('change', loadPayments);
  document.getElementById('reportTypeSelect')?.addEventListener('change', loadReports);

  // Database Table Search
  document.getElementById('searchDbTable')?.addEventListener('input', debounce(() => {
    AppState.dbTable.search = document.getElementById('searchDbTable').value.trim();
    AppState.dbTable.page = 1;
    fetchActiveTableData();
  }, 300));
}

// Reset Database Confirmation
function promptResetDatabase() {
  openConfirmModal(
    'Reset Database to Factory State',
    'Are you sure you want to reset the entire SQL database? This will drop and recreate all 7 tables and restore clean seed records.',
    async () => {
      try {
        const res = await API.resetDatabase();
        API.showToast('Database Reset', res.message, 'success');
        navigateTo(AppState.currentPage);
      } catch (e) {}
    }
  );
}

// Helper: Pagination Component
function renderPagination(containerId, pagination, onPageClick) {
  const container = document.getElementById(containerId);
  if (!container || !pagination) return;

  const { total, page, total_pages, limit } = pagination;
  if (total === 0) {
    container.innerHTML = '';
    return;
  }

  let html = `
    <span>Showing ${(page - 1) * limit + 1} to ${Math.min(page * limit, total)} of ${total} entries</span>
    <div class="pagination-controls">
      <button class="page-btn" ${page <= 1 ? 'disabled' : ''} onclick="(${onPageClick})(${page - 1})">&laquo; Prev</button>
  `;

  for (let i = 1; i <= total_pages; i++) {
    if (i === 1 || i === total_pages || (i >= page - 2 && i <= page + 2)) {
      html += `<button class="page-btn ${i === page ? 'active' : ''}" onclick="(${onPageClick})(${i})">${i}</button>`;
    } else if (i === page - 3 || i === page + 3) {
      html += `<span style="padding: 0 4px;">...</span>`;
    }
  }

  html += `
      <button class="page-btn" ${page >= total_pages ? 'disabled' : ''} onclick="(${onPageClick})(${page + 1})">Next &raquo;</button>
    </div>
  `;
  container.innerHTML = html;
}

// Utility: Debounce
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Utility: XSS Escaping
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeJs(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}
