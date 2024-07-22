# Move to the parent directory
Set-Location ..

# Function to delete specified folders and files recursively
function Remove-Items {
    param (
        [string]$basePath,
        [string[]]$paths
    )

    foreach ($path in $paths) {
        $fullPath = Join-Path -Path $basePath -ChildPath $path

        # Remove folders recursively
        if (Test-Path $fullPath -PathType Container) {
            Get-ChildItem -Path $basePath -Recurse -Directory -Filter $path | Remove-Item -Recurse -Force
            Write-Host "Removed folders matching: $fullPath"
        }
        # Remove files recursively
        elseif ($path -like "*.*") {
            Get-ChildItem -Path $basePath -Recurse -File -Filter $path | Remove-Item -Force
            Write-Host "Removed files matching: $fullPath"
        }
    }
}

# Define paths to remove in the frontend directory
$frontendPathsToRemove = @(
    "node_modules",
    ".pnpm-store",
    "*.log",
    "*.zip",
    "jspm_packages",
    "build"
)

# Define paths to remove in the backend directory
$backendPathsToRemove = @(
    "__pycache__",
    "*.log",
    "*.zip",
    ".venv",
    "venv",
    "*.pyc"
)

# Call the function to remove the specified items in frontend
Remove-Items -basePath "frontend" -paths $frontendPathsToRemove

# Call the function to remove the specified items in backend
Remove-Items -basePath "backend" -paths $backendPathsToRemove

# Output messages for clarity
Write-Host "Deploying stack..."
Write-Host

# Check if docker-compose command is available
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $cmd = "docker-compose up -d"
    $down = "docker-compose down"
} else {
    $cmd = "docker compose up -d"
    $down = "docker compose down"
}

# Down the docker compose
Invoke-Expression $down

# Execute the Docker Compose command to deploy the stack
Invoke-Expression $cmd

# Ensure the stack is deployed before running the next command
Start-Sleep -Seconds 10

# Output message before executing the next command
Write-Host "Running llama3 in ollama container..."
Write-Host

# Execute the command to run llama3 in the ollama container
Invoke-Expression "docker exec -it ollama ollama run llama3"

# Output completion message
Write-Host "Deployment and execution complete."
