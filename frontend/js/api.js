
import {authFetch} from './auth.js';

const API_BASE = 'http://192.168.1.135:8000';

export async function api(path, opts = {}) {
    const {qs, raw, ...fetchOpts} = opts;

    const url = API_BASE + path + (qs ? '?' + new URLSearchParams(qs) : '');

    const r = await authFetch(url, fetchOpts);

    if (!r.ok) throw await r.json();

    return raw ? r
        : (r.status === 204 ? null : r.json());   // 204 No Content ⇒ null
}

export const get = (path, qs) => api(path, {qs});
export const del = (path, qs) => api(path, {method: 'DELETE', qs});
export const post = (path, data, qs) => api(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    qs
});
export const put = (path, data, qs) => api(path, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    qs
});
