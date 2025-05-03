// frontend/js/api.js
// Generic, token-aware fetch helpers built on top of authFetch()

import {authFetch} from './auth.js';

const API_BASE = 'http://192.168.1.135:8000';   // Same-origin by default; prefix all calls with this if backend is on another host.

/* ---------------------------------------------------------------- *\
    Core helper
\* ---------------------------------------------------------------- */

/**
 * api() – one liner to hit the FastAPI backend.
 *
 * @param {string} path        e.g. '/qr_code/'
 * @param {object} [opts]      fetch options; same as window.fetch
 * @param {object} [opts.qs]   optional object turned into query string
 * @param {boolean}[opts.raw]  if true, caller gets the raw Response
 */
export async function api(path, opts = {}) {
    const {qs, raw, ...fetchOpts} = opts;

    const url = API_BASE + path + (qs ? '?' + new URLSearchParams(qs) : '');

    const r = await authFetch(url, fetchOpts);

    if (!r.ok) throw await r.json();

    return raw ? r
        : (r.status === 204 ? null : r.json());   // 204 No Content ⇒ null
}

/* ---------------------------------------------------------------- *\
    Convenience wrappers
\* ---------------------------------------------------------------- */

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
