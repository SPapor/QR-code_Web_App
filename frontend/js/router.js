import {
  login    as apiLogin,
  register as apiRegister,
  logout   as apiLogout,
  isLoggedIn
} from './auth.js';
import { loadList } from './qr.js';

const VIEWS = [...document.querySelectorAll('[data-view]')];

const hideAll = () => VIEWS.forEach(v => (v.hidden = true));
const show     = id => {
  hideAll();
  const el = document.getElementById(id);
  if (el) el.hidden = false;
};

function guard () {
  if (isLoggedIn()) return true;
  location.hash = '#login';
  return false;
}

function routeLogin    () { show('view-login'); }
function routeRegister () { show('view-reg');   }
function routeDash     () { if (guard()) { show('view-dash');  loadList(); } }
function routeEdit     () { if (guard()) show('view-edit'); }

const ROUTES = {
  ''        : routeLogin,
  '#':       routeLogin,
  '#login'  : routeLogin,
  '#reg'    : routeRegister,
  '#dash'   : routeDash,
  '#edit'   : routeEdit
};

function handleRoute () {
  const h = location.hash.split('?')[0];
  (ROUTES[h] || routeLogin)();
}

window.addEventListener('hashchange', handleRoute);
window.addEventListener('load', () => {
  if (isLoggedIn() && (!location.hash || location.hash === '#login')) {
    location.hash = '#dash';
  }
  handleRoute();
});

window.addEventListener('auth', ev => {
  const t = ev.detail.type;
  if (t === 'logout') location.hash = '#login';
  if (t === 'login')  location.hash = '#dash';
});

document.getElementById('loginForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const u = e.target.username.value.trim();
  const p = e.target.password.value.trim();
  try { await apiLogin(u, p); }
  catch (err) { alert(err?.detail || JSON.stringify(err)); }
});

document.getElementById('regForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const u = e.target.username.value.trim();
  const p = e.target.password.value.trim();
  try { await apiRegister(u, p); }
  catch (err) { alert(err?.detail || JSON.stringify(err)); }
});

document.getElementById('btn-logout')?.addEventListener('click', () => apiLogout());

export { handleRoute as reroute };
