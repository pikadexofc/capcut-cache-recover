# install.ps1 - Safe, transparent installer for CapCut Cache Recover
# Built by PixelPie Media
$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "======================================================" -ForegroundColor DarkYellow
Write-Host "   🎬 CapCut Cache Recover - Quick Setup" -ForegroundColor Yellow
Write-Host "   PixelPie Media • Precision Software Engineering" -ForegroundColor DarkGray
Write-Host "======================================================" -ForegroundColor DarkYellow
Write-Host ""

# Check Python
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonInstalled) {
    Write-Host "[!] Python 3.9+ was not found on your system." -ForegroundColor Red
    Write-Host "    Please install Python from https://www.python.org or Microsoft Store." -ForegroundColor Yellow
    exit 1
}

$targetDir = "$env:LOCALAPPDATA\capcut-cache-recover"
$zipUrl = "https://github.com/pikadexofc/export-capcut-pro-video-free/archive/refs/heads/main.zip"
$zipFile = "$env:TEMP\capcut-cache-recover.zip"

Write-Host "[1/3] Downloading latest release from GitHub..." -ForegroundColor Cyan
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing

Write-Host "[2/3] Extracting files to $targetDir..." -ForegroundColor Cyan
if (Test-Path $targetDir) {
    Remove-Item -Recurse -Force $targetDir
}
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\cc_extract" -Force
Move-Item "$env:TEMP\cc_extract\export-capcut-pro-video-free-main\*" $targetDir -Force
Remove-Item -Recurse -Force "$env:TEMP\cc_extract", $zipFile

Write-Host "[3/3] Setting up desktop drag-and-drop launcher..." -ForegroundColor Cyan
$desktopLauncher = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'CapCut-Cache-Recover.bat')
Copy-Item "$targetDir\CapCut-Cache-Recover.bat" $desktopLauncher -Force

# Editable install for Python
Write-Host "[*] Registering system-wide CLI command..." -ForegroundColor Cyan
& python -m pip install -e $targetDir --quiet

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  ✅ Installation Complete!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host "• Desktop Launcher ready at: $desktopLauncher" -ForegroundColor White
Write-Host "• CLI command active: capcut-cache-recover" -ForegroundColor White
Write-Host "• GUI command active: capcut-gui" -ForegroundColor White
Write-Host ""
Write-Host "Simply drag any unplayable CapCut video cache onto the Desktop icon!" -ForegroundColor Yellow
Write-Host ""
