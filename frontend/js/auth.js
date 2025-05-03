const API_BASE  = 'http://192.168.1.135:8000';
const ACCESS_KEY = 'access';
const EXP_KEY    = 'exp';

export function getAccess () {
  return localStorage.getItem(ACCESS_KEY) || null;
}

export function isLoggedIn () {
  return !!getAccess();
}

export async function login (username, password) {
  const body = new URLSearchParams({ username, password });

  const r = await fetch(`${API_BASE}/auth/login`, {
    method      : 'POST',
    headers     : { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
    credentials : 'include'
  });
  if (!r.ok) throw await r.json();

  const data = await r.json();
  saveTokens(data);
  signal('login');
  return data;
}

export async function register (username, password) {
  const r = await fetch(`${API_BASE}/user/register`, {
    method      : 'POST',
    headers     : { 'Content-Type': 'application/json' },
    body        : JSON.stringify({ username, password }),
    credentials : 'include'
  });
  if (!r.ok) throw await r.json();
  return login(username, password);
}

export async function refreshToken () {
  const r = await fetch(`${API_BASE}/auth/refresh`, {
    method      : 'POST',
    credentials : 'include'
  });

  if (!r.ok) {
    logout();
    throw await r.json();
  }

  const data = await r.json();
  saveTokens(data);
  signal('refresh');
  return data.access_token;
}

export function logout () {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(EXP_KEY);
  signal('logout');
}

export async function authFetch (url, opts = {}) {
  let token = await ensureValidAccess();
  opts.headers      = { ...opts.headers, Authorization: `Bearer ${token}` };
  opts.credentials  = 'include';

  let r = await fetch(url, opts);

  if (r.status === 401) {
    token = await refreshToken();
    opts.headers.Authorization = `Bearer ${token}`;
    r = await fetch(url, opts);
  }
  return r;
}

function saveTokens ({ access_token, expires_in }) {
  localStorage.setItem(ACCESS_KEY, access_token);

  if (expires_in) {
    const expMs = Date.now() + expires_in * 1000;
    localStorage.setItem(EXP_KEY, expMs.toString());
  } else {
    localStorage.removeItem(EXP_KEY);
  }
}

function tokenExpiresSoon () {
  const exp = parseInt(localStorage.getItem(EXP_KEY) || '0', 10);
  return exp && Date.now() > exp - 30_000; // false if exp == 0
}

async function ensureValidAccess () {
  if (!getAccess()) throw new Error('Not authenticated');

  if (tokenExpiresSoon()) {
    try { await refreshToken(); } catch {}
  }
  return getAccess();
}

function signal (type) {
  window.dispatchEvent(new CustomEvent('auth', { detail: { type } }));
}
