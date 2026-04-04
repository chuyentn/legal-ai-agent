param(
    [string]$BaseUrl = "https://legal-ai-agent.coach.io.vn"
)

$ErrorActionPreference = "Stop"

Write-Host "Running post-sync QA against: $BaseUrl"

$checks = @(
    @{ Name = "Health"; Url = "$BaseUrl/v1/health" },
    @{ Name = "Landing"; Url = "$BaseUrl/" },
    @{ Name = "App"; Url = "$BaseUrl/static/app.html" },
    @{ Name = "Admin"; Url = "$BaseUrl/static/admin.html" },
    @{ Name = "Pricing"; Url = "$BaseUrl/v1/pricing" }
)

$failed = @()

foreach ($check in $checks) {
    try {
        $response = Invoke-WebRequest -Uri $check.Url -Method GET -TimeoutSec 20
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Host "[PASS] $($check.Name): $($response.StatusCode)"
        }
        else {
            Write-Host "[FAIL] $($check.Name): HTTP $($response.StatusCode)"
            $failed += $check.Name
        }
    }
    catch {
        Write-Host "[FAIL] $($check.Name): $($_.Exception.Message)"
        $failed += $check.Name
    }
}

# Parse health details if available
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/v1/health" -Method GET -TimeoutSec 20
    Write-Host "Health status: $($health.status)"
    Write-Host "Database status: $($health.database)"

    if ($health.database -ne "ok") {
        Write-Host "[WARN] Database is not healthy. Fix DB env/connection before rollout."
        if (-not ($failed -contains "Health")) {
            $failed += "Health(database)"
        }
    }
}
catch {
    Write-Host "[WARN] Could not parse health JSON: $($_.Exception.Message)"
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "QA FAILED on: $($failed -join ', ')"
    exit 1
}

Write-Host ""
Write-Host "QA PASSED."
exit 0
