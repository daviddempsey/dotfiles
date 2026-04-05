#!/bin/bash
# Daily TRMNL "This Day in History" image generator
# Runs at 6:00 AM daily via cron

# Load environment variables
set -a
source ~/.openclaw/.env
set +a

# Change to skill directory
cd ~/.openclaw/skills/trmnl-imagegen || exit 1

echo "[$(date)] Starting daily history generation"
python3 daily_history.py
echo "[$(date)] Daily history generation completed"
