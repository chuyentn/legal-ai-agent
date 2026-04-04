# Supabase Production Env Mapping (project cjkrsnqdsfucngmrsnpm)

Use this mapping to configure backend runtime environment on your hosting platform.
Do not commit real secrets to GitHub.

## Values confirmed from your dashboard

- Project name: legal-ai-agent
- Project ID: cjkrsnqdsfucngmrsnpm
- API URL: https://cjkrsnqdsfucngmrsnpm.supabase.co

## Backend env values to set on host

ENV=production
APP_PORT=8080

ALLOWED_ORIGINS=https://legal-ai-agent.coach.io.vn
ALLOWED_ORIGIN_REGEX=

# PostgreSQL connection for app database features
SUPABASE_DB_HOST=db.cjkrsnqdsfucngmrsnpm.supabase.co
SUPABASE_DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_SSL_MODE=require
SUPABASE_DB_PASSWORD=<DB_PASSWORD_FROM_SUPABASE_DATABASE_SETTINGS>

# Supabase HTTP/storage APIs
SUPABASE_URL=https://cjkrsnqdsfucngmrsnpm.supabase.co
SUPABASE_ANON_KEY=<PUBLISHABLE_OR_ANON_KEY>
SUPABASE_SERVICE_KEY=<SERVER_SECRET_KEY>

# App security
SUPABASE_JWT_SECRET=<JWT_SECRET_FROM_SUPABASE_JWT_KEYS>
SECRET_KEY=<RANDOM_32+_CHARS>
API_KEY_SECRET=<RANDOM_32+_CHARS>
LLM_ENCRYPTION_KEY=<FERNET_KEY_32_BYTES_BASE64>

# AI provider
ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_KEY>
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Optional
CLAUDE_OAUTH_TOKEN=
CRAWLKIT_API_KEY=
UPLOAD_DIR=/tmp/legal-ai-agent-uploads
OAUTH_REDIRECT_URI=https://legal-ai-agent.coach.io.vn/v1/llm/oauth/callback

## Important notes

1. NEXT_PUBLIC_SUPABASE_* is frontend convention; this backend uses SUPABASE_URL and keys above.
2. If SUPABASE_DB_PASSWORD is wrong or missing, /v1/health will show database error.
3. After env update, redeploy and run QA script.

## Post-update verification

1. GET https://legal-ai-agent.coach.io.vn/v1/health must return status ok and database ok.
2. Run local command:
   powershell -ExecutionPolicy Bypass -File .\scripts\qa_post_sync.ps1 -BaseUrl "https://legal-ai-agent.coach.io.vn"
