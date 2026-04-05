#!/usr/bin/env python3
"""Create core documents/contracts tables and enums if missing."""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("SUPABASE_DB_HOST", "localhost")
is_pooler = "pooler" in host.lower()

conn = psycopg2.connect(
    host=host,
    port=6543 if is_pooler else 5432,
    dbname="postgres",
    user="postgres.cjkrsnqdsfucngmrsnpm" if is_pooler else "postgres",
    password=os.getenv("SUPABASE_DB_PASSWORD", ""),
    sslmode="require",
)

cur = conn.cursor()

ENUMS = {
    "doc_status": "('uploaded', 'processing', 'analyzed', 'error')",
    "doc_type": "('hop_dong_lao_dong', 'hop_dong_thuong_mai', 'hop_dong_dich_vu', 'noi_quy', 'quy_che', 'quyet_dinh', 'cong_van', 'bien_ban', 'bao_cao', 'phu_luc', 'other')",
}

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS contracts (
        id UUID DEFAULT gen_random_uuid() NOT NULL,
        company_id UUID NOT NULL,
        uploaded_by UUID,
        name VARCHAR(500) NOT NULL,
        contract_type VARCHAR(100),
        parties JSONB DEFAULT '[]'::jsonb,
        start_date DATE,
        end_date DATE,
        file_path TEXT,
        file_type VARCHAR(50),
        extracted_text TEXT,
        status VARCHAR(50) DEFAULT 'active'::character varying,
        review_result JSONB,
        notes TEXT,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now(),
        folder_id UUID,
        deleted_at TIMESTAMPTZ,
        tags TEXT[] DEFAULT '{}'::text[],
        content TEXT,
        PRIMARY KEY (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id UUID DEFAULT gen_random_uuid() NOT NULL,
        company_id UUID NOT NULL,
        uploaded_by UUID,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        mime_type TEXT,
        doc_type doc_type,
        status doc_status DEFAULT 'uploaded'::doc_status,
        extracted_text TEXT,
        page_count INTEGER,
        analysis JSONB,
        risk_score INTEGER,
        issues_count INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT now(),
        analyzed_at TIMESTAMPTZ,
        folder_id UUID,
        deleted_at TIMESTAMPTZ,
        tags TEXT[] DEFAULT '{}'::text[],
        PRIMARY KEY (id)
    );
    """,
]

print("🧱 Ensuring enums...")
for name, values in ENUMS.items():
    cur.execute("SELECT 1 FROM pg_type WHERE typname = %s", (name,))
    if cur.fetchone():
        print(f"  ℹ️  {name} exists")
    else:
        cur.execute(f"CREATE TYPE {name} AS ENUM {values}")
        print(f"  ✅ {name} created")

print("\n🏗️  Ensuring tables...")
for ddl in TABLES:
    cur.execute(ddl)

conn.commit()
cur.close()
conn.close()
print("✅ Core tables ready")
