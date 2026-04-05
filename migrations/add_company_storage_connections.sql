-- Per-tenant storage connectors (Google Drive, Supabase)
-- Superadmin can configure storage per company.

CREATE TABLE IF NOT EXISTS company_storage_connections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('supabase', 'google_drive', 'onedrive')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_default BOOLEAN NOT NULL DEFAULT false,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (company_id, provider)
);

CREATE INDEX IF NOT EXISTS idx_company_storage_connections_company
    ON company_storage_connections(company_id);

CREATE INDEX IF NOT EXISTS idx_company_storage_connections_default
    ON company_storage_connections(company_id, is_default)
    WHERE is_active = true;

-- Keep only one default connector per company.
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY company_id
               ORDER BY is_default DESC, updated_at DESC, created_at DESC
           ) AS rn
    FROM company_storage_connections
    WHERE is_active = true
)
UPDATE company_storage_connections c
SET is_default = (ranked.rn = 1)
FROM ranked
WHERE c.id = ranked.id;
