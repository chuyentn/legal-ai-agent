"""Supabase client initialization."""

import os
from functools import lru_cache

from supabase import create_client, Client


@lru_cache()
def get_supabase() -> Client:
    """Get Supabase client (singleton)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")  # Service role for backend
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    
    return create_client(url, key)


def get_supabase_anon() -> Client:
    """Get Supabase client with anon key (for user-context operations)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
    
    return create_client(url, key)
