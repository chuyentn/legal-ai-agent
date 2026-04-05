# Victor's One-Command Startup Script
# Run this in PowerShell to start HuggingFace data integration

param(
    [switch]$test,
    [switch]$full,
    [switch]$help
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$text)
    Write-Host ""
    Write-Host "╔" + ("═" * 60) + "╗" -ForegroundColor Cyan
    Write-Host "║ $text" + (" " * (58 - $text.Length)) + "║" -ForegroundColor Cyan
    Write-Host "╚" + ("═" * 60) + "╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$text)
    Write-Host "✅ $text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$text)
    Write-Host "❌ $text" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$text)
    Write-Host "⚠️  $text" -ForegroundColor Yellow
}

function Show-Help {
    Write-Host @"
Victor's HuggingFace Data Integration Script

USAGE:
  .\victor_start.ps1 -test    # TEST mode: 500 rows each dataset (5 min)
  .\victor_start.ps1 -full    # FULL mode: all datasets (1-2 hours)

STEPS:
  1. Verify Python + dependencies
  2. Setup git branch
  3. Run data pipeline
  4. Monitor progress
  5. Commit and push

EXAMPLE:
  .\victor_start.ps1 -test   # Start with test
  [wait 5 min]
  .\victor_start.ps1 -full   # If test OK, run full load

"@
}

if ($help) {
    Show-Help
    exit 0
}

if (-not $test -and -not $full) {
    Write-Warning-Custom "No mode specified. Use -test or -full"
    Write-Host "Example: .\victor_start.ps1 -test"
    Write-Host ""
    Show-Help
    exit 1
}

# ============= STEP 0: VERIFY SETUP =============

Write-Header "🔍 STEP 0: VERIFYING SETUP"

# Check Python
Write-Host "Checking Python..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Python found: $pythonVersion"
} else {
    Write-Error-Custom "Python not found! Activate venv first."
    exit 1
}

# Check dependencies
Write-Host "Checking dependencies..."
$datasets_check = pip show datasets 2>$null | Select-String "Version"
$bs4_check = pip show beautifulsoup4 2>$null | Select-String "Version"

if ($datasets_check -and $bs4_check) {
    Write-Success "Dependencies installed checkmark"
    Write-Host "  datasets, beautifulsoup4 OK"
} else {
    Write-Warning-Custom "Some dependencies missing. Installing..."
    pip install -r requirements.txt
}

# Check .env
Write-Host "Checking database connection..."
$envCheck = python -c "
import os
from dotenv import load_dotenv
load_dotenv()
host = os.getenv('SUPABASE_DB_HOST')
pwd = os.getenv('SUPABASE_DB_PASSWORD')
if not host or not pwd:
    print('ERROR: Missing SUPABASE_DB_HOST or SUPABASE_DB_PASSWORD')
    exit(1)
print('OK')
" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "Database connection configured ✓"
} else {
    Write-Error-Custom "Database connection error: $envCheck"
    Write-Warning-Custom "Make sure .env has SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD"
    exit 1
}

# ============= STEP 1: GIT SETUP =============

Write-Header "🌿 STEP 1: GIT BRANCH SETUP"

Write-Host "Current branch: $(git branch --show-current)"
Write-Host "Creating feature branch..."

git checkout main 2>&1 | Out-Null
git pull origin main 2>&1 | Out-Null

$branch = "feature/hf-data-integration"
$branchExists = git rev-parse --verify $branch 2>$null
if ($branchExists) {
    Write-Warning-Custom "Branch $branch already exists. Checking out..."
    git checkout $branch
} else {
    Write-Host "Creating new branch..."
    git checkout -b $branch
}

Write-Success "Branch ready: $branch"

# ============= STEP 2: RUN PIPELINE =============

$mode = if ($test) { "TEST" } else { "FULL" }
Write-Header "🚀 STEP 2: STARTING PIPELINE - $mode MODE"

if ($test) {
    Write-Host "TEST mode: 500 rows per dataset (est. 5 minutes)"
    Write-Host ""
    python scripts/load_hf_datasets.py --test
} else {
    Write-Host "FULL mode: All datasets (est. 45-90 minutes)"
    Write-Host ""
    Write-Warning-Custom "This will run in background. You can minimize this window."
    Write-Host ""
    python scripts/load_hf_datasets.py --full
}

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Pipeline failed!"
    exit 1
}

Write-Success "Pipeline completed!"

# ============= STEP 3: VERIFY DATA =============

Write-Header "STEP 3: VERIFYING DATA"

$stats = python -c @"
import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('SUPABASE_DB_HOST'), port=5432,
    dbname='postgres', user='postgres',
    password=os.getenv('SUPABASE_DB_PASSWORD'), sslmode='require'
)
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM law_documents')
total_docs = cur.fetchone()[0]

cur.execute(\"SELECT COUNT(*) FROM law_documents WHERE source_site = 'huggingface'\")
hf_docs = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM law_chunks')
total_chunks = cur.fetchone()[0]

print('Total documents: ' + str(total_docs))
print('HuggingFace docs: ' + str(hf_docs))
print('Total chunks: ' + str(total_chunks))

conn.close()
"@ 2>&1

Write-Host $stats

# ============= STEP 4: GIT COMMIT =============

Write-Header "GIT COMMIT AND PUSH"

git add requirements.txt scripts/load_hf_datasets.py 2>&1 | Out-Null
git commit -m "feat: HuggingFace datasets integration - $mode load" 2>&1 | Out-Null
$push = git push origin $branch 2>&1

Write-Success "Committed and pushed to $branch"

# ============= FINAL STATUS =============

Write-Header "COMPLETE"

if ($test) {
    Write-Host "TEST mode complete! OK"
    Write-Host "Next: Run with -full flag when ready"
} else {
    Write-Host "FULL load complete! OK"
    Write-Host "Next: Notify Lucky to run embeddings"
}

Write-Host ""
Write-Host "Status:"
Write-Host "  Branch: $branch"
Write-Host "  Status: Clean"
Write-Host ""

