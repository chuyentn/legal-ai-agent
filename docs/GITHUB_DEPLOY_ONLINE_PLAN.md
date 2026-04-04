# GitHub Push + Online Deploy Plan

Use this plan to publish safely with your custom domain and private data preserved.

## Branch policy

- `main`: upstream sync branch
- `production-custom`: deploy branch (your domain/config)

Deploy only from `production-custom`.

## A. One-time setup

1. Add upstream remote:

```bash
git remote add upstream https://github.com/<upstream-owner>/<upstream-repo>.git
git fetch upstream
```

2. Create deploy branch from current working state:

```bash
git checkout -b production-custom
```

3. Copy `.env.production.example` to host environment variables (never commit real values).

## B. Recurring update from upstream

```bash
git fetch upstream

git checkout main
git merge upstream/main
git push origin main

git checkout production-custom
git rebase main
# resolve conflicts if needed
git push origin production-custom --force-with-lease
```

Conflict rule:

- Keep your version for deployment-owned files:
  - `static/app.html`
  - `static/admin.html`
  - `static/platform-admin.html`
  - `.env.example`
  - `.env.production.example`
  - `docs/CLOUDFLARE_PAGES_DEPLOY.md`

## C. GitHub push (release)

```bash
git checkout production-custom
git add .
git commit -m "chore(deploy): update production config and release docs"
git push origin production-custom
```

Token-based safe push (recommended):

1. Set token in current shell:

```powershell
$env:GH_TOKEN="your_github_pat"
```

2. Push using helper script (token not stored in remote URL):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\push_github_with_token.ps1 -Repo "<owner>/<repo>" -Branch "production-custom"
```

One-command local QA + push workflow:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_full.ps1 -Repo "<owner>/<repo>" -Branch "production-custom"
```

## D. Online deploy

1. Configure host to deploy from branch: `production-custom`.
2. Set environment variables from `.env.production.example`.
3. Redeploy service.

## E. Mandatory QA gate after deploy

Run from local machine:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\qa_post_sync.ps1 -BaseUrl "https://legal-ai-agent.coach.io.vn"
```

Pass criteria:

- Health endpoint returns `status: ok`
- Health `database: ok`
- Landing/App/Admin/Pricing checks pass

If health shows `database: error`, stop release and fix DB env first.

## F. Data source readiness checklist

Before go-live, confirm:

1. DB connection is healthy (`/v1/health`).
2. Migrations applied successfully.
3. Legal library tables contain data (laws/chunks/indexes).
4. At least one search query returns expected legal results.

## G. Rollback plan

1. Keep previous deploy artifact/version.
2. If QA fails in production, rollback immediately.
3. Restore DB snapshot only if migration caused corruption.
