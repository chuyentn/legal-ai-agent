#!/usr/bin/env python3
"""Check embedding coverage for law_chunks."""

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
cur.execute("SELECT COUNT(*) FROM law_chunks")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM law_chunks WHERE embedding IS NOT NULL")
filled = cur.fetchone()[0]
print(f"law_chunks total: {total}")
print(f"embeddings filled: {filled}")

cur.close()
conn.close()
