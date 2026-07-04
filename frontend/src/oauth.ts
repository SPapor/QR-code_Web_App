import { authFetch } from './auth';
import { API_BASE } from './config';
import { flash, apiErr } from './ui';

interface AuthConfig {
  telegram_login: boolean;
  telegram_bot_username: string | null;
  google_login: boolean;
}

let configPromise: Promise<AuthConfig> | null = null;

function loadConfig(): Promise<AuthConfig> {
  configPromise ??= fetch(`${API_BASE}/auth/config`).then(r => {
    if (!r.ok) throw new Error('config unavailable');
    return r.json();
  });
  return configPromise;
}

/** Show/inject external-login buttons on the login view. Safe to call repeatedly. */
export async function initOAuthButtons(): Promise<void> {
  let cfg: AuthConfig;
  try { cfg = await loadConfig(); } catch { return; }

  const divider   = document.getElementById('oauth-divider');
  const googleBtn = document.getElementById('btn-google');
  const tgSlot    = document.getElementById('tg-login-slot');

  const tgEnabled = cfg.telegram_login && !!cfg.telegram_bot_username;
  if (divider)   divider.hidden   = !(tgEnabled || cfg.google_login);
  if (googleBtn) googleBtn.hidden = !cfg.google_login;

  if (tgSlot && tgEnabled && !tgSlot.hasChildNodes()) {
    const s = document.createElement('script');
    s.src = 'https://telegram.org/js/telegram-widget.js?22';
    s.async = true;
    s.setAttribute('data-telegram-login', cfg.telegram_bot_username!);
    s.setAttribute('data-size', 'large');
    s.setAttribute('data-userpic', 'false');
    s.setAttribute('data-request-access', 'write');
    s.setAttribute('data-auth-url', `${location.origin}/auth/telegram/callback`);
    tgSlot.appendChild(s);
  }
}

/** Show the "open in Telegram" button in the top bar when the bot is configured. */
export async function syncTelegramButton(): Promise<void> {
  const btn = document.getElementById('btn-telegram');
  if (!btn) return;
  const cfg = await loadConfig().catch(() => null);
  btn.hidden = !cfg?.telegram_bot_username;
}

/**
 * Issue a one-time link code and open the bot chat via deep link,
 * so the bot binds this Telegram chat to the current website account.
 */
export async function openTelegramBot(): Promise<void> {
  const cfg = await loadConfig().catch(() => null);
  if (!cfg?.telegram_bot_username) return;
  // open synchronously so popup blockers treat it as a user gesture
  const win = window.open('', '_blank');
  try {
    const r = await authFetch(`${API_BASE}/auth/telegram/link_code`, { method: 'POST' });
    if (!r.ok) throw await r.json();
    const { code } = await r.json();
    const url = `https://t.me/${cfg.telegram_bot_username}?start=link_${code}`;
    if (win) win.location.href = url;
    else location.href = url;
  } catch (err) {
    win?.close();
    flash(apiErr(err), 'error');
  }
}
