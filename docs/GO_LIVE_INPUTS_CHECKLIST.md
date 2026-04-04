# Go-Live Inputs Checklist

Use this checklist to provide all required information for end-to-end online deployment.

## 1) Hosting and deployment target

- Hosting platform for backend (Render/Railway/VPS/other):
- Service name:
- Region:
- Deploy branch: production-custom

## 2) Domain and DNS

- Production domain: https://legal-ai-agent.coach.io.vn
- DNS provider:
- TLS/SSL mode:
- If using Cloudflare proxy, status (Proxied or DNS only):

## 3) Database connection (required)

- SUPABASE_DB_HOST:
- SUPABASE_DB_PORT:
- SUPABASE_DB_PASSWORD:
- DB_NAME:
- DB_USER:
- DB_SSL_MODE: require (managed DB) or disable (internal Docker DB)

## 4) Supabase API/storage (recommended)

- SUPABASE_URL:
- SUPABASE_SERVICE_KEY:
- SUPABASE_ANON_KEY:

## 5) Security secrets (required)

- SUPABASE_JWT_SECRET:
- SECRET_KEY:
- API_KEY_SECRET:
- LLM_ENCRYPTION_KEY:

## 6) AI provider credentials

- ANTHROPIC_API_KEY (or OpenAI/Google keys):
- ANTHROPIC_MODEL (optional, default allowed):
- CLAUDE_OAUTH_TOKEN (optional):

## 7) OAuth (optional)

- OAUTH_REDIRECT_URI (if OAuth flow used):
- OPENAI_CLIENT_ID:
- OPENAI_CLIENT_SECRET:
- GOOGLE_CLIENT_ID:
- GOOGLE_CLIENT_SECRET:

## 8) Cloudflare Pages runtime env (if frontend on Pages)

- LEGAL_API_BASE_URL:
- LEGAL_APP_ENV: production

## 9) Access for assisted execution

Provide one of the following:

- Temporary operator access to hosting dashboard
- Or run commands sent by assistant and paste outputs

## 10) Acceptance criteria

Go-live is complete when all are true:

- GET /v1/health => status ok
- GET /v1/health => database ok
- Landing/App/Admin/Pricing checks pass
- Login works
- One write-read test for contracts or documents passes
