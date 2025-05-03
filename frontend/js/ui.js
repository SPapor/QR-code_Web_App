// frontend/js/ui.js
// Tiny DOM-utility grab-bag. Zero dependencies, ES-module friendly.

export const q  = (sel, root = document)      => root.querySelector(sel);
export const qs = (sel, root = document)      => [...root.querySelectorAll(sel)];

/**
 * el('div', { class:'box', text:'Hi' }, otherEl, 'raw text')
 */
export function el (tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);

  Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'class')        node.className = v;
    else if (k === 'html')    node.innerHTML = v;
    else if (k === 'text')    node.textContent = v;
    else if (k in node)       node[k] = v;
    else                      node.setAttribute(k, v);
  });

  kids.flat().forEach(kid => {
    if (kid == null) return;
    node.append(kid.nodeType ? kid : document.createTextNode(kid));
  });

  return node;
}

/* ---------------------------------------------------------------- *\
   Show / hide helpers
\* ---------------------------------------------------------------- */

export const hide  = el => { if (el) el.hidden = true;  };
export const show  = el => { if (el) el.hidden = false; };
export const toggle= el => { if (el) el.hidden = !el.hidden; };

/* ---------------------------------------------------------------- *\
   Event-delegation helper
   on(parent, 'click', 'button[data-x]', e => ...)
\* ---------------------------------------------------------------- */

export function on (root, evt, selector, handler) {
  root.addEventListener(evt, e => {
    const t = e.target.closest(selector);
    if (t && root.contains(t)) handler.call(t, e);
  });
}

/* ---------------------------------------------------------------- *\
   Flash message (appears top-center, auto-dismiss)
\* ---------------------------------------------------------------- */

export function flash (msg, type = 'info', ms = 2500) {
  let box = q('#flash-box');
  if (!box) {
    box = el('div', { id: 'flash-box', class: 'flash' });
    document.body.append(box);
    const style = el('style', { html: `
      .flash{position:fixed;top:1rem;left:50%;transform:translateX(-50%);
             padding:.6rem 1.2rem;border-radius:.4rem;background:#333;color:#fff;
             font:14px/1 sans-serif;opacity:0;transition:opacity .2s;}
      .flash.show{opacity:1;}
      .flash.error{background:#c62828;}
    `});
    document.head.append(style);
  }
  box.textContent = msg;
  box.classList.toggle('error', type === 'error');
  box.classList.add('show');
  show(box);
  if (ms > 0) setTimeout(() => { box.classList.remove('show'); hide(box); }, ms);
}

/* ---------------------------------------------------------------- *\
   Escape utilities – handy for user-supplied strings
\* ---------------------------------------------------------------- */

export function escapeHTML (s = '') {
  return s.replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

export function escapeAttr (s = '') {
  return escapeHTML(s).replace(/"/g, '&quot;');
}
