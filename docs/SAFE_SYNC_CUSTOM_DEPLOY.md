# Safe Upstream Sync for Custom Domain and Private Data

Use this workflow to keep receiving upstream updates without breaking your own domain, deployment settings, and private data.

## Goal

- Receive new code from upstream regularly
- Keep your custom production domain unchanged
- Keep private database and secrets untouched

## Branch model (required)

Create and keep these long-lived branches:

1. `main`
- Mirror upstream as closely as possible
- Avoid custom deploy edits here

2. `production-custom`
- Your deploy branch
- Contains domain/config overrides and custom docs
- Deploy only from this branch

## One-time setup

```bash
git remote add upstream https://github.com/<upstream-owner>/<upstream-repo>.git
git fetch upstream

git checkout main
git merge upstream/main

git checkout -b production-custom
```

## Recurring update flow

Run this every time upstream has updates:

```bash
git fetch upstream

git checkout main
git merge upstream/main

git push origin main

git checkout production-custom
git rebase main
# resolve conflicts if any
git push origin production-custom --force-with-lease
```

## Files to treat as deployment-owned (your side wins)

When conflicts happen, keep your version for these areas:

- custom domain references in static pages
- runtime API base wiring in static pages
- environment templates and deploy docs
- host-specific infra files (if customized)

Current files likely to be deployment-owned in this repo:

- `static/app.html`
- `static/admin.html`
- `static/platform-admin.html`
- `.env.example`
- `docs/CLOUDFLARE_PAGES_DEPLOY.md`

## Data and secret protection rules

1. Never commit real secrets
- Keep `.env` out of git (already ignored)
- Use host environment variables for production secrets

2. Never run destructive DB migration blindly
- Review SQL migrations before applying
- Apply to staging first, then production

3. Always backup before upgrade
- Export DB snapshot before rebase/deploy
- Keep at least one known-good restore point

## QA gate after every sync/deploy

Run these checks in order:

1. Health endpoint
- `GET /v1/health` returns `status: ok` and `database: ok`

2. Frontend reachability
- `/`
- `/static/app.html`
- `/static/admin.html`

3. Public API
- `GET /v1/pricing` returns valid JSON

4. Auth path
- login/register works from app UI

5. One write test in DB-backed feature
- create one document or contract and verify readback

If check #1 fails (`database: error`), stop rollout and fix DB connection/env first.

## Recommended release procedure

1. Deploy to staging from `production-custom`
2. Run QA gate
3. Deploy to production
4. Smoke test again
5. Keep previous release available for rollback

## Fast conflict resolution tip

If a conflict is only in deployment-owned files:

- Keep `production-custom` version for those files
- Keep upstream for core logic and new features
- Re-run QA gate

This gives you upstream features while preserving your domain and private platform setup.
