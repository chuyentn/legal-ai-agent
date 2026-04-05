#!/usr/bin/env python3
"""Delete HuggingFace-loaded documents and chunks."""

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

print("🧹 Deleting HuggingFace chunks...")
cur.execute("""
    DELETE FROM law_chunks
    WHERE law_id IN (
        SELECT id FROM law_documents WHERE source_site = 'huggingface'
    )
""")

print("🧹 Deleting HuggingFace documents...")
cur.execute("DELETE FROM law_documents WHERE source_site = 'huggingface'")

conn.commit()

cur.execute("SELECT COUNT(*) FROM law_documents")
print(f"Remaining law_documents: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM law_chunks")
print(f"Remaining law_chunks: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("✅ HF data cleared")
