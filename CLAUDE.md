# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

QR-code manager ("qr/studio"): FastAPI backend + vanilla-TS SPA frontend (PWA) + aiogram Telegram bot, deployed with docker compose on the owner's home server and exposed publicly via Tailscale Funnel at `https://qr.tailba71db.ts.net`. Generated QR images encode `{API_SCHEME}://{API_URL}/qr_code/{uuid}` (a 302-redirect endpoint), so `API_URL` in `.env` must point at the *frontend* origin — its nginx proxies `/qr_code|auth|user` to the backend.

## Commands

```bash
# full stack (backend :8000, frontend :3000)
docker compose up -d --build

# backend dev server (from app/, uses app/.venv)
cd app && .venv/bin/uvicorn main:app --reload

# tests (96 tests, in-memory sqlite; run from repo root)
app/.venv/bin/python -m pytest tests -q
app/.venv/bin/python -m pytest tests/test_auth/test_auth_api.py -q   # single file

# lint/format (repo root, targets ./app ./tests)
make lint    # autoflake + isort + black
make check   # check-black + check-isort + check-flake8

# frontend (from frontend/)
npm run dev     # vite dev server, proxies API to localhost:8000
npm run build   # tsc + vite build + PWA (sw.js, manifest)

# migrations (from app/; applied automatically on app startup)
.venv/bin/alembic revision --autogenerate -m "..."   # review the generated file
.venv/bin/alembic check                              # verify no schema drift
```

## Architecture

### Backend (`app/`) — layered modules with dishka DI

Each domain module (`user`, `auth`, `qr_code`, `telegram_auth`) has the same layout:
`router.py` → `services.py` → `dal.py` (Repo + Crud) → `tables.py`, plus `models.py` (frozen dataclass entity), `providers.py` (dishka Provider wiring the chain), `errors.py`/`api_errors.py` (domain exception → HTTP handler registration in `main.py`).

Key core machinery (read these before touching the data layer):
- `core/repo_base.py` — `RepoMeta` metaclass auto-wraps every repo coroutine to translate `NoResultFound`/unique `IntegrityError` into the entity's `NotFoundError`/`AlreadyExistError` (declared per-entity on the dataclass model).
- `core/crud_base.py` + `core/serializer.py` — generic CRUD over SQLAlchemy **Core tables** (not ORM models); rows are serialized to/from dataclass entities. All tables share `core.database.metadata`.
- `core/settings.py` — pydantic-settings, reads `.env` at repo root (`extra="ignore"`); env vars override the file.
- Session-per-request comes from dishka (`ConnectionProvider`); commit is centralized — services/repos don't commit.

Auth: JWT access token (15 min, `Authorization: Bearer`) + refresh JWT in an httponly cookie (`samesite`/`secure` from settings). `ADMIN_USERNAME`/`ADMIN_PASSWORD` are seeded at startup.

Migrations: alembic (`app/migrations/`), run at startup from `main.py` lifespan via `core/migrations.py` (in a thread — env.py calls `asyncio.run`). Migration `0001` adopts pre-alembic databases by skipping tables that already exist. Tests bypass alembic and use `create_tables()` directly. SQLite needs batch mode (already configured in env.py); dev/prod DB is sqlite, `DB_URI` also accepts postgres.

### Frontend (`frontend/`) — no framework

Vanilla TypeScript + Vite. Hash-based router (`src/router.ts`) toggles `<section data-view>` blocks in the single `index.html`; `src/qr.ts` renders the list with `innerHTML` templates (always escape via `escapeHTML`/`escapeAttr` from `src/ui.ts`). `API_BASE = ''` — all API calls are same-origin, proxied by nginx (prod) or vite (dev). Design system lives in `style.css` tokens (editorial style, Fraunces + Inter, auto dark mode via `prefers-color-scheme`). PWA via `vite-plugin-pwa` in `vite.config.ts`: API routes are NetworkOnly, QR images StaleWhileRevalidate.

### Bot (`bot/`)

Aiogram bot talking to the backend over the docker network (`BACKEND_URL=http://backend:8000`), authenticating through `/auth/telegram/exchange` with `BOT_SHARED_SECRET`.

## Deployment flow

- `dev` branch — work happens here; CI (`.github/workflows/pr-checks.yaml`) runs pytest + frontend build on every push (black/isort lint checks are advisory, flake8 is enforced).
- `master` — merging/pushing triggers `.github/workflows/deploy.yml` on a **self-hosted runner on this machine**: checkout → copy prod env from `~/.config/qr-menu/.env` → `docker compose up -d --build` → smoke check. Deploys happen **only** from master.
- Compose project name is pinned (`name: qr-menu` in docker-compose.yml) so any checkout dir reuses the same containers/volumes. The sqlite DB lives in the `db_data` volume mounted at `/data` (never mount it over `/app` — it will shadow the image code).
- `.env` at repo root is gitignored and holds real secrets; after changing it, also update `~/.config/qr-menu/.env` (used by deploys).
- The `db_backup` compose service snapshots the sqlite DB daily (`app/backup_db.py`, online backup API, keeps 14) into `~/qr-menu-backups` on the host (override with `QR_BACKUP_DIR`); with `BACKUP_TELEGRAM_CHAT_ID` set in `.env` each snapshot is also sent to that Telegram chat via the bot (offsite copy).

## Conventions

- Commits: single subject line only (`feat:`/`fix:`/`chore:` style), no body.
- Communicate with the owner in Russian; code/comments in English.
- Line length 120 (black `-S`, isort black profile — see root `Makefile`).
