import { authFetch } from './auth';
import { API_BASE } from './config';
import { escapeHTML, escapeAttr, flash, apiErr } from './ui';

export interface QrCode {
  id: string;
  name: string;
  link: string;
}

let items: QrCode[] = [];
let currentEditId: string | null = null;

/* ── API ─────────────────────────────────────────────────────── */

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

export async function updateQr(id: string, name: string, link: string): Promise<QrCode> {
  const qs = new URLSearchParams({ name, link });
  const r  = await authFetch(`${API_BASE}/qr_code/${id}?${qs}`, { method: 'PUT' });
  if (!r.ok) throw await r.json();
  return r.json();
}

export async function deleteQr(id: string): Promise<null> {
  const r = await authFetch(`${API_BASE}/qr_code/${id}`, { method: 'DELETE' });
  if (!r.ok) throw await r.json();
  return null;
}

export function qrImageUrl(id: string): string {
  return `${API_BASE}/qr_code/${id}/image`;
}

/* ── Rendering ───────────────────────────────────────────────── */

const ICON_OPEN = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3h7v7"/><path d="M10 14 21 3"/><path d="M21 14v7H3V3h7"/></svg>`;
const ICON_EDIT = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4Z"/></svg>`;
const ICON_TRASH = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="m19 6-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>`;

function pluralCodes(n: number): string {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return 'код';
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return 'кода';
  return 'кодов';
}

function updateCount(n: number | null): void {
  const num  = document.getElementById('qr-count');
  const word = document.getElementById('qr-count-word');
  if (num)  num.textContent  = n == null ? '—' : String(n);
  if (word) word.textContent = pluralCodes(n ?? 0);
}

function displayLink(link: string): string {
  return link.replace(/^https?:\/\//, '').replace(/\/$/, '');
}

function skeletonHtml(): string {
  return Array.from({ length: 3 }, (_, i) => `
    <div class="row skeleton" style="--i:${i}">
      <div class="n">··</div>
      <span class="sk sk-box"></span>
      <div class="name"><span class="sk" style="width:${45 + i * 12}%"></span></div>
      <div class="link"><span class="sk" style="width:${60 - i * 10}%"></span></div>
      <div class="actions"><span class="sk sk-pill"></span></div>
    </div>`).join('');
}

function emptyHtml(): string {
  return `
    <div class="empty">
      <div class="icon"><svg width="52" height="52"><use href="#qr"/></svg></div>
      <h2>Пока пусто.</h2>
      <p>Создайте первый QR-код — это займёт меньше минуты.</p>
      <button class="btn-primary" type="button" data-new>+ Создать код</button>
    </div>`;
}

function rowHtml(q: QrCode, i: number): string {
  return `
    <div class="row" data-id="${escapeAttr(String(q.id))}" style="--i:${i}">
      <div class="n">${String(i + 1).padStart(2, '0')}</div>
      <button class="qr-thumb" type="button" data-open title="Открыть QR">
        <img src="${qrImageUrl(q.id)}" alt="" loading="lazy">
      </button>
      <div class="name">${escapeHTML(q.name)}</div>
      <div class="link"><a href="${escapeAttr(q.link)}" target="_blank" rel="noopener">${escapeHTML(displayLink(q.link))}</a></div>
      <div class="actions">
        <button class="btn-icon" type="button" data-open title="Открыть QR" aria-label="Открыть QR">${ICON_OPEN}</button>
        <button class="btn-icon" type="button" data-edit title="Редактировать" aria-label="Редактировать">${ICON_EDIT}</button>
        <button class="btn-icon danger" type="button" data-delete title="Удалить" aria-label="Удалить">${ICON_TRASH}</button>
      </div>
    </div>`;
}

export async function loadList(): Promise<void> {
  const list = document.getElementById('list');
  if (!list) return;

  list.innerHTML = skeletonHtml();
  updateCount(null);
  try {
    items = await fetchAll();
    updateCount(items.length);
    list.innerHTML = items.length === 0
      ? emptyHtml()
      : items.map(rowHtml).join('');
  } catch (err: unknown) {
    list.innerHTML = `<div class="list-state">Ошибка: ${escapeHTML(apiErr(err))}</div>`;
  }
}

/* ── QR modal ────────────────────────────────────────────────── */

function openModal(q: QrCode): void {
  const modal = document.getElementById('qr-modal');
  if (!modal) return;
  (document.getElementById('modal-img') as HTMLImageElement).src = qrImageUrl(q.id);
  document.getElementById('modal-name')!.textContent = q.name;

  const link = document.getElementById('modal-link') as HTMLAnchorElement;
  link.href = q.link;
  link.textContent = displayLink(q.link);

  const dl = document.getElementById('modal-download') as HTMLAnchorElement;
  dl.href = qrImageUrl(q.id);
  dl.download = (q.name.replace(/[^\wа-яё \-]+/gi, '').trim() || 'qr') + '.png';

  modal.hidden = false;
  document.body.classList.add('modal-open');
}

function closeModal(): void {
  const modal = document.getElementById('qr-modal');
  if (modal) modal.hidden = true;
  document.body.classList.remove('modal-open');
}

/* ── Edit view ───────────────────────────────────────────────── */

function openEditView(id: string | null, name = '', link = ''): void {
  currentEditId = id;
  const title = document.getElementById('edit-title');
  if (title) title.innerHTML = id != null ? 'Edit <em>code.</em>' : 'New <em>code.</em>';
  (document.getElementById('edit-name') as HTMLInputElement).value = name;
  (document.getElementById('edit-link') as HTMLInputElement).value = link;
  location.hash = '#edit' + (id != null ? `?id=${id}` : '');
}

async function handleEditSubmit(evt: Event): Promise<void> {
  evt.preventDefault();
  const name = (document.getElementById('edit-name') as HTMLInputElement).value.trim();
  const link = (document.getElementById('edit-link') as HTMLInputElement).value.trim();
  if (!name || !link) { flash('Заполните оба поля', 'error'); return; }

  const btn = (evt.target as HTMLFormElement).querySelector<HTMLButtonElement>('[type="submit"]');
  if (btn) btn.disabled = true;
  try {
    if (currentEditId != null) await updateQr(currentEditId, name, link);
    else                       await createQr(name, link);
    flash(currentEditId != null ? 'Сохранено' : 'Код создан');
    location.hash = '#dash';
    await loadList();
  } catch (err: unknown) {
    flash(apiErr(err), 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

/* ── Wiring ──────────────────────────────────────────────────── */

export function initQrModule(): void {
  const list = document.getElementById('list');

  list?.addEventListener('click', e => {
    const t = e.target as HTMLElement;

    if (t.closest('[data-new]')) { openEditView(null); return; }

    const row = t.closest<HTMLElement>('.row');
    if (!row?.dataset.id) return;
    const q = items.find(x => String(x.id) === row.dataset.id);
    if (!q) return;

    if (t.closest('[data-open]')) { openModal(q); return; }
    if (t.closest('[data-edit]')) { openEditView(q.id, q.name, q.link); return; }

    const del = t.closest<HTMLElement>('[data-delete]');
    if (del) {
      // two-step delete: first click arms the button, second confirms
      if (!del.classList.contains('arm')) {
        del.classList.add('arm');
        flash('Нажмите ещё раз, чтобы удалить', 'info', 2200);
        setTimeout(() => del.classList.remove('arm'), 2400);
        return;
      }
      deleteQr(String(q.id))
        .then(() => { flash('Код удалён'); return loadList(); })
        .catch((err: unknown) => flash(apiErr(err), 'error'));
    }
  });

  document.getElementById('btn-new')
    ?.addEventListener('click', () => openEditView(null));

  document.getElementById('editForm')
    ?.addEventListener('submit', handleEditSubmit);

  document.getElementById('qr-modal')?.addEventListener('click', e => {
    if ((e.target as HTMLElement).closest('[data-close]')) closeModal();
  });
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });

  window.addEventListener('auth', (ev: Event) => {
    const { type } = (ev as CustomEvent<{ type: string }>).detail;
    if (type === 'login' || type === 'refresh') loadList();
    if (type === 'logout') closeModal();
  });
}
