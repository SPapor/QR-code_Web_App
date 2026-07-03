# qr/studio

QR-code manager: create named QR codes that redirect to any link, manage them from a web dashboard (installable as a PWA) or a Telegram bot.

**Live:** https://qr.tailba71db.ts.net (home server behind Tailscale Funnel)

## Stack

- **Backend** — FastAPI + SQLAlchemy Core + dishka DI, alembic migrations (auto-applied on startup), JWT auth with refresh cookie
- **Frontend** — vanilla TypeScript + Vite, editorial UI with auto dark mode, PWA (Android/iOS installable)
- **Bot** — aiogram, talks to the backend over the docker network
- **Infra** — docker compose; CI on `dev` (pytest + frontend build + lint), auto-deploy on push to `master` via self-hosted GitHub Actions runner

## Run

```bash
cp .env.example .env   # or craft your own; see app/core/settings.py for options
docker compose up -d --build
# frontend → http://localhost:3000, backend → http://localhost:8000/docs
```

## Develop

```bash
app/.venv/bin/python -m pytest tests -q   # tests
make lint && make check                   # format + lint
cd frontend && npm run dev                # frontend dev server
```

Work in `dev` (CI runs on every push), merge to `master` to deploy.
