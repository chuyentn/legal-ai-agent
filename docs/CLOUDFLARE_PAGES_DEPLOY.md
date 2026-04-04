# Cloudflare Pages + Backend API Deploy

This project is backend-first (FastAPI) and can be deployed in split mode:

- Frontend static files on Cloudflare Pages
- Backend API on Render/Railway/Docker/VPS

Production templates and runbook:

- [.env.production.example](../.env.production.example)
- [docs/GITHUB_DEPLOY_ONLINE_PLAN.md](GITHUB_DEPLOY_ONLINE_PLAN.md)
- [docs/CLOUDFLARE_PAGES_ENV.md](CLOUDFLARE_PAGES_ENV.md)

## 1) Deploy backend API first

Deploy the FastAPI service to a Python/container host.

Required env vars (minimum):

- `ANTHROPIC_API_KEY` (or another configured provider)
- DB/Supabase variables
- `SUPABASE_JWT_SECRET`
- `ALLOWED_ORIGINS`
- `ALLOWED_ORIGIN_REGEX` (optional)

Recommended CORS:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,https://legal-ai-agent.coach.io.vn,https://your-pages-domain.pages.dev
ALLOWED_ORIGIN_REGEX=^https://.*\.pages\.dev$
```

Search data source note:

- Your legal search library depends on a healthy PostgreSQL/Supabase connection.
- If `/v1/health` shows `database: error`, search/indexed data endpoints will be degraded.
- Ensure production DB env vars are correct and migrations are applied before rollout.

Verify backend:

- `GET https://your-api-domain/v1/health`

## 2) Deploy frontend to Cloudflare Pages

Use this repository as source. Two common options:

- Build command: leave empty (static)
- Output directory:
  - `.` (repo root), then open `/static/index.html`
  - or `static` (recommended), then open `/index.html`

## 3) Bind frontend to backend API

Because frontend can run on different origin, pass API base once in URL:

- App: `https://your-pages-domain/static/app.html?api_base=https://your-api-domain`
- Admin: `https://your-pages-domain/static/admin.html?api_base=https://your-api-domain`
- Platform admin: `https://your-pages-domain/static/platform-admin.html?api_base=https://your-api-domain`

Custom-domain example:

- `https://legal-ai-agent.coach.io.vn/static/app.html?api_base=https://legal-ai-agent.coach.io.vn`

The app stores this in localStorage key `LEGAL_API_BASE_URL` and reuses it automatically.

Production recommendation:

- Configure runtime injection via Cloudflare Pages variables and build command.
- See [docs/CLOUDFLARE_PAGES_ENV.md](CLOUDFLARE_PAGES_ENV.md).

## 4) Troubleshooting

### 404 on `/v1/*` in browser

Cause: frontend is calling its own Pages domain instead of API domain.

Fix: open with `?api_base=https://your-api-domain` once.

### CORS blocked

Cause: backend does not allow your Pages origin.

Fix: add origin to `ALLOWED_ORIGINS` or use `ALLOWED_ORIGIN_REGEX`.

### Cloudflare 522

Cause: origin backend not reachable or timed out.

Fix:

- verify backend URL directly from browser/curl
- check backend host logs and health endpoint
- ensure domain DNS/proxy points to running service
