-- Legal AI Agent — Database Init
-- Auto-runs on first Docker Compose startup
-- Creates extensions and base schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Base tables are auto-created by the application on startup
-- This file only handles extensions that need superuser privileges
