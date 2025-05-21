# Create the quakelive-network if it doesn't exist
$networkExists = docker network ls --format "{{.Name}}" | Where-Object { $_ -eq "quakelive-network" }

if (-not $networkExists) {
    Write-Host "Creating quakelive-network Docker network..." -ForegroundColor Green
    docker network create quakelive-network
    Write-Host "Network created successfully!" -ForegroundColor Green
} else {
    Write-Host "Network 'quakelive-network' already exists." -ForegroundColor Yellow
}
