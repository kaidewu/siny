#!/bin/bash

# Move to the parent directory
cd ..

# Output messages for clarity
echo "Deploying stack..."
echo

# Check if docker-compose command is available
if command -v docker-compose &> /dev/null
then
    cmd="docker-compose up -d"
else
    cmd="docker compose up -d"
fi

# Execute the Docker Compose command to deploy the stack
$cmd

# Ensure the stack is deployed before running the next command
sleep 10

# Output message before executing the next command
echo "Running llama3 in ollama container..."
echo

# Execute the command to run llama3 in the ollama container
docker exec -it ollama ollama run llama3

# Output completion message
echo "Deployment and execution complete."
