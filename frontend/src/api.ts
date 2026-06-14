import { authFetch } from './auth';
import { API_BASE } from './config';

interface ApiOptions extends RequestInit {
  qs?: Record<string, string>;
  raw?: boolean;
}

export async function api<T = unknown>(path: string, opts: ApiOptions = {}): Promise<T | null> {
  const { qs, raw, ...fetchOpts } = opts;
  const url = API_BASE + path + (qs ? '?' + new URLSearchParams(qs) : '');
  const r = await authFetch(url, fetchOpts);
  if (!r.ok) throw await r.json();
  if (raw) return r as unknown as T;
  return r.status === 204 ? null : (r.json() as Promise<T>);
}

export const get  = <T>(path: string, qs?: Record<string, string>) =>
  api<T>(path, { qs });

export const del  = <T>(path: string, qs?: Record<string, string>) =>
  api<T>(path, { method: 'DELETE', qs });

export const post = <T>(path: string, data: unknown, qs?: Record<string, string>) =>
  api<T>(path, {
    method : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify(data),
    qs,
  });

export const put  = <T>(path: string, data: unknown, qs?: Record<string, string>) =>
  api<T>(path, {
    method : 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify(data),
    qs,
  });
