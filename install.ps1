$ErrorActionPreference = "Stop"

function Run-Native {
    param(
        [string]$Program,
        [string[]]$Arguments
    )

    & $Program @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "$Program failed: $LASTEXITCODE"
    }
}

Clear-Host

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "      TERMGPT INSTALLER v0.8.4      " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$root = $PSScriptRoot
Set-Location $root

Write-Host "[1/6] Checking requirements..." -ForegroundColor Yellow

foreach ($command in @("py", "node", "npm.cmd", "git")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Missing dependency: $command"
    }
}

Run-Native "py" @("-3", "--version")
Run-Native "node" @("--version")

Write-Host "[2/6] Creating Python environment..." -ForegroundColor Yellow

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Run-Native "py" @("-3", "-m", "venv", ".venv")
}

$python = Join-Path $root ".venv\Scripts\python.exe"

Write-Host "[3/6] Installing Python dependencies..." -ForegroundColor Yellow

Run-Native $python @("-m", "pip", "install", "--upgrade", "pip")
Run-Native $python @("-m", "pip", "install", "-r", "requirements.txt")

Write-Host "[4/6] Installing OpenAI SDK..." -ForegroundColor Yellow

if (-not (Test-Path "sdk\.git")) {
    Run-Native "git" @(
        "clone",
        "https://github.com/openai/sign-in-with-chatgpt-devkit.git",
        "sdk"
    )
}


$sdkCommit = "0a36fefeb913055c8c7a1a29b63d82b96b2e841a"

Run-Native "git" @("-C", "sdk", "checkout", "--detach", $sdkCommit)

Push-Location sdk

try {
    Run-Native "npm.cmd" @("ci")
    Run-Native "npm.cmd" @("audit", "fix")
    Run-Native "npm.cmd" @("audit")
    Run-Native "npm.cmd" @("run", "build", "-w", "@siwc/local")
}
finally {
    Pop-Location
}

Write-Host "[5/6] Configuring global CLI..." -ForegroundColor Yellow

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

if (($userPath -split ";") -notcontains $root) {
    $newPath = (@($userPath, $root) | Where-Object { $_ }) -join ";"

    [Environment]::SetEnvironmentVariable(
        "Path",
        $newPath,
        "User"
    )
}

if (($env:Path -split ";") -notcontains $root) {
    $env:Path += ";$root"
}

Write-Host "[6/6] Checking installation..." -ForegroundColor Yellow

Run-Native $python @(
    "-m", "py_compile",
    "main.py",
    "agent.py",
    "access.py",
    "ui.py",
    "tools/engine.py"
)

Write-Host ""
Write-Host "TERMGPT installed successfully!" -ForegroundColor Green
Write-Host "Run: termgpt" -ForegroundColor Cyan
Write-Host "Then use /login to connect ChatGPT."
