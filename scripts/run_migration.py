import os
#!/usr/bin/env python3
"""
Run migration_auth.sql on Supabase database
"""
import psycopg2
import sys
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

def _normalize_db_host(raw_host: str) -> str:
    host = (raw_host or "").strip()
    if not host:
        return "localhost"
    if "://" in host:
        parsed = urlparse(host)
        if parsed.hostname:
            return parsed.hostname
    if "/" in host:
        return host.split("/")[0]
    return host


def _build_database_url_with_ssl(url: str, sslmode: str) -> str:
    parsed = urlparse(url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query_params and sslmode:
        query_params["sslmode"] = sslmode
    return urlunparse(parsed._replace(query=urlencode(query_params)))


def _build_db_connect_args():
    sslmode = os.getenv("DB_SSL_MODE", "require")
    database_url = (os.getenv("DATABASE_URL") or "").strip()
    if database_url:
        return {
            "dsn": _build_database_url_with_ssl(database_url, sslmode),
            "kwargs": {},
        }

    return {
        "dsn": None,
        "kwargs": {
            "host": _normalize_db_host(os.getenv("SUPABASE_DB_HOST", "localhost")),
            "port": int(os.getenv("SUPABASE_DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
            "sslmode": sslmode,
        },
    }


DB_CONNECT = _build_db_connect_args()

def run_migration():
    try:
        # Read migration file
        with open("scripts/migration_auth.sql", "r") as f:
            sql = f.read()
        
        # Connect and execute
        print("Connecting to database...")
        if DB_CONNECT["dsn"]:
            conn = psycopg2.connect(DB_CONNECT["dsn"], **DB_CONNECT["kwargs"])
        else:
            conn = psycopg2.connect(**DB_CONNECT["kwargs"])
        cur = conn.cursor()
        
        print("Running migration...")
        cur.execute(sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name IN ('auth_id', 'password_hash', 'user_settings')")
        results = cur.fetchall()
        print(f"✅ Verified columns added to users table: {[r[0] for r in results]}")
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'company_invites'")
        if cur.fetchone():
            print("✅ Verified company_invites table created")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
