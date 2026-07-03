import { login as apiLogin, register as apiRegister, logout as apiLogout, isLoggedIn, getUsername } from './auth';
import { loadList } from './qr';
import { flash, apiErr } from './ui';

const VIEWS = [...document.querySelectorAll<HTMLElement>('[data-view]')];
const hideAll  = () => VIEWS.forEach(v => (v.hidden = true));
const showView = (id: string) => {
  hideAll();
  const e = document.getElementById(id);
  if (e) e.hidden = false;
  document.body.dataset.route = id;
};

function syncUser(): void {
  const box = document.getElementById('user-name');
  if (box) box.textContent = getUsername() ?? '';
}

function guard(): boolean {
  if (isLoggedIn()) return true;
  location.hash = '#login';
  return false;
}

function routeLogin(): void {
  showView('view-login');
  const f = document.getElementById('loginForm') as HTMLFormElement | null;
  if (f) {
    f.reset();
    // Browser autofill fires asynchronously after the element becomes visible,
    // overriding synchronous clears. Defer to run after autofill settles.
    setTimeout(() => {
      (f.elements.namedItem('username') as HTMLInputElement).value = '';
      (f.elements.namedItem('password') as HTMLInputElement).value = '';
    }, 50);
  }
}
function routeRegister(): void { showView('view-reg');  }
function routeDash():     void { if (guard()) { showView('view-dash'); loadList(); } }
function routeEdit():     void { if (guard()) showView('view-edit'); }

const ROUTES: Record<string, () => void> = {
  ''       : routeLogin,
  '#'      : routeLogin,
  '#login' : routeLogin,
  '#reg'   : routeRegister,
  '#dash'  : routeDash,
  '#edit'  : routeEdit,
};

function handleRoute(): void {
  const h = location.hash.split('?')[0];
  (ROUTES[h] ?? routeLogin)();
}

window.addEventListener('hashchange', handleRoute);
window.addEventListener('load', () => {
  if (isLoggedIn() && (!location.hash || location.hash === '#login')) {
    location.hash = '#dash';
  }
  syncUser();
  handleRoute();
});

window.addEventListener('auth', (ev: Event) => {
  const { type } = (ev as CustomEvent<{ type: string }>).detail;
  syncUser();
  if (type === 'logout') location.hash = '#login';
  if (type === 'login')  location.hash = '#dash';
});

async function submitAuth(e: Event, action: (u: string, p: string) => Promise<unknown>): Promise<void> {
  e.preventDefault();
  const form = e.target as HTMLFormElement;
  const u = (form.elements.namedItem('username') as HTMLInputElement).value.trim();
  const p = (form.elements.namedItem('password') as HTMLInputElement).value.trim();
  const btn = form.querySelector<HTMLButtonElement>('[type="submit"]');
  if (btn) btn.disabled = true;
  try { await action(u, p); }
  catch (err: unknown) { flash(apiErr(err), 'error'); }
  finally { if (btn) btn.disabled = false; }
}

(document.getElementById('loginForm') as HTMLFormElement | null)
  ?.addEventListener('submit', e => submitAuth(e, apiLogin));

(document.getElementById('regForm') as HTMLFormElement | null)
  ?.addEventListener('submit', e => submitAuth(e, apiRegister));

document.getElementById('btn-logout')
  ?.addEventListener('click', () => apiLogout());
