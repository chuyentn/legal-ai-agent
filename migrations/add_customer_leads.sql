-- Add customer leads table for superadmin conversion pipeline

CREATE TABLE IF NOT EXISTS customer_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source VARCHAR(50) NOT NULL DEFAULT 'contact_form',
    full_name VARCHAR(120) NOT NULL,
    company_name VARCHAR(180) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(40),
    ai_level VARCHAR(80),
    needs JSONB DEFAULT '[]'::jsonb,
    detail TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'new',
    assigned_to UUID,
    note TEXT,
    converted_company_id UUID,
    converted_user_id UUID,
    converted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_customer_leads_email ON customer_leads(email);
CREATE INDEX IF NOT EXISTS idx_customer_leads_status_created ON customer_leads(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_customer_leads_source_created ON customer_leads(source, created_at DESC);
