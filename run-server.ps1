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

# --- Frontend : node_modules avec verification de version Node ---
$frontend = Join-Path $root "frontend"

# Vérifier si nvm est disponible
$nvmAvailable = Get-Command "nvm" -ErrorAction SilentlyContinue
if (-not $nvmAvailable) {
    Write-Host "ATTENTION: nvm n'est pas installe. Installation manuelle de Node 22 requise." -ForegroundColor Yellow
    Write-Host "Telechargez Node.js 22 depuis https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Vérifier et forcer la version Node 22
Write-Host "==> Verification de la version Node..." -ForegroundColor Yellow

# Fonction pour obtenir la version Node active
function Get-NodeVersion {
    $version = & node --version 2>$null
    return $version
}

$currentVersion = Get-NodeVersion
Write-Host "Version Node actuelle: $currentVersion" -ForegroundColor Yellow

if ($currentVersion -notmatch "v22") {
    Write-Host "Activation de Node v22..." -ForegroundColor Yellow
    
    # Vérifier si Node 22 est installé
    $installedVersions = & nvm list 2>$null
    if ($installedVersions -notmatch "22\.16\.0") {
        Write-Host "Installation de Node 22.16.0..." -ForegroundColor Yellow
        & nvm install 22.16.0
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Tentative d'installation de Node 22..." -ForegroundColor Yellow
            & nvm install 22
        }
    }
    
    # Activer Node 22
    & nvm use 22.16.0 2>$null
    if ($LASTEXITCODE -ne 0) {
        & nvm use 22
    }
    
    # FORCER l'actualisation de l'environnement PowerShell en rechargeant le PATH
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = $machinePath + ";" + $userPath
    
    # Vérifier la version après activation
    $newVersion = Get-NodeVersion
    Write-Host "Nouvelle version Node: $newVersion" -ForegroundColor Yellow
    
    if ($newVersion -notmatch "v22") {
        Write-Host "ERREUR: Impossible d'activer Node 22. Version actuelle: $newVersion" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUTIONS POSSIBLES:" -ForegroundColor Yellow
        Write-Host "1. Ouvrez une NOUVELLE fenetre PowerShell en tant qu'Administrateur" -ForegroundColor White
        Write-Host "2. Executez: nvm use 22.16.0" -ForegroundColor White
        Write-Host "3. Verifiez: node --version" -ForegroundColor White
        Write-Host "4. Puis relancez ce script" -ForegroundColor White
        Write-Host ""
        exit 1
    }
    Write-Host "Node version $newVersion activee avec succes!" -ForegroundColor Green
} else {
    Write-Host "Node version $currentVersion deja activee" -ForegroundColor Green
}

# Installation des dépendances Node
if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    Write-Host "==> Installation des dependances Node..." -ForegroundColor Yellow
    Push-Location $frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "npm install a echoue" -ForegroundColor Red
        Pop-Location
        exit 1
    }
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

# Commande robuste pour forcer Node 22 dans la nouvelle fenetre
$frontendCmd = @"
Write-Host 'Demarrage du frontend avec Node 22...' -ForegroundColor Cyan
# Forcer l'utilisation de Node 22
nvm use 22.16.0 2>`$null
if (`$LASTEXITCODE -ne 0) { nvm use 22 }
# Recharger le PATH
`$machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
`$userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
`$env:Path = `$machinePath + ';' + `$userPath
Write-Host "Node version: `$(node --version)" -ForegroundColor Green
npm run dev
"@

$frontendProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoExit", "-Command", $frontendCmd `
    -WorkingDirectory $frontend -PassThru

Write-Host ""
Write-Host "Backend  PID : $($backendProc.Id)" -ForegroundColor DarkGray
Write-Host "Frontend PID : $($frontendProc.Id)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Les serveurs tournent dans deux fenetres PowerShell separees." -ForegroundColor Cyan
Write-Host "Node 22 est force pour le frontend." -ForegroundColor Cyan
Write-Host "Si vous voyez encore Node 16, fermez cette fenetre et ouvrez-en une NOUVELLE." -ForegroundColor Yellow
Write-Host "Fermez les serveurs avec Ctrl+C dans chaque fenetre." -ForegroundColor DarkGray