type ElAttrs = Record<string, unknown>;

export function el(tag: string, attrs: ElAttrs = {}, ...kids: (Node | string | null | undefined)[]): HTMLElement {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'class')     node.className = String(v);
    else if (k === 'html') node.innerHTML = String(v);
    else if (k === 'text') node.textContent = String(v);
    else if (k in node)    (node as unknown as Record<string, unknown>)[k] = v;
    else                   node.setAttribute(k, String(v));
  });
  kids.flat().forEach(kid => {
    if (kid == null) return;
    node.append(typeof kid === 'string' ? document.createTextNode(kid) : kid);
  });
  return node;
}

export const hide   = (e: HTMLElement | null) => { if (e) e.hidden = true;  };
export const show   = (e: HTMLElement | null) => { if (e) e.hidden = false; };
export const toggle = (e: HTMLElement | null) => { if (e) e.hidden = !e.hidden; };

export function on(
  root: HTMLElement,
  evt: string,
  selector: string,
  handler: (this: HTMLElement, e: Event) => void,
): void {
  root.addEventListener(evt, e => {
    const t = (e.target as HTMLElement).closest<HTMLElement>(selector);
    if (t && root.contains(t)) handler.call(t, e);
  });
}

export function flash(msg: string, type: 'info' | 'error' = 'info', ms = 2500): void {
  let box = document.getElementById('flash-box');
  if (!box) {
    box = el('div', { id: 'flash-box', class: 'flash' });
    document.body.append(box);
  }
  box.textContent = msg;
  box.classList.toggle('error', type === 'error');
  box.classList.add('show');
  box.hidden = false;
  if (ms > 0) setTimeout(() => { box!.classList.remove('show'); box!.hidden = true; }, ms);
}

/** Russian texts for the backend's {error_code, error_message} responses. */
const ERROR_RU: Record<string, string> = {
  'auth.0002': 'Сессия истекла — войдите снова',
  'auth.0003': 'Сессия истекла — войдите снова',
  'auth.0004': 'Неверный логин или пароль',
  'auth.0005': 'Нужны права администратора',
  'auth.0006': 'Слишком много попыток входа — попробуйте позже',
  'user.0002': 'Такой логин уже занят',
  'qr_code.0001': 'Код не найден',
  'core.0003': 'Ошибка сервера — попробуйте позже',
};

/** Human-readable message from an API error (backend error_code/error_message or FastAPI detail). */
export function apiErr(err: unknown): string {
  if (err && typeof err === 'object') {
    const e = err as { error_code?: unknown; error_message?: unknown; detail?: unknown };
    if (typeof e.error_code === 'string' && ERROR_RU[e.error_code]) return ERROR_RU[e.error_code];
    if (typeof e.error_message === 'string') return e.error_message;
    if (typeof e.detail === 'string') return e.detail;
    if (Array.isArray(e.detail)) {
      const msgs = e.detail.map(x => (x as { msg?: string })?.msg ?? '').filter(Boolean);
      if (msgs.length) return msgs.join('; ');
    }
  }
  if (err instanceof Error) return err.message;
  return 'Что-то пошло не так';
}

export function escapeHTML(s = ''): string {
  return s.replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] ?? c));
}

export function escapeAttr(s = ''): string {
  return escapeHTML(s).replace(/"/g, '&quot;');
}
