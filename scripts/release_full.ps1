param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [string]$Branch = "production-custom",

    [string]$LocalBaseUrl = "http://localhost:8080",

    [string]$ProdBaseUrl = "https://legal-ai-agent.coach.io.vn",

    [string]$TokenEnvVar = "GH_TOKEN",

    [string]$CommitMessage = "chore(deploy): release update",

    [switch]$SkipLocalQA
)

$ErrorActionPreference = "Stop"

if (-not $SkipLocalQA) {
    powershell -ExecutionPolicy Bypass -File ".\scripts\qa_local.ps1" -BaseUrl $LocalBaseUrl
    if ($LASTEXITCODE -ne 0) {
        throw "Local QA failed. Stop release."
    }
}

powershell -ExecutionPolicy Bypass -File ".\scripts\push_github_with_token.ps1" -Repo $Repo -Branch $Branch -TokenEnvVar $TokenEnvVar -CommitMessage $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "GitHub push failed."
}

Write-Host "Now trigger deploy on your host from branch: $Branch"
Write-Host "After deploy, run:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\qa_post_sync.ps1 -BaseUrl \"$ProdBaseUrl\""
