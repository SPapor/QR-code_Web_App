// frontend/js/qr.js
// Minimal QR-code CRUD client for the FastAPI backend.
//
// Assumes the following DOM elements exist (see index.html):
//   #list        <tbody> that will be filled with rows
//   #preview     <div>   where the selected QR image is shown
//   #btn-new     “New QR” button in dashboard
//   #editForm    shared form for both create and edit views
//   #edit-name   text input (name)
//   #edit-link   text input (link)
//
// Router will switch <section data-view> visibility; this module
// focuses only on talking to the API and wiring UI events.

import { authFetch } from './auth.js';

const API_BASE = 'http://192.168.1.135:8000';                      // override if backend served elsewhere
let currentEditId = null;                 // null ⇒ create, uuid ⇒ edit

/* ---------------------------------------------------------------- *\
    Low-level API helpers
\* ---------------------------------------------------------------- */

export async function fetchAll () {
  const r = await authFetch(`${API_BASE}/qr_code/`);
  if (!r.ok) throw await r.json();
  return r.json();                        // array of QrCode objects
}

export async function createQr (name, link) {
  const qs = new URLSearchParams({ name, link });
  const r  = await authFetch(`${API_BASE}/qr_code/?${qs}`, { method: 'POST' });
  if (!r.ok) throw await r.json();
  return r.json();
}

export async function updateQr (id, name, link) {
  const qs = new URLSearchParams({ name, link });
  const r  = await authFetch(`${API_BASE}/qr_code/${id}?${qs}`, { method: 'PUT' });
  if (!r.ok) throw await r.json();
  return r.json();                        // updated QrCode
}

export function qrImageUrl (id) {
  return `${API_BASE}/qr_code/${id}/image`;
}

/* ---------------------------------------------------------------- *\
    UI logic
\* ---------------------------------------------------------------- */

export async function loadList () {
  const tbody = document.getElementById('list');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="4">Loading…</td></tr>';
  try {
    const data = await fetchAll();
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4">No QR-codes yet</td></tr>';
      return;
    }
    tbody.innerHTML = '';
    data.forEach(q => {
      const tr  = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHTML(q.name)}</td>
        <td><a href="${escapeAttr(q.link)}" target="_blank">visit</a></td>
        <td><img src="${qrImageUrl(q.id)}" alt="qr" width="64"></td>
        <td><button data-edit="${q.id}">Edit</button></td>`;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4">Error: ${err?.detail || err}</td></tr>`;
  }
}

function showPreview (id) {
  const div = document.getElementById('preview');
  if (div) div.innerHTML = `<img src="${qrImageUrl(id)}" alt="qr full">`;
}

function openEditView (id, name = '', link = '') {
  currentEditId = id;
  document.getElementById('edit-name').value = name;
  document.getElementById('edit-link').value = link;
  location.hash = '#edit' + (id ? `?id=${id}` : '');
}

async function handleEditSubmit (evt) {
  evt.preventDefault();
  const name = document.getElementById('edit-name').value.trim();
  const link = document.getElementById('edit-link').value.trim();
  if (!name || !link) return alert('Both fields required');

  try {
    if (currentEditId) await updateQr(currentEditId, name, link);
    else               await createQr(name, link);
    location.hash = '#dash';
    await loadList();
  } catch (err) {
    alert(err?.detail || JSON.stringify(err));
  }
}

/* ---------------------------------------------------------------- *\
    Event wiring – called once at app start
\* ---------------------------------------------------------------- */

export function initQrModule () {
  // Dashboard list click
  const tbody = document.getElementById('list');
  if (tbody) {
    tbody.addEventListener('click', e => {
      const id = e.target?.dataset?.edit;
      if (!id) return;
      // pull existing row data so user can edit
      const row = e.target.closest('tr');
      const [nameCell, linkCell] = row.children;
      openEditView(id, nameCell.textContent, linkCell.querySelector('a').href);
    });
    // Preview on row hover
    tbody.addEventListener('mouseover', e => {
      const img = e.target.closest('tr')?.querySelector('img');
      if (img) showPreview(img.src.split('/').slice(-2, -1)[0]); // crude id extraction
    });
  }

  // “+ New QR” button
  const btnNew = document.getElementById('btn-new');
  if (btnNew) btnNew.addEventListener('click', () => openEditView(null));

  // Edit/Create form submit
  const form = document.getElementById('editForm');
  if (form) form.addEventListener('submit', handleEditSubmit);

  // When user logs in / refreshes, reload list automatically
  window.addEventListener('auth', ev => {
    if (ev.detail.type === 'login' || ev.detail.type === 'refresh') loadList();
  });
}

/* ---------------------------------------------------------------- *\
    Small util
\* ---------------------------------------------------------------- */

function escapeHTML (s) {
  return s.replace(/[&<>"']/g, m => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[m]));
}
function escapeAttr (s) { return escapeHTML(s).replace(/"/g, '&quot;'); }

// Initialize automatically
initQrModule();
