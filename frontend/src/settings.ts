import { authFetch, isLoggedIn, saveTokens } from './auth';
import { API_BASE } from './config';
import { applyI18n, getLang, setLang, t, type Lang } from './i18n';
import { apiErr, flash } from './ui';

type ThemePref = 'light' | 'dark' | 'system';

const THEME_KEY = 'theme';
const PALETTE_KEY = 'palette';
const DEFAULT_PALETTE = 'terracotta';
// keep in sync with --bg in style.css: the browser chrome should match the page
const THEME_COLOR = { light: '#FAF5EE', dark: '#151009' };

const systemDark = matchMedia('(prefers-color-scheme: dark)');

interface Me {
  username: string;
  telegram_linked: boolean;
  google_linked: boolean;
}

function themePref(): ThemePref {
  const saved = localStorage.getItem(THEME_KEY);
  return saved === 'light' || saved === 'dark' ? saved : 'system';
}

/** Resolve the preference to a concrete theme and stamp it on <html> (theme-init.js did the first pass). */
function applyTheme(): void {
  const pref = themePref();
  const dark = pref === 'dark' || (pref === 'system' && systemDark.matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? THEME_COLOR.dark : THEME_COLOR.light);
}

function setThemePref(pref: ThemePref): void {
  if (pref === 'system') localStorage.removeItem(THEME_KEY);
  else localStorage.setItem(THEME_KEY, pref);
  applyTheme();
}

function currentPalette(): string {
  return localStorage.getItem(PALETTE_KEY) ?? DEFAULT_PALETTE;
}

function setPalette(name: string): void {
  if (name === DEFAULT_PALETTE) {
    localStorage.removeItem(PALETTE_KEY);
    delete document.documentElement.dataset.palette;
  } else {
    localStorage.setItem(PALETTE_KEY, name);
    document.documentElement.dataset.palette = name;
  }
}

/** Settings modal: profile & links, theme, palette, language, password change. */
export function initSettings(): void {
  const modal = document.getElementById('settings-modal');
  if (!modal) return;

  applyTheme();
  systemDark.addEventListener('change', () => {
    if (themePref() === 'system') applyTheme();
  });

  const syncControls = (): void => {
    modal.querySelectorAll<HTMLButtonElement>('[data-theme-opt]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.themeOpt === themePref());
    });
    modal.querySelectorAll<HTMLButtonElement>('[data-palette-opt]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.paletteOpt === currentPalette());
    });
    modal.querySelectorAll<HTMLButtonElement>('[data-lang]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === getLang());
    });
  };

  const linkChip = (label: string, linked: boolean): string => {
    const state = linked ? t('linked') : t('notLinked');
    return `<span class="link-chip${linked ? ' on' : ''}">${label} · ${state}</span>`;
  };

  const syncProfile = async (): Promise<void> => {
    const profile = document.getElementById('set-profile');
    const password = document.getElementById('set-password');
    const logged = isLoggedIn();
    if (profile) profile.hidden = !logged;
    if (password) password.hidden = !logged;
    if (!logged) return;

    try {
      const r = await authFetch(`${API_BASE}/user/me`);
      if (!r.ok) return;
      const me: Me = await r.json();
      const nameBox = document.getElementById('settings-user');
      if (nameBox) nameBox.textContent = me.username;
      const links = document.getElementById('profile-links');
      if (links) links.innerHTML = linkChip('Telegram', me.telegram_linked) + linkChip('Google', me.google_linked);
    } catch {
      /* profile info is decoration; the rest of the modal still works */
    }
  };

  const open = (): void => {
    syncControls();
    void syncProfile();
    modal.hidden = false;
    document.body.classList.add('settings-open');
  };
  const close = (): void => {
    modal.hidden = true;
    document.body.classList.remove('settings-open');
  };

  document.getElementById('btn-settings')?.addEventListener('click', open);

  modal.addEventListener('click', e => {
    const target = e.target as HTMLElement;
    if (target.closest('[data-close]')) { close(); return; }

    const themeOpt = target.closest<HTMLElement>('[data-theme-opt]');
    if (themeOpt) { setThemePref(themeOpt.dataset.themeOpt as ThemePref); syncControls(); return; }

    const paletteOpt = target.closest<HTMLElement>('[data-palette-opt]');
    if (paletteOpt?.dataset.paletteOpt) { setPalette(paletteOpt.dataset.paletteOpt); syncControls(); return; }

    const langOpt = target.closest<HTMLElement>('[data-lang]');
    if (langOpt) { setLang(langOpt.dataset.lang as Lang); syncControls(); }
  });

  window.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !modal.hidden) close();
  });

  window.addEventListener('langchange', () => {
    applyI18n();
    // the linked/not-linked chips hold translated text
    if (!modal.hidden) void syncProfile();
  });

  window.addEventListener('auth', (ev: Event) => {
    const { type } = (ev as CustomEvent<{ type: string }>).detail;
    if (type === 'logout') close();
  });

  document.getElementById('pwForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const oldPw = (form.elements.namedItem('old_password') as HTMLInputElement).value;
    const newPw = (form.elements.namedItem('new_password') as HTMLInputElement).value;
    const btn = form.querySelector<HTMLButtonElement>('[type="submit"]');
    if (btn) btn.disabled = true;
    try {
      const r = await authFetch(`${API_BASE}/auth/change_password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_password: oldPw, new_password: newPw }),
      });
      if (!r.ok) throw await r.json();
      // password change rotates the session: adopt the fresh token pair so this
      // device stays logged in (all other sessions are revoked server-side)
      saveTokens(await r.json());
      form.reset();
      flash(t('flashPwChanged'));
    } catch (err: unknown) {
      flash(apiErr(err), 'error');
    } finally {
      if (btn) btn.disabled = false;
    }
  });
}
