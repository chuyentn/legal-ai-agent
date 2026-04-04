param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [string]$Branch = "production-custom",

    [string]$CommitMessage = "chore(deploy): release update",

    [string]$TokenEnvVar = "GH_TOKEN"
)

$ErrorActionPreference = "Stop"

$token = [Environment]::GetEnvironmentVariable($TokenEnvVar)
if ([string]::IsNullOrWhiteSpace($token)) {
    throw "Environment variable $TokenEnvVar is empty. Set your GitHub token first."
}

# Init git if missing
$insideRepo = $false
try {
    $result = git rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -eq 0 -and $result -match "true") { $insideRepo = $true }
}
catch {
    $insideRepo = $false
}

if (-not $insideRepo) {
    Write-Host "Initializing git repository..."
    git init -b main | Out-Null
}

# Ensure branch exists
$branchExists = $false
try {
    git show-ref --verify --quiet "refs/heads/$Branch"
    if ($LASTEXITCODE -eq 0) { $branchExists = $true }
}
catch {}

if (-not $branchExists) {
    git checkout -b $Branch | Out-Null
}
else {
    git checkout $Branch | Out-Null
}

# Add or update origin
$originExists = $false
try {
    git remote get-url origin | Out-Null
    if ($LASTEXITCODE -eq 0) { $originExists = $true }
}
catch {}

$originUrl = "https://github.com/$Repo.git"
if ($originExists) {
    git remote set-url origin $originUrl | Out-Null
}
else {
    git remote add origin $originUrl | Out-Null
}

# Commit if there are changes
$hasChanges = $false
$status = git status --porcelain
if (-not [string]::IsNullOrWhiteSpace($status)) {
    $hasChanges = $true
}

if ($hasChanges) {
    git add .
    git commit -m $CommitMessage
}
else {
    Write-Host "No local changes to commit."
}

# Push using ephemeral auth header (token is not stored in remote URL)
$authHeader = "AUTHORIZATION: bearer $token"
git -c "http.https://github.com/.extraheader=$authHeader" push -u origin $Branch

Write-Host "Push completed: $Repo ($Branch)"
