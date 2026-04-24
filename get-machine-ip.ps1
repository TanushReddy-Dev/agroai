Write-Host "Getting your machine IP address..." -ForegroundColor Green
Write-Host ""

# Get IPv4 addresses (non-loopback)
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch "^127\." } | Select-Object -ExpandProperty IPAddress | Get-Unique

if ($ips) {
    Write-Host "Found IP addresses:" -ForegroundColor Cyan
    foreach ($ip in $ips) {
        Write-Host "  $ip" -ForegroundColor White
        Write-Host "  -> Use http://${ip}:8000 in agro-app/services/api.js" -ForegroundColor Green
    }
} else {
    Write-Host "Running ipconfig to find your IP:" -ForegroundColor Yellow
    ipconfig
}
