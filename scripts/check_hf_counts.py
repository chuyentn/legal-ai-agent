#!/usr/bin/env python3
"""Print counts for HuggingFace-loaded data."""

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
cur.execute("SELECT COUNT(*) FROM law_documents")
total_docs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM law_documents WHERE source_site = 'huggingface'")
hf_docs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM law_chunks")
chunks = cur.fetchone()[0]

print(f"law_documents: {total_docs}")
print(f"hf_docs: {hf_docs}")
print(f"law_chunks: {chunks}")

cur.close()
conn.close()
