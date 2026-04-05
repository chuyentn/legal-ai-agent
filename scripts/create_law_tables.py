#!/usr/bin/env python3
"""
Create missing law_* tables in Supabase database.
Extracts and executes law table definitions from database/init.sql
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-1-ap-south-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_DB_PORT', 6543))
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres.cjkrsnqdsfucngmrsnpm')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', 'LegalAI2026Strong!')

# SQL statements to create enums and tables
CREATE_ENUMS = [
    "law_type",
    "law_status"
]

ENUM_DEFINITIONS = {
    "law_type": "('hien_phap', 'bo_luat', 'luat', 'nghi_dinh', 'thong_tu', 'quyet_dinh', 'nghi_quyet', 'cong_van', 'other')",
    "law_status": "('active', 'expired', 'amended', 'repealed', 'pending')"
}

CREATE_TABLES = """
-- Create law_documents table
CREATE TABLE IF NOT EXISTS law_documents (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    title TEXT NOT NULL,
    law_number TEXT NOT NULL,
    law_type law_type NOT NULL,
    issuer TEXT NOT NULL,
    signer TEXT,
    issued_date DATE,
    effective_date DATE,
    expiry_date DATE,
    status law_status DEFAULT 'active'::law_status,
    domains TEXT[] NOT NULL,
    replaces TEXT[],
    amended_by TEXT[],
    full_text TEXT,
    summary TEXT,
    table_of_contents JSONB,
    source_url TEXT,
    source_site TEXT,
    article_count INTEGER,
    word_count INTEGER,
    crawled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    tsv TSVECTOR,
    PRIMARY KEY (id)
);

-- Create law_chunks table
CREATE TABLE IF NOT EXISTS law_chunks (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    law_id UUID NOT NULL,
    chapter TEXT,
    section TEXT,
    article TEXT,
    clause TEXT,
    point TEXT,
    title TEXT,
    content TEXT NOT NULL,
    parent_context TEXT,
    embedding vector,
    domains TEXT[],
    keywords TEXT[],
    created_at TIMESTAMPTZ DEFAULT now(),
    tsv TSVECTOR,
    PRIMARY KEY (id),
    CONSTRAINT fk_law_chunks_law_documents FOREIGN KEY (law_id) REFERENCES law_documents(id) ON DELETE CASCADE
);

-- Create law_relations table
CREATE TABLE IF NOT EXISTS law_relations (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    source_law_id UUID,
    source_article TEXT,
    target_law_id UUID,
    target_article TEXT,
    relation_type TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT fk_law_relations_source FOREIGN KEY (source_law_id) REFERENCES law_documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_law_relations_target FOREIGN KEY (target_law_id) REFERENCES law_documents(id) ON DELETE CASCADE
);
"""

def main():
    try:
        print(f"🔗 Connecting to Supabase database...")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print(f"   User: {DB_USER}")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        print("✅ Connected successfully\n")
        
        # Check if pgvector extension exists
        print("📦 Checking pgvector extension...")
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
        vector_exists = cur.fetchone()[0]
        if vector_exists:
            print("✅ pgvector extension already exists\n")
        else:
            print("📥 Creating pgvector extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✅ pgvector extension created\n")
        
        # Check if law tables already exist
        print("🔍 Checking existing tables...")
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'law_%'
        """)
        existing_tables = [row[0] for row in cur.fetchall()]
        print(f"   Existing law tables: {existing_tables if existing_tables else 'NONE'}\n")
        
        # Create enums (check if they exist first)
        print("📝 Creating enums...")
        for enum_name, enum_values in ENUM_DEFINITIONS.items():
            try:
                cur.execute(f"SELECT 1 FROM pg_type WHERE typname = '{enum_name}'")
                if cur.fetchone():
                    print(f"   ℹ️  {enum_name} already exists (skipped)")
                else:
                    cur.execute(f"CREATE TYPE {enum_name} AS ENUM {enum_values}")
                    conn.commit()
                    print(f"   ✅ {enum_name}")
            except Exception as e:
                print(f"   ❌ Error creating {enum_name}: {e}")
                conn.rollback()
        
        print()
        
        # Create tables
        print("🏗️  Creating tables...")
        for statement in CREATE_TABLES.split(';'):
            if statement.strip():
                try:
                    cur.execute(statement)
                    conn.commit()
                    # Extract table name
                    table_name = statement.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
                    print(f"   ✅ {table_name}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    conn.rollback()

        # Add unique constraint for law_number to prevent duplicates
        print("\n🔐 Ensuring unique constraint on law_documents.law_number...")
        try:
            cur.execute(
                "ALTER TABLE law_documents ADD CONSTRAINT law_documents_law_number_key UNIQUE (law_number)"
            )
            conn.commit()
            print("   ✅ Unique constraint added")
        except Exception as e:
            conn.rollback()
            print(f"   ℹ️  Skipped (already exists or cannot add): {e}")
        
        print()
        
        # Verify tables were created
        print("✔️  Verifying tables...")
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'law_%'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"   Found {len(tables)} law tables: {', '.join(tables)}\n")
        
        # Show table row counts
        print("📊 Table statistics:")
        for table in ['law_documents', 'law_chunks', 'law_relations']:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count:,} rows")
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        print("\n✨ Schema creation complete!")
        print("You can now run: python scripts/load_hf_datasets.py --test")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
