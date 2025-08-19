#!/bin/bash

# Script for creating log directories for all servers
# This script should be run before starting containers

LOG_BASE_DIR="./logs"

# Create base logs directory if it doesn't exist
if [ ! -d "$LOG_BASE_DIR" ]; then
    echo "Creating base logs directory..."
    mkdir -p "$LOG_BASE_DIR"
fi

# List of possible servers (add your servers)
SERVERS=(
    "ca"
    "ctf" 
    "duel"
    "ffa"
    "freeze"
    "race"
    "tdm"
    "va"
    "premium-duel"
    "private-duel"
)

# Create directories for each server
for server in "${SERVERS[@]}"; do
    server_log_dir="$LOG_BASE_DIR/$server"
    if [ ! -d "$server_log_dir" ]; then
        echo "Creating logs directory for server: $server"
        mkdir -p "$server_log_dir"
        # Set permissions
        chmod 755 "$server_log_dir"
    else
        echo "Logs directory for server $server already exists"
    fi
done

echo "All logs directories created and ready to use"
