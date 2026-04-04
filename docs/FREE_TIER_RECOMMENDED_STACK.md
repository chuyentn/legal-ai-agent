# Free Tier Recommended Stack (Victor Dev)

This is the best free setup for the current codebase with minimal refactor and stable operations.

## Chosen stack

- Backend/API: Render Web Service (free)
- Database/Auth data: Supabase Postgres (free)
- Storage/API keys: Supabase project keys
- Frontend: serve static directly from backend domain
- DNS/CDN: Cloudflare DNS for custom domain only

## Why this is the best free option for this app

1. Current backend is FastAPI + PostgreSQL-first, already compatible.
2. No major rewrite needed (keeps velocity high).
3. Single-domain serving avoids CORS mismatch pain.
4. Render + Supabase free tiers are enough for pilot/demo and internal use.

## Production branch policy

- Deploy branch: `production-custom`
- Keep upstream sync on `main`
- Rebase `production-custom` on top of `main`

## Required env on Render

Minimum required for healthy backend:

- `ENV=production`
- `APP_PORT=8080`
- `ALLOWED_ORIGIN_REGEX=`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL=claude-sonnet-4-20250514`
- `CLAUDE_OAUTH_TOKEN`
- `SUPABASE_DB_HOST`
- `SUPABASE_DB_PORT`
- `SUPABASE_DB_PASSWORD`
- `DB_NAME`
- `DB_USER`
- `DB_SSL_MODE=require`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`
- `SUPABASE_JWT_SECRET`
- `ALLOWED_ORIGINS=https://legal-ai-agent.coach.io.vn`
- `API_KEY_SECRET`
- `LLM_ENCRYPTION_KEY`
- `SECRET_KEY`
- `OAUTH_REDIRECT_URI=https://legal-ai-agent.coach.io.vn/v1/llm/oauth/callback`
- `UPLOAD_DIR=/tmp/legal-ai-agent-uploads`

## Copy-ready .env block (Render)

Use this block directly in Render `Environment` (replace placeholder values):

```env
ENV=production
APP_PORT=8080

ALLOWED_ORIGINS=https://legal-ai-agent.coach.io.vn
ALLOWED_ORIGIN_REGEX=

ANTHROPIC_API_KEY=REPLACE_ANTHROPIC_API_KEY
ANTHROPIC_MODEL=claude-sonnet-4-20250514
CLAUDE_OAUTH_TOKEN=

SUPABASE_DB_HOST=REPLACE_SUPABASE_DB_HOST
SUPABASE_DB_PORT=5432
SUPABASE_DB_PASSWORD=REPLACE_SUPABASE_DB_PASSWORD
DB_NAME=postgres
DB_USER=postgres
DB_SSL_MODE=require

SUPABASE_URL=REPLACE_SUPABASE_URL
SUPABASE_ANON_KEY=REPLACE_SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=REPLACE_SUPABASE_SERVICE_KEY
SUPABASE_JWT_SECRET=REPLACE_SUPABASE_JWT_SECRET

SECRET_KEY=REPLACE_SECRET_KEY
API_KEY_SECRET=REPLACE_API_KEY_SECRET
LLM_ENCRYPTION_KEY=REPLACE_LLM_ENCRYPTION_KEY

OAUTH_REDIRECT_URI=https://legal-ai-agent.coach.io.vn/v1/llm/oauth/callback
UPLOAD_DIR=/tmp/legal-ai-agent-uploads
```

## Optional env (only if you use these integrations)

- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `OPENAI_CLIENT_ID`
- `OPENAI_CLIENT_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `CRAWLKIT_API_KEY`
- `CAL_API_KEY`
- `CAL_EVENT_LINK`
- `RESEND_API_KEY`
- `GOOGLE_APPS_SCRIPT_WEBHOOK_URL`
- `GOOGLE_SHEET_EDIT_URL`

## Common naming pitfalls

1. Use `SUPABASE_JWT_SECRET` (not `JWT_SECRET`).
2. Use `OAUTH_REDIRECT_URI` (not `OAUTH_REDIRECT_UR`).
3. App now supports `DATABASE_URL` fallback. If set, it is used first; otherwise app uses explicit DB vars (`SUPABASE_DB_*`, `DB_*`).

## Deploy checklist

1. Push code to `production-custom`.
2. Ensure Render service tracks `production-custom`.
3. Set/verify env vars.
4. Deploy and run migration in Render shell:

```bash
python scripts/run_migration.py
```

5. Run QA:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\qa_post_sync.ps1 -BaseUrl "https://legal-ai-agent.coach.io.vn"
```

## Expected free-tier caveats

- Cold starts on Render free instance.
- Limited compute; heavy indexing should run off-peak.
- Keep large data files out of git when possible (prefer storage/object store).
