Write-Host "VaultX Stack Verification" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

$checks = @(
    @{name="Backend Health"; url="http://localhost:8000/api/health"},
    @{name="Nginx Proxy";    url="http://localhost/api/health"},
    @{name="MinIO Console";  url="http://localhost:9001"},
    @{name="Frontend";       url="http://localhost:5173"}
)

foreach ($check in $checks) {
    try {
        $response = Invoke-WebRequest -Uri $check.url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "OK  $($check.name) ($($check.url))" -ForegroundColor Green
        }
    } catch {
        Write-Host "FAIL $($check.name) ($($check.url))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Docker containers:" -ForegroundColor Yellow
docker-compose ps