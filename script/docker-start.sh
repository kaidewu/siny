#!/bin/bash

# Deploy stack
echo "Desplegando stack.."
echo
if  [ -x "$(command -v docker-compose)" ]; then
    cmd="docker-compose up -d"
else
    cmd="docker compose up -d"
fi
eval $cmd
