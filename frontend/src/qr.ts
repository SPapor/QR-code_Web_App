import { authFetch } from './auth';
import { API_BASE } from './config';
import { dateLocale, pluralCodes, pluralScans, scansShort, t } from './i18n';
import { escapeHTML, escapeAttr, flash, apiErr } from './ui';

export interface QrCode {
  id: string;
  name: string;
  link: string;
  scan_count: number;
  last_scan_at: number | null;
}

let items: QrCode[] = [];
let currentEditId: string | null = null;

type ViewMode = 'grid' | 'list';
const VIEW_KEY = 'view-mode';

function viewMode(): ViewMode {
  return localStorage.getItem(VIEW_KEY) === 'list' ? 'list' : 'grid';
}

function setViewMode(mode: ViewMode): void {
  localStorage.setItem(VIEW_KEY, mode);
  syncViewToggle();
  renderList();
}

function syncViewToggle(): void {
  document.querySelectorAll<HTMLButtonElement>('[data-viewmode]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.viewmode === viewMode());
  });
}

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

/** The public redirect URL encoded in the QR image. */
export function qrPublicUrl(id: string): string {
  return `${location.origin}/qr_code/${id}`;
}

async function copyText(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
    flash(t('flashCopied'));
  } catch {
    flash(t('flashCopyFail'), 'error');
  }
}

/* ── Rendering ───────────────────────────────────────────────── */

const ICON_OPEN = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3h7v7"/><path d="M10 14 21 3"/><path d="M21 14v7H3V3h7"/></svg>`;
const ICON_EDIT = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4Z"/></svg>`;
const ICON_TRASH = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="m19 6-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>`;
const ICON_COPY = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;

function relTime(ts: number): string {
  const diff = Math.floor(Date.now() / 1000) - ts;
  if (diff < 60) return t('justNow');
  if (diff < 3600) return t('minAgo', { n: Math.floor(diff / 60) });
  if (diff < 86400) return t('hourAgo', { n: Math.floor(diff / 3600) });
  return new Date(ts * 1000).toLocaleDateString(dateLocale(), { day: 'numeric', month: 'short', year: 'numeric' });
}

function scansSummary(q: QrCode): string {
  const scans = q.scan_count ?? 0;
  let text = `${scans} ${pluralScans(scans)}`;
  if (scans > 0 && q.last_scan_at) text += ` · ${relTime(q.last_scan_at)}`;
  return text;
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
  if (viewMode() === 'grid') {
    return Array.from({ length: 3 }, (_, i) => `
      <div class="card skeleton" style="--i:${i}">
        <span class="sk sk-card"></span>
        <div class="card-body">
          <span class="sk" style="width:${55 + i * 10}%"></span>
        </div>
      </div>`).join('');
  }
  return Array.from({ length: 3 }, (_, i) => `
    <div class="row skeleton" style="--i:${i}">
      <div class="n">··</div>
      <span class="sk sk-box"></span>
      <div class="name"><span class="sk" style="width:${45 + i * 12}%"></span></div>
      <div class="link"><span class="sk" style="width:${60 - i * 10}%"></span></div>
      <div class="scans"></div>
      <div class="actions"><span class="sk sk-pill"></span></div>
    </div>`).join('');
}

function emptyHtml(): string {
  return `
    <div class="empty">
      <div class="icon"><svg width="52" height="52"><use href="#qr"/></svg></div>
      <h2>${t('emptyTitle')}</h2>
      <p>${t('emptyText')}</p>
      <button class="btn-primary" type="button" data-new>${t('emptyCreate')}</button>
    </div>`;
}

function rowHtml(q: QrCode, i: number): string {
  const scans = q.scan_count ?? 0;
  return `
    <div class="row" data-id="${escapeAttr(String(q.id))}" style="--i:${i}">
      <div class="n">${String(i + 1).padStart(2, '0')}</div>
      <button class="qr-thumb" type="button" data-open title="${escapeAttr(t('openQr'))}">
        <img src="${qrImageUrl(q.id)}" alt="" loading="lazy">
      </button>
      <div class="name">${escapeHTML(q.name)}</div>
      <div class="link"><a href="${escapeAttr(q.link)}" target="_blank" rel="noopener">${escapeHTML(displayLink(q.link))}</a></div>
      <div class="scans" title="${escapeAttr(scansSummary(q))}">${scans}&thinsp;${scansShort(scans)}</div>
      <div class="actions">
        <button class="btn-icon" type="button" data-copy title="${escapeAttr(t('copyQrLink'))}" aria-label="${escapeAttr(t('copyQrLink'))}">${ICON_COPY}</button>
        <button class="btn-icon" type="button" data-open title="${escapeAttr(t('openQr'))}" aria-label="${escapeAttr(t('openQr'))}">${ICON_OPEN}</button>
        <button class="btn-icon" type="button" data-edit title="${escapeAttr(t('editAction'))}" aria-label="${escapeAttr(t('editAction'))}">${ICON_EDIT}</button>
        <button class="btn-icon danger" type="button" data-delete title="${escapeAttr(t('deleteAction'))}" aria-label="${escapeAttr(t('deleteAction'))}">${ICON_TRASH}</button>
      </div>
    </div>`;
}

function cardHtml(q: QrCode, i: number): string {
  const scans = q.scan_count ?? 0;
  return `
    <div class="card" data-id="${escapeAttr(String(q.id))}" style="--i:${i}">
      <button class="card-thumb" type="button" data-open title="${escapeAttr(t('openQr'))}">
        <img src="${qrImageUrl(q.id)}" alt="" loading="lazy">
      </button>
      <div class="card-body">
        <div class="name">${escapeHTML(q.name)}</div>
        <a class="link" href="${escapeAttr(q.link)}" target="_blank" rel="noopener">${escapeHTML(displayLink(q.link))}</a>
      </div>
      <div class="card-foot">
        <span class="scans-chip" title="${escapeAttr(scansSummary(q))}">${scans}&thinsp;${scansShort(scans)}</span>
        <div class="actions">
          <button class="btn-icon" type="button" data-copy title="${escapeAttr(t('copyQrLink'))}" aria-label="${escapeAttr(t('copyQrLink'))}">${ICON_COPY}</button>
          <button class="btn-icon" type="button" data-edit title="${escapeAttr(t('editAction'))}" aria-label="${escapeAttr(t('editAction'))}">${ICON_EDIT}</button>
          <button class="btn-icon danger" type="button" data-delete title="${escapeAttr(t('deleteAction'))}" aria-label="${escapeAttr(t('deleteAction'))}">${ICON_TRASH}</button>
        </div>
      </div>
    </div>`;
}

function searchQuery(): string {
  const input = document.getElementById('search') as HTMLInputElement | null;
  return input?.value.trim().toLowerCase() ?? '';
}

function renderList(): void {
  const list = document.getElementById('list');
  const toolbar = document.getElementById('toolbar');
  if (!list) return;

  const grid = viewMode() === 'grid';
  list.classList.toggle('grid', grid);
  if (toolbar) toolbar.hidden = items.length < 2;
  if (items.length === 0) {
    list.classList.remove('grid');
    list.innerHTML = emptyHtml();
    return;
  }
  const q = searchQuery();
  const visible = q
    ? items.filter(x => x.name.toLowerCase().includes(q) || x.link.toLowerCase().includes(q))
    : items;
  if (visible.length === 0) {
    list.classList.remove('grid');
    list.innerHTML = `<div class="list-state">${t('nothingFound', { q: escapeHTML(q) })}</div>`;
    return;
  }
  list.innerHTML = visible.map(grid ? cardHtml : rowHtml).join('');
}

export async function loadList(): Promise<void> {
  const list = document.getElementById('list');
  if (!list) return;

  list.classList.toggle('grid', viewMode() === 'grid');
  list.innerHTML = skeletonHtml();
  updateCount(null);
  try {
    items = await fetchAll();
    updateCount(items.length);
    renderList();
  } catch (err: unknown) {
    list.classList.remove('grid');
    list.innerHTML = `<div class="list-state">${t('listError', { msg: escapeHTML(apiErr(err)) })}</div>`;
  }
}

/* ── QR modal ────────────────────────────────────────────────── */

let modalQr: QrCode | null = null;

interface ScanStats {
  days: { date: string; count: number }[];
}

function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString(dateLocale(), { day: 'numeric', month: 'short' }).replace('.', '');
}

/** Inline bar chart: scans per day. One series, so no legend; peak gets the only direct label. */
function chartHtml(days: ScanStats['days']): string {
  const W = 300, H = 56, BASE = 46, TOP = 12;
  const slot = W / days.length;
  const barW = Math.max(2, slot - 2);
  const max = Math.max(...days.map(d => d.count));
  const peakIdx = days.findIndex(d => d.count === max);

  const bars = days.map((d, i) => {
    const x = i * slot + (slot - barW) / 2;
    const h = d.count === 0 ? 0 : Math.max(3, (d.count / max) * (BASE - TOP));
    const bar = d.count === 0
      ? `<rect class="stub" x="${x}" y="${BASE - 1.5}" width="${barW}" height="1.5"/>`
      : `<rect class="bar" x="${x}" y="${BASE - h}" width="${barW}" height="${h}" rx="1.5"/>`;
    const label = i === peakIdx && max > 0
      ? `<text class="peak" x="${x + barW / 2}" y="${BASE - h - 3}" text-anchor="middle">${d.count}</text>`
      : '';
    // full-height hit area so the tooltip works on short bars too
    return `<g><title>${shortDate(d.date)} · ${d.count}</title>
      <rect class="hit" x="${i * slot}" y="0" width="${slot}" height="${BASE}"/>${bar}${label}</g>`;
  }).join('');

  return `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${escapeAttr(t('chartAria', { n: days.length }))}">
      <line class="axis" x1="0" y1="${BASE}" x2="${W}" y2="${BASE}"/>
      ${bars}
      <text class="tick" x="0" y="${H}">${shortDate(days[0].date)}</text>
      <text class="tick" x="${W}" y="${H}" text-anchor="end">${shortDate(days[days.length - 1].date)}</text>
    </svg>`;
}

async function loadModalChart(q: QrCode): Promise<void> {
  const box = document.getElementById('modal-chart');
  if (!box) return;
  box.hidden = true;
  box.innerHTML = '';
  try {
    const r = await authFetch(`${API_BASE}/qr_code/${q.id}/stats?days=30`);
    if (!r.ok) return;
    const stats: ScanStats = await r.json();
    if (modalQr?.id !== q.id) return; // modal changed while loading
    if (!stats.days.some(d => d.count > 0)) return; // nothing to plot yet
    box.innerHTML = chartHtml(stats.days);
    box.hidden = false;
  } catch {
    /* the chart is optional decoration — fail silently */
  }
}

function openModal(q: QrCode): void {
  const modal = document.getElementById('qr-modal');
  if (!modal) return;
  modalQr = q;
  (document.getElementById('modal-img') as HTMLImageElement).src = qrImageUrl(q.id);
  document.getElementById('modal-name')!.textContent = q.name;

  const link = document.getElementById('modal-link') as HTMLAnchorElement;
  link.href = q.link;
  link.textContent = displayLink(q.link);

  const scansBox = document.getElementById('modal-scans');
  if (scansBox) scansBox.textContent = scansSummary(q);

  const fileBase = q.name.replace(/[^\wа-яё \-]+/gi, '').trim() || 'qr';
  const dl = document.getElementById('modal-download') as HTMLAnchorElement;
  // hi-res png (~1200px) so the code survives print
  dl.href = `${qrImageUrl(q.id)}?scale=20`;
  dl.download = `${fileBase}.png`;

  const svg = document.getElementById('modal-svg') as HTMLAnchorElement | null;
  if (svg) {
    svg.href = `${qrImageUrl(q.id)}?fmt=svg`;
    svg.download = `${fileBase}.svg`;
  }

  modal.hidden = false;
  document.body.classList.add('modal-open');
  void loadModalChart(q);
}

function closeModal(): void {
  const modal = document.getElementById('qr-modal');
  if (modal) modal.hidden = true;
  document.body.classList.remove('modal-open');
}

/* ── Edit view ───────────────────────────────────────────────── */

function openEditView(id: string | null): void {
  location.hash = '#edit' + (id != null ? `?id=${id}` : '');
}

/**
 * Fill the edit form from the id in the hash (`#edit?id=…`).
 * Survives page reloads: fetches the list if it is not loaded yet.
 */
export async function syncEditView(): Promise<void> {
  const id = new URLSearchParams(location.hash.split('?')[1] ?? '').get('id');
  const title = document.getElementById('edit-title');
  const nameInput = document.getElementById('edit-name') as HTMLInputElement;
  const linkInput = document.getElementById('edit-link') as HTMLInputElement;

  if (id == null) {
    currentEditId = null;
    if (title) title.innerHTML = 'New <em>code.</em>';
    nameInput.value = '';
    linkInput.value = '';
    return;
  }

  if (items.length === 0) {
    try { items = await fetchAll(); } catch { location.hash = '#dash'; return; }
  }
  const q = items.find(x => String(x.id) === id);
  if (!q) { location.hash = '#dash'; return; }

  currentEditId = q.id;
  if (title) title.innerHTML = 'Edit <em>code.</em>';
  nameInput.value = q.name;
  linkInput.value = q.link;
}

/** Prepend https:// when the scheme is missing; returns null for unparseable links. */
function normalizeLink(raw: string): string | null {
  const link = /^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ? raw : `https://${raw}`;
  try {
    new URL(link);
    return link;
  } catch {
    return null;
  }
}

async function handleEditSubmit(evt: Event): Promise<void> {
  evt.preventDefault();
  const name = (document.getElementById('edit-name') as HTMLInputElement).value.trim();
  const rawLink = (document.getElementById('edit-link') as HTMLInputElement).value.trim();
  if (!name || !rawLink) { flash(t('flashFillBoth'), 'error'); return; }
  const link = normalizeLink(rawLink);
  if (!link) { flash(t('flashBadLink'), 'error'); return; }

  const btn = (evt.target as HTMLFormElement).querySelector<HTMLButtonElement>('[type="submit"]');
  if (btn) btn.disabled = true;
  try {
    if (currentEditId != null) await updateQr(currentEditId, name, link);
    else                       await createQr(name, link);
    flash(currentEditId != null ? t('flashSaved') : t('flashCreated'));
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
    const target = e.target as HTMLElement;

    if (target.closest('[data-new]')) { openEditView(null); return; }
    if (target.closest('a')) return; // plain links keep their default behaviour

    const row = target.closest<HTMLElement>('[data-id]');
    if (!row?.dataset.id) return;
    const q = items.find(x => String(x.id) === row.dataset.id);
    if (!q) return;

    if (target.closest('[data-copy]')) { void copyText(qrPublicUrl(q.id)); return; }
    if (target.closest('[data-open]')) { openModal(q); return; }
    if (target.closest('[data-edit]')) { openEditView(q.id); return; }

    const del = target.closest<HTMLElement>('[data-delete]');
    if (del) {
      // two-step delete: first click arms the button, second confirms
      if (!del.classList.contains('arm')) {
        del.classList.add('arm');
        flash(t('flashDeleteArm'), 'info', 2200);
        setTimeout(() => del.classList.remove('arm'), 2400);
        return;
      }
      deleteQr(String(q.id))
        .then(() => { flash(t('flashDeleted')); return loadList(); })
        .catch((err: unknown) => flash(apiErr(err), 'error'));
    }
  });

  document.getElementById('btn-new')
    ?.addEventListener('click', () => openEditView(null));

  document.getElementById('editForm')
    ?.addEventListener('submit', handleEditSubmit);

  document.getElementById('search')
    ?.addEventListener('input', renderList);

  document.querySelectorAll<HTMLButtonElement>('[data-viewmode]').forEach(btn => {
    btn.addEventListener('click', () => setViewMode(btn.dataset.viewmode as ViewMode));
  });
  syncViewToggle();

  document.getElementById('qr-modal')?.addEventListener('click', e => {
    if ((e.target as HTMLElement).closest('[data-close]')) closeModal();
  });

  document.getElementById('modal-copy')?.addEventListener('click', () => {
    if (modalQr) void copyText(qrPublicUrl(modalQr.id));
  });

  document.getElementById('modal-print')?.addEventListener('click', () => window.print());
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });

  window.addEventListener('auth', (ev: Event) => {
    const { type } = (ev as CustomEvent<{ type: string }>).detail;
    if (type === 'login' || type === 'refresh') loadList();
    if (type === 'logout') closeModal();
  });

  // dynamic templates hold translated strings — redraw them on language change
  window.addEventListener('langchange', () => {
    if (document.body.dataset.route !== 'view-dash') return;
    updateCount(items.length);
    renderList();
  });
}
