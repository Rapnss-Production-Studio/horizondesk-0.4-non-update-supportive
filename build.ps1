# Horizon Desk - Full Build Script
# Run from project root: .\build.ps1

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  HORIZON DESK BUILD PIPELINE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------------
# STEP 1: Build React Frontend (Vite)
# ------------------------------------------------------------------
Write-Host "[1/3] Building React frontend..." -ForegroundColor Yellow

$guiDir = Join-Path $PROJECT_ROOT "sample-gui"

if (-not (Test-Path (Join-Path $guiDir "node_modules"))) {
    Write-Host "      node_modules not found - running npm install first..." -ForegroundColor Gray
    Push-Location $guiDir
    npm install
    Pop-Location
}

Push-Location $guiDir
npm run build
Pop-Location

$distIndex = Join-Path $guiDir "dist\index.html"
if (-not (Test-Path $distIndex)) {
    Write-Error "React build failed - dist/index.html not found."
    exit 1
}
Write-Host "      React build complete -> sample-gui/dist/" -ForegroundColor Green

# ------------------------------------------------------------------
# STEP 2: Compile Python with PyInstaller
# ------------------------------------------------------------------
Write-Host ""
Write-Host "[2/3] Compiling Python with PyInstaller..." -ForegroundColor Yellow

# Clean previous build
$buildOut = Join-Path $PROJECT_ROOT "dist\HorizonDesk"
if (Test-Path $buildOut) {
    Write-Host "      Cleaning previous build..." -ForegroundColor Gray
    Remove-Item $buildOut -Recurse -Force
}

# Run PyInstaller via python -m (works regardless of PATH)
Push-Location $PROJECT_ROOT
python -m PyInstaller horizon.spec --noconfirm --clean
Pop-Location

$exePath = Join-Path $PROJECT_ROOT "dist\HorizonDesk\HorizonDesk.exe"
if (-not (Test-Path $exePath)) {
    Write-Error "PyInstaller build failed - HorizonDesk.exe not found in dist\HorizonDesk\"
    exit 1
}
Write-Host "      PyInstaller build complete -> dist/HorizonDesk/HorizonDesk.exe" -ForegroundColor Green

# Sanity check: no framework .py files should be in output
$pyFiles = Get-ChildItem (Join-Path $PROJECT_ROOT "dist\HorizonDesk") -Recurse -Filter "*.py" |
Where-Object { $_.FullName -notlike "*\cv2\*" -and $_.FullName -notlike "*\plugins\*" }
if ($pyFiles.Count -gt 0) {
    Write-Warning "WARNING: $($pyFiles.Count) unexpected .py file(s) found in dist output:"
    $pyFiles | ForEach-Object { Write-Warning "  $($_.FullName)" }
}
else {
    Write-Host "      Sanity check passed: 0 framework .py files in output." -ForegroundColor Green
}

# ------------------------------------------------------------------
# STEP 3: Compile Inno Setup Installer
# ------------------------------------------------------------------
Write-Host ""
Write-Host "[3/3] Compiling Inno Setup installer..." -ForegroundColor Yellow

$isccPaths = @(
    "D:\Inno Setup 6\ISCC.exe"
)
$iscc = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    Write-Host "      Inno Setup (ISCC.exe) not found - skipping installer step." -ForegroundColor Red
    Write-Host "      Install from https://jrsoftware.org/isdl.php then re-run." -ForegroundColor Red
}
else {
    & $iscc (Join-Path $PROJECT_ROOT "setup.iss")
    $installer = Join-Path $PROJECT_ROOT "Output\HorizonDesk_v0.2_Setup.exe"
    if (Test-Path $installer) {
        Write-Host "      Installer built -> Output/HorizonDesk_v0.2_Setup.exe" -ForegroundColor Green
    }
    else {
        Write-Warning "Inno Setup ran but installer not found at expected path."
    }
}

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  EXE:       dist\HorizonDesk\HorizonDesk.exe"
Write-Host "  Installer: Output\HorizonDesk_v0.2_Setup.exe"
Write-Host ""
