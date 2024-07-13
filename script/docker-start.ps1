# PowerShell script to deploy Docker stack

Write-Host "Deploying stack..."
Write-Host

# Check if docker-compose command is available
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $cmd = "docker-compose up -d"
} else {
    $cmd = "docker compose up -d"
}

# Execute the command
Invoke-Expression $cmd
