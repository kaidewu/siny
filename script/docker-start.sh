#!/bin/bash

# Move to the parent directory
cd ..

# Function to delete specified folders and files recursively
function Remove_Items {
    local base_path=$1
    shift
    local paths=("$@")

    for path in "${paths[@]}"; do
        full_path="$base_path/$path"

        # Remove folders recursively
        if [ -d "$full_path" ]; then
            echo "Removing folders matching: $full_path"
            sudo find "$base_path" -type d -name "$(basename "$path")" -exec rm -rf {} +
        # Remove files recursively (using globbing)
        elif [[ "$path" == *\** ]]; then
            echo "Removing files matching: $full_path"
            sudo find "$base_path" -type f -name "$(basename "$path")" -exec rm -f {} +
        fi
    done
}

# Define paths to remove in the frontend directory
frontend_paths_to_remove=(
    "node_modules"
    ".pnpm-store"
    "*.log"
    "*.zip"
    "jspm_packages"
    "build"
)

# Define paths to remove in the backend directory
backend_paths_to_remove=(
    "__pycache__"
    ".pytest_cache"
    "*.log"
    "*.zip"
    ".venv"
    "venv"
    "*.pyc"
)

# Call the function to remove the specified items in frontend
Remove_Items "frontend" "${frontend_paths_to_remove[@]}"

# Call the function to remove the specified items in backend
Remove_Items "backend" "${backend_paths_to_remove[@]}"

# Output messages for clarity
echo "Deploying stack..."
echo

# Check if docker-compose command is available
if command -v docker-compose &> /dev/null; then
    cmd="docker-compose up -d"
    down="docker-compose down"
else
    cmd="docker compose up -d"
    down="docker compose down"
fi

# Down the docker compose
sudo $down

# Execute the Docker Compose command to deploy the stack
sudo $cmd

# Ensure the stack is deployed before running the next command
sleep 10

# Output message before executing the next command
echo "Running llama3 in ollama container..."
echo

# Execute the command to run llama3 in the ollama container
sudo docker exec -it ollama ollama run llama3.1

# Output completion message
echo "Deployment and execution complete."
