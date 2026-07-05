export type Lang = 'ru' | 'en';

const LANG_KEY = 'lang';

/** Every user-facing string in both languages; editorial English headings (h1) are intentionally not translated. */
const STRINGS = {
  // auth views
  authSubLogin : { ru: 'Войдите, чтобы управлять своими QR-кодами', en: 'Sign in to manage your QR codes' },
  authSubReg   : { ru: 'Минута — и ваши QR-коды под контролем', en: 'One minute — and your QR codes are under control' },
  labelUsername: { ru: 'Логин', en: 'Username' },
  labelPassword: { ru: 'Пароль', en: 'Password' },
  btnLogin     : { ru: 'Войти', en: 'Sign in' },
  btnRegister  : { ru: 'Создать аккаунт', en: 'Create account' },
  or           : { ru: 'или', en: 'or' },
  googleLogin  : { ru: 'Войти через Google', en: 'Sign in with Google' },
  noAccount    : { ru: 'Нет аккаунта?', en: 'No account?' },
  createLink   : { ru: 'Создать', en: 'Sign up' },
  haveAccount  : { ru: 'Уже есть аккаунт?', en: 'Already have an account?' },
  loginLink    : { ru: 'Войти', en: 'Sign in' },
  usernameHint : { ru: '3–64 символа, без пробелов', en: '3–64 characters, no spaces' },

  // top bar
  btnLogout    : { ru: 'Выйти', en: 'Log out' },
  tgLinkTitle  : { ru: 'Привязать этот аккаунт к Telegram-боту', en: 'Link this account to the Telegram bot' },

  // settings modal
  settings       : { ru: 'Настройки', en: 'Settings' },
  language       : { ru: 'Язык', en: 'Language' },
  profile        : { ru: 'Профиль', en: 'Profile' },
  linked         : { ru: 'привязан', en: 'linked' },
  notLinked      : { ru: 'не привязан', en: 'not linked' },
  theme          : { ru: 'Тема', en: 'Theme' },
  themeLight     : { ru: 'Светлая', en: 'Light' },
  themeDark      : { ru: 'Тёмная', en: 'Dark' },
  themeSystem    : { ru: 'Как в системе', en: 'System' },
  palette        : { ru: 'Палитра', en: 'Palette' },
  palTerracotta  : { ru: 'Терракота', en: 'Terracotta' },
  palOcean       : { ru: 'Океан', en: 'Ocean' },
  palForest      : { ru: 'Лес', en: 'Forest' },
  palPlum        : { ru: 'Слива', en: 'Plum' },
  changePassword : { ru: 'Смена пароля', en: 'Change password' },
  currentPassword: { ru: 'Текущий пароль', en: 'Current password' },
  newPassword    : { ru: 'Новый пароль', en: 'New password' },
  btnChangePw    : { ru: 'Сменить пароль', en: 'Change password' },
  flashPwChanged : { ru: 'Пароль изменён', en: 'Password changed' },

  // dashboard
  newCode          : { ru: '+ Новый код', en: '+ New code' },
  searchPlaceholder: { ru: 'Поиск по названию или ссылке…', en: 'Search by name or link…' },
  searchAria       : { ru: 'Поиск по кодам', en: 'Search codes' },
  viewModeAria     : { ru: 'Вид списка', en: 'View mode' },
  gridTitle        : { ru: 'Сетка', en: 'Grid' },
  listTitle        : { ru: 'Список', en: 'List' },
  emptyTitle       : { ru: 'Пока пусто.', en: 'Nothing here yet.' },
  emptyText        : { ru: 'Создайте первый QR-код — это займёт меньше минуты.', en: 'Create your first QR code — it takes less than a minute.' },
  emptyCreate      : { ru: '+ Создать код', en: '+ Create code' },
  nothingFound     : { ru: 'Ничего не нашлось по «{q}»', en: 'Nothing found for “{q}”' },
  listError        : { ru: 'Ошибка: {msg}', en: 'Error: {msg}' },
  openQr           : { ru: 'Открыть QR', en: 'Open QR' },
  copyQrLink       : { ru: 'Скопировать ссылку QR', en: 'Copy QR link' },
  editAction       : { ru: 'Редактировать', en: 'Edit' },
  deleteAction     : { ru: 'Удалить', en: 'Delete' },

  // edit view
  labelName: { ru: 'Название', en: 'Name' },
  labelLink: { ru: 'Ссылка', en: 'Link' },
  save     : { ru: 'Сохранить', en: 'Save' },
  cancel   : { ru: 'Отмена', en: 'Cancel' },
  linkHint : { ru: 'Ссылка должна начинаться с http:// или https://', en: 'The link must start with http:// or https://' },

  // QR modal
  qrAlt      : { ru: 'QR-код', en: 'QR code' },
  close      : { ru: 'Закрыть', en: 'Close' },
  downloadPng: { ru: 'Скачать PNG', en: 'Download PNG' },
  print      : { ru: 'Печать', en: 'Print' },
  copyBtn    : { ru: 'Ссылка', en: 'Link' },
  chartAria  : { ru: 'Сканирования по дням за последние {n} дней', en: 'Scans per day over the last {n} days' },

  // tab titles
  titleLogin: { ru: 'вход', en: 'sign in' },
  titleReg  : { ru: 'регистрация', en: 'sign up' },
  titleDash : { ru: 'ваши коды', en: 'your codes' },
  titleEdit : { ru: 'код', en: 'code' },

  // flashes
  flashOauthFinishFail: { ru: 'Не удалось завершить вход', en: 'Could not finish sign-in' },
  flashOauthFail      : { ru: 'Вход через внешний сервис не удался', en: 'External sign-in failed' },
  flashCopied         : { ru: 'Ссылка скопирована', en: 'Link copied' },
  flashCopyFail       : { ru: 'Не удалось скопировать', en: 'Copy failed' },
  flashDeleteArm      : { ru: 'Нажмите ещё раз, чтобы удалить', en: 'Click again to delete' },
  flashDeleted        : { ru: 'Код удалён', en: 'Code deleted' },
  flashFillBoth       : { ru: 'Заполните оба поля', en: 'Fill in both fields' },
  flashBadLink        : { ru: 'Некорректная ссылка', en: 'Invalid link' },
  flashSaved          : { ru: 'Сохранено', en: 'Saved' },
  flashCreated        : { ru: 'Код создан', en: 'Code created' },

  // relative time
  justNow: { ru: 'только что', en: 'just now' },
  minAgo : { ru: '{n} мин назад', en: '{n} min ago' },
  hourAgo: { ru: '{n} ч назад', en: '{n} h ago' },

  // backend error codes
  'auth.0002'   : { ru: 'Сессия истекла — войдите снова', en: 'Session expired — sign in again' },
  'auth.0003'   : { ru: 'Сессия истекла — войдите снова', en: 'Session expired — sign in again' },
  'auth.0004'   : { ru: 'Неверный логин или пароль', en: 'Wrong username or password' },
  'auth.0005'   : { ru: 'Нужны права администратора', en: 'Admin rights required' },
  'auth.0006'   : { ru: 'Слишком много попыток входа — попробуйте позже', en: 'Too many attempts — try again later' },
  'auth.0007'   : { ru: 'Неверный текущий пароль', en: 'Current password is incorrect' },
  'user.0002'   : { ru: 'Такой логин уже занят', en: 'This username is already taken' },
  'qr_code.0001': { ru: 'Код не найден', en: 'Code not found' },
  'core.0003'   : { ru: 'Ошибка сервера — попробуйте позже', en: 'Server error — try again later' },
  somethingWrong: { ru: 'Что-то пошло не так', en: 'Something went wrong' },
} satisfies Record<string, Record<Lang, string>>;

export type MsgKey = keyof typeof STRINGS;

let lang: Lang = initialLang();

function initialLang(): Lang {
  const saved = localStorage.getItem(LANG_KEY);
  if (saved === 'ru' || saved === 'en') return saved;
  return navigator.language.toLowerCase().startsWith('ru') ? 'ru' : 'en';
}

export function getLang(): Lang {
  return lang;
}

export function setLang(next: Lang): void {
  if (next === lang) return;
  lang = next;
  localStorage.setItem(LANG_KEY, next);
  applyI18n();
  window.dispatchEvent(new CustomEvent('langchange'));
}

export function t(key: MsgKey, vars?: Record<string, string | number>): string {
  let text = STRINGS[key][lang];
  if (vars) for (const [k, v] of Object.entries(vars)) text = text.replace(`{${k}}`, String(v));
  return text;
}

/** Text for a backend {error_code} response, or null when the code is unknown. */
export function errorText(code: string): string | null {
  return lookup(code);
}

export function dateLocale(): string {
  return lang === 'ru' ? 'ru-RU' : 'en-GB';
}

/* ── Plural helpers ──────────────────────────────────────────── */

function ruPlural(n: number, one: string, few: string, many: string): string {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
  return many;
}

export function pluralCodes(n: number): string {
  return lang === 'ru' ? ruPlural(n, 'код', 'кода', 'кодов') : n === 1 ? 'code' : 'codes';
}

export function pluralScans(n: number): string {
  return lang === 'ru' ? ruPlural(n, 'сканирование', 'сканирования', 'сканирований') : n === 1 ? 'scan' : 'scans';
}

/** Short unit for list rows / cards: "12 скан." / "12 scans". */
export function scansShort(n: number): string {
  return lang === 'ru' ? 'скан.' : n === 1 ? 'scan' : 'scans';
}

/* ── Static markup ───────────────────────────────────────────── */

const ATTR_TARGETS = [
  ['data-i18n-placeholder', 'placeholder'],
  ['data-i18n-title', 'title'],
  ['data-i18n-aria', 'aria-label'],
  ['data-i18n-alt', 'alt'],
] as const;

function lookup(key: string): string | null {
  const entry = (STRINGS as Record<string, Record<Lang, string> | undefined>)[key];
  return entry ? entry[lang] : null;
}

/** (Re)translate everything annotated with data-i18n* in the static HTML; unknown keys are left as-is. */
export function applyI18n(): void {
  document.documentElement.lang = lang;
  document.querySelectorAll<HTMLElement>('[data-i18n]').forEach(node => {
    const text = lookup(node.dataset.i18n ?? '');
    if (text != null) node.textContent = text;
  });
  for (const [dataAttr, attr] of ATTR_TARGETS) {
    document.querySelectorAll<HTMLElement>(`[${dataAttr}]`).forEach(node => {
      const text = lookup(node.getAttribute(dataAttr) ?? '');
      if (text != null) node.setAttribute(attr, text);
    });
  }
}
