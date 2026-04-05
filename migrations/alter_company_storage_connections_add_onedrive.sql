-- Add OneDrive provider support to company_storage_connections check constraint

DO $$
DECLARE
    existing_check TEXT;
BEGIN
    SELECT conname INTO existing_check
    FROM pg_constraint
    WHERE conrelid = 'company_storage_connections'::regclass
      AND contype = 'c'
      AND pg_get_constraintdef(oid) ILIKE '%provider%';

    IF existing_check IS NOT NULL THEN
        EXECUTE format('ALTER TABLE company_storage_connections DROP CONSTRAINT %I', existing_check);
    END IF;

    ALTER TABLE company_storage_connections
    ADD CONSTRAINT company_storage_connections_provider_check
    CHECK (provider IN ('supabase', 'google_drive', 'onedrive'));
END $$;
