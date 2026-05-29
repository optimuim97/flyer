# Softara — Demarrage backend (Flask :6060) + frontend (Vite :3000)
# Usage : .\run-server.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host ""
Write-Host "==> Softara : demarrage des serveurs" -ForegroundColor Cyan
Write-Host "    Backend  : http://localhost:6060" -ForegroundColor DarkGray
Write-Host "    Frontend : http://localhost:3000" -ForegroundColor DarkGray
Write-Host ""

# --- Backend : venv + dependances ---
$backend = Join-Path $root "backend"
$venv = Join-Path $backend ".venv"
if (-not (Test-Path $venv)) {
    Write-Host "==> Creation de l'environnement Python..." -ForegroundColor Yellow
    python -m venv $venv
}
$python = Join-Path $venv "Scripts\python.exe"
$pip    = Join-Path $venv "Scripts\pip.exe"

Write-Host "==> Verification des dependances Python..." -ForegroundColor Yellow
& $pip install -q -r (Join-Path $backend "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip install a echoue" -ForegroundColor Red
    exit 1
}

# --- Seed de la base ---
Write-Host "==> Seed (project_types + features)..." -ForegroundColor Yellow
Push-Location $backend
& $python "seed.py"
$seedOk = ($LASTEXITCODE -eq 0)
Pop-Location
if (-not $seedOk) {
    Write-Host "Seed a echoue - l'API ne renverra pas de donnees." -ForegroundColor Red
    exit 1
}

# --- Frontend : node_modules ---
$frontend = Join-Path $root "frontend"
if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    Write-Host "==> Installation des dependances Node..." -ForegroundColor Yellow
    Push-Location $frontend
    npm install
    Pop-Location
}

# --- Lancement parallele dans deux fenetres separees ---
$env:PYTHONUNBUFFERED = "1"

$appPath = Join-Path $backend "app.py"
$backendCmd = "& `"$python`" `"$appPath`""

Write-Host ""
Write-Host "==> Lancement du backend (nouvelle fenetre)" -ForegroundColor Green
$backendProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoExit", "-Command", $backendCmd `
    -WorkingDirectory $backend -PassThru

Start-Sleep -Seconds 2

Write-Host "==> Lancement du frontend (nouvelle fenetre)" -ForegroundColor Green
$frontendProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoExit", "-Command", "npm run dev" `
    -WorkingDirectory $frontend -PassThru

Write-Host ""
Write-Host "Backend  PID : $($backendProc.Id)" -ForegroundColor DarkGray
Write-Host "Frontend PID : $($frontendProc.Id)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Les serveurs tournent dans deux fenetres PowerShell separees." -ForegroundColor Cyan
Write-Host "Fermez-les avec Ctrl+C dans chaque fenetre." -ForegroundColor DarkGray
