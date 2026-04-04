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
- `ANTHROPIC_API_KEY`
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
