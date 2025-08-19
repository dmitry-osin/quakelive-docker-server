# PowerShell script for creating log directories for all servers
# This script should be run before starting containers

$LOG_BASE_DIR = ".\logs"

# Create base logs directory if it doesn't exist
if (-not (Test-Path $LOG_BASE_DIR)) {
    Write-Host "Creating base logs directory..."
    New-Item -ItemType Directory -Path $LOG_BASE_DIR -Force
}

# List of possible servers (add your servers)
$SERVERS = @(
    "ca",
    "ctf", 
    "duel",
    "ffa",
    "freeze",
    "race",
    "tdm",
    "va",
    "premium-duel",
    "private-duel"
)

# Create directories for each server
foreach ($server in $SERVERS) {
    $server_log_dir = Join-Path $LOG_BASE_DIR $server
    if (-not (Test-Path $server_log_dir)) {
        Write-Host "Creating logs directory for server: $server"
        New-Item -ItemType Directory -Path $server_log_dir -Force
    } else {
        Write-Host "Logs directory for server $server already exists"
    }
}

Write-Host "All logs directories created and ready to use"
