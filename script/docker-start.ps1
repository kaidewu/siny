# Move to the parent directory
Set-Location ..

# Output messages for clarity
Write-Host "Deploying stack..."
Write-Host

# Check if docker-compose command is available
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $cmd = "docker-compose up -d"
} else {
    $cmd = "docker compose up -d"
}

# Execute the Docker Compose command to deploy the stack
Invoke-Expression $cmd

# Ensure the stack is deployed before running the next command
Start-Sleep -Seconds 10

# Output message before executing the next command
Write-Host "Running llama3 in ollama container..."
Write-Host

# Execute the command to run llama3 in the ollama container
docker exec -it ollama ollama run llama3

# Output completion message
Write-Host "Deployment and execution complete."
