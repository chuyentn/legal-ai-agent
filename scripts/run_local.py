#!/usr/bin/env python3
"""Run local FastAPI app with DATABASE_URL from .env."""

import os
import sys
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Ensure repo root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

host = os.getenv("SUPABASE_DB_HOST", "localhost")
password = os.getenv("SUPABASE_DB_PASSWORD", "")
port = 6543 if "pooler" in host.lower() else 5432
user = "postgres.cjkrsnqdsfucngmrsnpm" if "pooler" in host.lower() else "postgres"

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        f"postgresql://{user}:{password}@{host}:{port}/postgres"
    )

uvicorn.run("src.api.main:app", host="0.0.0.0", port=8080, reload=False)
