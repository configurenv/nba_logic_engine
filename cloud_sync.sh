#!/bin/bash
echo "🔄 Initiating Full Re-Sync for NBA Logic Engine..."

# 1. Define Paths (Updated to your new condensed directory)
LOCAL_DIR="/home/configurenv/nba_logic_engine"
REMOTE_DIR="gdrive:nba_logic_engine"

# 2. Execute Rclone Copy
# --exclude skips massive/temporary folders
# -P shows real-time progress
rclone copy "$LOCAL_DIR" "$REMOTE_DIR" \
    --exclude ".venv/**" \
    --exclude "__pycache__/**" \
    --exclude ".git/**" \
    --drive-chunk-size 64M \
    -P

echo "✅ Cloud Brokenit on Drive."