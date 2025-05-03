// frontend/js/auth.js
// Lightweight auth helper for the FastAPI backend.
// Pure ES-module, no dependencies – just import the functions you need.

const API_BASE = 'http://192.168.1.135:8000';               // Same-origin by default; override if backend is on another host.
const ACCESS_KEY = 'access';
const REFRESH_KEY = 'refresh';
const EXP_KEY = 'exp';         // millis-since-epoch when access token expires

/* ---------------------------------------------------------------- *\
   Public API
\* ---------------------------------------------------------------- */

export function getAccess() {
    return localStorage.getItem(ACCESS_KEY) || null;
}

export function isLoggedIn() {
    return !!getAccess();
}

export async function login(username, password) {
    const body = new URLSearchParams({username, password});
    const r = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body
    });
    if (!r.ok) throw await r.json();
    const data = await r.json();         // {access_token, refresh_token, expires_in}
    saveTokens(data);
    signal('login');
    return data;
}

export async function register(username, password) {
    const r = await fetch(`${API_BASE}/user/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    if (!r.ok) throw await r.json();
    // Auto-login after successful sign-up
    return login(username, password);
}

export async function refreshToken() {
    const refresh = localStorage.getItem(REFRESH_KEY);
    if (!refresh) throw new Error('No refresh token');
    const r = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: {'Authorization': `Bearer ${refresh}`}
    });
    if (!r.ok) {
        logout();                         // refresh token no longer valid
        throw await r.json();
    }
    const data = await r.json();        // {access_token, expires_in}
    saveTokens({...data, refresh_token: refresh});
    signal('refresh');
    return data.access_token;
}

export function logout() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(EXP_KEY);
    signal('logout');
}

/**
 * `authFetch` wraps window.fetch with automatic bearer header and token refresh.
 * Usage: `const res = await authFetch('/qr_code/');`
 */
export async function authFetch(url, opts = {}) {
    let token = await ensureValidAccess();
    opts.headers = {...opts.headers, Authorization: `Bearer ${token}`};

    let r = await fetch(url, opts);

    // If backend still complains, try one forced refresh then repeat once
    if (r.status === 401) {
        token = await refreshToken();
        opts.headers.Authorization = `Bearer ${token}`;
        r = await fetch(url, opts);
    }
    return r;
}

/* ---------------------------------------------------------------- *\
   Internals
\* ---------------------------------------------------------------- */

function saveTokens({access_token, refresh_token, expires_in}) {
    localStorage.setItem(ACCESS_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    // store absolute expiry time in ms; refresh ~30 s early
    const expMs = Date.now() + (expires_in * 1000);
    localStorage.setItem(EXP_KEY, expMs.toString());
}

function tokenExpiresSoon() {
    const exp = parseInt(localStorage.getItem(EXP_KEY) || '0', 10);
    return Date.now() > (exp - 30_000);        // 30-second safety window
}

async function ensureValidAccess() {
    if (!getAccess()) throw new Error('Not authenticated');
    if (tokenExpiresSoon()) {
        try {
            await refreshToken();
        } catch (_) { /* will fall through */
        }
    }
    return getAccess();
}

function signal(type) {
    window.dispatchEvent(new CustomEvent('auth', {detail: {type}}));
}
