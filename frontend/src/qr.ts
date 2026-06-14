import { authFetch } from './auth';
import { API_BASE } from './config';
import { escapeHTML, escapeAttr } from './ui';

export interface QrCode {
  id: number;
  name: string;
  link: string;
}

type ApiError = { detail?: string };

let currentEditId: number | null = null;

export async function fetchAll(): Promise<QrCode[]> {
  const r = await authFetch(`${API_BASE}/qr_code/`);
  if (!r.ok) throw await r.json();
  return r.json();
}

export async function createQr(name: string, link: string): Promise<QrCode> {
  const qs = new URLSearchParams({ name, link });
  const r  = await authFetch(`${API_BASE}/qr_code/?${qs}`, { method: 'POST' });
  if (!r.ok) throw await r.json();
  return r.json();
}

export async function updateQr(id: number, name: string, link: string): Promise<QrCode> {
  const qs = new URLSearchParams({ name, link });
  const r  = await authFetch(`${API_BASE}/qr_code/${id}?${qs}`, { method: 'PUT' });
  if (!r.ok) throw await r.json();
  return r.json();
}

export async function deleteQr(id: number): Promise<null> {
  const r = await authFetch(`${API_BASE}/qr_code/${id}`, { method: 'DELETE' });
  if (!r.ok) throw await r.json();
  return null;
}

export function qrImageUrl(id: number): string {
  return `${API_BASE}/qr_code/${id}/image`;
}

export async function loadList(): Promise<void> {
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
      const clean = q.link.replace(/^https?:\/\//, '');
      const display = escapeHTML(clean.length > 20 ? clean.slice(0, 20) + '...' : clean);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHTML(q.name)}</td>
        <td><a href="${escapeAttr(q.link)}" target="_blank">${display}</a></td>
        <td><img src="${qrImageUrl(q.id)}" alt="qr" width="64"></td>
        <td>
          <button class="btn-ghost"   data-edit="${q.id}">Edit</button>
          <button class="btn-danger" data-delete="${q.id}">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (err: unknown) {
    const msg = (err as ApiError)?.detail ?? String(err);
    tbody.innerHTML = `<tr><td colspan="4">Error: ${escapeHTML(msg)}</td></tr>`;
  }
}

function showPreview(id: string): void {
  const div = document.getElementById('preview');
  if (div) div.innerHTML = `<img src="${qrImageUrl(Number(id))}" alt="qr full">`;
}

function openEditView(id: number | null, name = '', link = ''): void {
  currentEditId = id;
  (document.getElementById('edit-name') as HTMLInputElement).value = name;
  (document.getElementById('edit-link') as HTMLInputElement).value = link;
  location.hash = '#edit' + (id != null ? `?id=${id}` : '');
}

async function handleEditSubmit(evt: Event): Promise<void> {
  evt.preventDefault();
  const name = (document.getElementById('edit-name') as HTMLInputElement).value.trim();
  const link = (document.getElementById('edit-link') as HTMLInputElement).value.trim();
  if (!name || !link) { alert('Both fields required'); return; }

  try {
    if (currentEditId != null) await updateQr(currentEditId, name, link);
    else                       await createQr(name, link);
    location.hash = '#dash';
    await loadList();
  } catch (err: unknown) {
    alert((err as ApiError)?.detail ?? JSON.stringify(err));
  }
}

export function initQrModule(): void {
  const tbody = document.getElementById('list');
  if (tbody) {
    tbody.addEventListener('click', e => {
      const target = e.target as HTMLElement;

      const editId = target.dataset.edit;
      if (editId) {
        const row = target.closest('tr')!;
        const nameCell = row.children[0] as HTMLElement;
        const linkCell = row.children[1] as HTMLElement;
        openEditView(
          Number(editId),
          nameCell.textContent ?? '',
          linkCell.querySelector('a')!.href,
        );
      }

      const delId = target.dataset.delete;
      if (delId) {
        if (!confirm('Are you sure you want to delete this QR code?')) return;
        deleteQr(Number(delId))
          .then(() => loadList())
          .catch((err: unknown) => alert((err as ApiError)?.detail ?? JSON.stringify(err)));
      }
    });

    tbody.addEventListener('mouseover', e => {
      const img = (e.target as HTMLElement).closest('tr')?.querySelector('img');
      if (img) showPreview(img.src.split('/').slice(-2, -1)[0]);
    });
  }

  document.getElementById('btn-new')
    ?.addEventListener('click', () => openEditView(null));

  document.getElementById('editForm')
    ?.addEventListener('submit', handleEditSubmit);

  window.addEventListener('auth', (ev: Event) => {
    const { type } = (ev as CustomEvent<{ type: string }>).detail;
    if (type === 'login' || type === 'refresh') loadList();
  });
}
