import { API_BASE } from './config';

interface TokenResponse {
  access_token: string;
  expires_in?: number;
}

type AuthEventType = 'login' | 'logout' | 'refresh';

const ACCESS_KEY = 'access';
const EXP_KEY    = 'exp';
const USER_KEY   = 'username';

export function getAccess(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

export function getUsername(): string | null {
  return localStorage.getItem(USER_KEY);
}

export function isLoggedIn(): boolean {
  return !!getAccess();
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username, password });
  const r = await fetch(`${API_BASE}/auth/login`, {
    method     : 'POST',
    headers    : { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
    credentials: 'include',
  });
  if (!r.ok) throw await r.json();
  const data: TokenResponse = await r.json();
  saveTokens(data);
  signal('login');
  return data;
}

export async function register(username: string, password: string): Promise<TokenResponse> {
  const r = await fetch(`${API_BASE}/user/register`, {
    method     : 'POST',
    headers    : { 'Content-Type': 'application/json' },
    body       : JSON.stringify({ username, password }),
    credentials: 'include',
  });
  if (!r.ok) throw await r.json();
  return login(username, password);
}

export async function refreshToken(): Promise<string> {
  const r = await fetch(`${API_BASE}/auth/refresh`, {
    method     : 'POST',
    credentials: 'include',
  });
  if (!r.ok) {
    logout();
    throw await r.json();
  }
  const data: TokenResponse = await r.json();
  saveTokens(data);
  signal('refresh');
  return data.access_token;
}

export function logout(): void {
  // revoke the refresh session server-side; best-effort, don't block the UI
  void fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' }).catch(() => {});
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(EXP_KEY);
  localStorage.removeItem(USER_KEY);
  signal('logout');
}

export async function authFetch(url: string, opts: RequestInit = {}): Promise<Response> {
  let token = await ensureValidAccess();
  opts.headers = { ...opts.headers, Authorization: `Bearer ${token}` };
  opts.credentials = 'include';

  let r = await fetch(url, opts);
  if (r.status === 401) {
    token = await refreshToken();
    (opts.headers as Record<string, string>).Authorization = `Bearer ${token}`;
    r = await fetch(url, opts);
  }
  return r;
}

export function saveTokens({ access_token, expires_in }: TokenResponse): void {
  localStorage.setItem(ACCESS_KEY, access_token);
  const username = usernameFromToken(access_token);
  if (username) localStorage.setItem(USER_KEY, username);
  if (expires_in) {
    localStorage.setItem(EXP_KEY, String(Date.now() + expires_in * 1000));
  } else {
    localStorage.removeItem(EXP_KEY);
  }
}

function usernameFromToken(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    return typeof payload.username === 'string' ? payload.username : null;
  } catch {
    return null;
  }
}

function tokenExpiresSoon(): boolean {
  const exp = parseInt(localStorage.getItem(EXP_KEY) ?? '0', 10);
  return !!exp && Date.now() > exp - 30_000;
}

async function ensureValidAccess(): Promise<string> {
  const token = getAccess();
  if (!token) throw new Error('Not authenticated');
  if (tokenExpiresSoon()) {
    try { await refreshToken(); } catch { /* silently retry on next request */ }
  }
  return getAccess()!;
}

function signal(type: AuthEventType): void {
  window.dispatchEvent(new CustomEvent('auth', { detail: { type } }));
}
