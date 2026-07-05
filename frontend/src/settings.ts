import { getUsername } from './auth';
import { getLang, setLang, type Lang } from './i18n';

/** Settings dropdown in the top bar: profile line + language switcher. */
export function initSettings(): void {
  const btn = document.getElementById('btn-settings');
  const menu = document.getElementById('settings-menu');
  if (!btn || !menu) return;

  const syncMenu = (): void => {
    const userBox = document.getElementById('settings-user');
    if (userBox) {
      const username = getUsername();
      userBox.textContent = username ?? '';
      userBox.hidden = !username;
    }
    menu.querySelectorAll<HTMLButtonElement>('.lang-opt').forEach(opt => {
      const active = opt.dataset.lang === getLang();
      opt.classList.toggle('active', active);
      opt.setAttribute('aria-checked', String(active));
    });
  };

  const close = (): void => {
    menu.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
  };

  btn.addEventListener('click', () => {
    if (menu.hidden) {
      syncMenu();
      menu.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
    } else {
      close();
    }
  });

  menu.addEventListener('click', e => {
    const opt = (e.target as HTMLElement).closest<HTMLElement>('.lang-opt');
    if (!opt?.dataset.lang) return;
    setLang(opt.dataset.lang as Lang);
    syncMenu();
    close();
  });

  document.addEventListener('click', e => {
    if (!menu.hidden && !(e.target as HTMLElement).closest('.prefs')) close();
  });
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') close();
  });
  window.addEventListener('auth', syncMenu);
}
