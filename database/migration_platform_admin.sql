-- ============================================
-- Platform Admin Database Schema
-- Migration for platform super admin features
-- ============================================

-- Platform settings table
CREATE TABLE IF NOT EXISTS platform_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Insert default settings
INSERT INTO platform_settings (key, value) VALUES
    ('general', '{"registration_enabled": true, "require_email_verification": false, "maintenance_mode": false, "maintenance_message": ""}'),
    ('limits', '{"max_file_size_mb": 50, "max_queries_per_day_free": 10, "max_contracts_free": 1, "allowed_file_types": [".pdf", ".doc", ".docx", ".txt"]}'),
    ('llm', '{"default_provider": "anthropic", "default_model": "claude-sonnet-4-20250514"}'),
    ('features', '{"contract_review": true, "crawler": true, "templates": true, "multi_llm": true, "api_access": true}')
ON CONFLICT (key) DO NOTHING;

-- Platform audit log table
CREATE TABLE IF NOT EXISTS platform_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50), -- 'company', 'user', 'setting', 'system'
    target_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_platform_logs_created ON platform_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_platform_logs_action ON platform_logs(action);
CREATE INDEX IF NOT EXISTS idx_platform_logs_user ON platform_logs(user_id);

-- LLM usage tracking table
CREATE TABLE IF NOT EXISTS llm_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    user_id UUID REFERENCES users(id),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,6) DEFAULT 0,
    request_type VARCHAR(50), -- 'chat', 'review', 'generate', 'draft'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_usage_company ON llm_usage(company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_usage_daily ON llm_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_usage_provider ON llm_usage(provider);

-- Add is_active column to companies table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='is_active') THEN
        ALTER TABLE companies ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
END $$;

-- Grant permissions (adjust based on your user setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Migration complete
-- Platform Admin ready to use!
