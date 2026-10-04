param(
    [string]$FilePath = "C:\Users\Shanto\Desktop\CapCut-Cache-Recover.exe"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $FilePath)) {
    Write-Host "File not found: $FilePath" -ForegroundColor Red
    exit 1
}

# 1. Look for existing cert in CurrentUser\My
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert -ErrorAction SilentlyContinue | 
        Where-Object { $_.Subject -like '*PixelPie Media*' } | 
        Select-Object -First 1

if (-not $cert) {
    Write-Host "[*] Creating Code Signing Certificate in CurrentUser\My..." -ForegroundColor Cyan
    $cert = New-SelfSignedCertificate -Type CodeSigningCert `
        -Subject "CN=PixelPie Media, O=PixelPie Media, OU=Software Engineering" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(5)
}

Write-Host "[*] Using Certificate: $($cert.Subject) [Thumbprint: $($cert.Thumbprint)]" -ForegroundColor Green

# 2. Sign binary silently
Write-Host "[*] Applying Authenticode digital signature to $FilePath..." -ForegroundColor Cyan
$sig = Set-AuthenticodeSignature -FilePath $FilePath -Certificate $cert

Write-Host ""
Write-Host "=== Signature Verification ===" -ForegroundColor Green
$verify = Get-AuthenticodeSignature $FilePath
Write-Host "Path:   $($verify.Path)" -ForegroundColor White
Write-Host "Status: $($verify.Status)" -ForegroundColor Yellow
Write-Host "Signer: $($verify.SignerCertificate.Subject)" -ForegroundColor White
Write-Host "Thumb:  $($verify.SignerCertificate.Thumbprint)" -ForegroundColor White
