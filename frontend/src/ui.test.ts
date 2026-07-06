import { describe, expect, it } from 'vitest';

import { escapeAttr, escapeHTML } from './ui';

// the QR list is rendered with innerHTML templates, so these two functions
// are the only thing standing between user-supplied names/links and XSS
describe('escapeHTML', () => {
  it('escapes tag-forming characters', () => {
    expect(escapeHTML('<img src=x onerror=alert(1)>')).toBe('&lt;img src=x onerror=alert(1)&gt;');
  });

  it('escapes quotes and ampersands', () => {
    expect(escapeHTML(`Tom & Jerry's "show"`)).toBe('Tom &amp; Jerry&#39;s &quot;show&quot;');
  });

  it('escapes a script tag completely', () => {
    const out = escapeHTML('<script>alert("xss")</script>');
    expect(out).not.toContain('<');
    expect(out).not.toContain('>');
    expect(out).not.toContain('"');
  });

  it('returns empty string for undefined input', () => {
    expect(escapeHTML(undefined)).toBe('');
  });

  it('leaves safe text untouched', () => {
    expect(escapeHTML('Menu page 1 — drinks')).toBe('Menu page 1 — drinks');
  });
});

describe('escapeAttr', () => {
  it('leaves no raw double quotes for attribute injection', () => {
    const out = escapeAttr('" onmouseover="alert(1)');
    expect(out).not.toContain('"');
  });

  it('escapes html as well', () => {
    expect(escapeAttr('<b>')).toBe('&lt;b&gt;');
  });
});
