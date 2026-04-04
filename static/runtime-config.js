/*
 * Runtime config for static deploys (Cloudflare Pages, CDN, etc.)
 *
 * Option 1: keep empty and pass ?api_base=... in URL once.
 * Option 2: generate this file during build from env var LEGAL_API_BASE_URL.
 */
window.LEGAL_API_BASE_URL = window.LEGAL_API_BASE_URL || "";
window.LEGAL_APP_ENV = window.LEGAL_APP_ENV || "production";
