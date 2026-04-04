# Cloudflare Pages Environment Setup

Use this file to configure runtime API base on Cloudflare Pages without editing HTML each release.

## Required Pages variable

Set in Cloudflare Pages project settings:

- `LEGAL_API_BASE_URL` = `https://legal-ai-agent.coach.io.vn`
- `LEGAL_APP_ENV` = `production`

## Build command

Use a build command that renders `static/runtime-config.js` from variables:

```bash
cat > static/runtime-config.js <<EOF
window.LEGAL_API_BASE_URL = "${LEGAL_API_BASE_URL}";
window.LEGAL_APP_ENV = "${LEGAL_APP_ENV}";
EOF
```

## Output directory

- If deploying whole repo: `.`
- If deploying only static: `static`

## Verify after deploy

Open:

- `/static/app.html`
- `/static/admin.html`
- `/static/platform-admin.html`

Then check network requests to `/v1/*` go to the API domain configured in `LEGAL_API_BASE_URL`.

## Fallback

If variable injection was missed, you can still set API base by URL once:

- `/static/app.html?api_base=https://legal-ai-agent.coach.io.vn`
