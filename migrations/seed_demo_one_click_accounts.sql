-- Seed demo one-click accounts for Legal AI app login
-- Shared password for demo UX: Demolegal@123

CREATE EXTENSION IF NOT EXISTS pgcrypto;

BEGIN;

-- 1) Ensure demo company exists and is full access
INSERT INTO companies (
    name,
    slug,
    plan,
    monthly_quota,
    used_quota
)
VALUES (
    'Coach Legal Demo',
    'coach-legal-demo',
    'enterprise'::plan_type,
    100000,
    0
)
ON CONFLICT (slug) DO UPDATE
SET plan = 'enterprise'::plan_type,
    monthly_quota = 100000,
    used_quota = 0;

-- 2) Seed CEO Admin demo account
WITH c AS (
    SELECT id FROM companies WHERE slug = 'coach-legal-demo' LIMIT 1
)
INSERT INTO users (
    company_id,
    role,
    full_name,
    email,
    password_hash,
    is_active,
    preferences,
    user_settings
)
SELECT
    c.id,
    'owner'::user_role,
    'CEO Admin Demo',
    'adminlegal@coach.io.vn',
    crypt('Demolegal@123', gen_salt('bf', 10)),
    true,
    '{}'::jsonb,
    '{}'::jsonb
FROM c
ON CONFLICT (email) DO UPDATE
SET company_id = EXCLUDED.company_id,
    role = 'owner'::user_role,
    full_name = EXCLUDED.full_name,
    password_hash = EXCLUDED.password_hash,
    is_active = true;

-- 3) Seed Lawyer demo account
WITH c AS (
    SELECT id FROM companies WHERE slug = 'coach-legal-demo' LIMIT 1
)
INSERT INTO users (
    company_id,
    role,
    full_name,
    email,
    password_hash,
    is_active,
    preferences,
    user_settings
)
SELECT
    c.id,
    'admin'::user_role,
    'Chuyen gia Luat su Demo',
    'luatsu@coach.io.vn',
    crypt('Demolegal@123', gen_salt('bf', 10)),
    true,
    '{}'::jsonb,
    '{}'::jsonb
FROM c
ON CONFLICT (email) DO UPDATE
SET company_id = EXCLUDED.company_id,
    role = 'admin'::user_role,
    full_name = EXCLUDED.full_name,
    password_hash = EXCLUDED.password_hash,
    is_active = true;

COMMIT;

-- 4) Verify output
SELECT
    u.email,
    u.role,
    u.is_active AS user_active,
    c.name AS company_name,
    c.plan,
    c.monthly_quota,
    c.used_quota
FROM users u
LEFT JOIN companies c ON c.id = u.company_id
WHERE lower(u.email) IN ('adminlegal@coach.io.vn', 'luatsu@coach.io.vn')
ORDER BY u.email;
