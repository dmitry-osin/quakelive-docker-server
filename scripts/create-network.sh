#!/bin/bash

# Create the quakelive-network if it doesn't exist
if ! docker network ls | grep -q quakelive-network; then
    echo "Creating quakelive-network Docker network..."
    docker network create quakelive-network
    echo "Network created successfully!"
else
    echo "Network 'quakelive-network' already exists."
fi
