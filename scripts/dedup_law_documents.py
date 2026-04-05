#!/usr/bin/env python3
"""Remove duplicate law_documents by law_number."""

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

print("🔎 Finding duplicates...")
cur.execute("""
    SELECT COUNT(*) FROM (
        SELECT law_number, COUNT(*) AS c
        FROM law_documents
        GROUP BY law_number
        HAVING COUNT(*) > 1
    ) t
""")
dup_count = cur.fetchone()[0]
print(f"Duplicate law_number groups: {dup_count}")

print("🧹 Removing duplicates (keep newest by created_at)...")
cur.execute("""
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY law_number
                   ORDER BY created_at DESC NULLS LAST
               ) AS rn
        FROM law_documents
    )
    DELETE FROM law_documents d
    USING ranked r
    WHERE d.id = r.id AND r.rn > 1
""")
conn.commit()

cur.execute("SELECT COUNT(*) FROM law_documents")
remaining = cur.fetchone()[0]
print(f"Remaining law_documents: {remaining}")

cur.close()
conn.close()
print("✅ Dedup complete")
