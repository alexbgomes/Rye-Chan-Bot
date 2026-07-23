#!/bin/bash

# Get current time to filter out old logs
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "Restarting rye-chan service..."
sudo systemctl restart rye-chan

echo "Waiting for bot to connect to Gateway..."
MAX_RETRIES=30
for ((i=1; i<=MAX_RETRIES; i++)); do
  if sudo journalctl -u rye-chan --since "$START_TIME" --no-pager | grep -q "has connected to Gateway"; then
    echo "✅ Bot successfully connected to Gateway!"
    sudo journalctl -u rye-chan --since "$START_TIME" --no-pager
    exit 0
  fi
  sleep 1
done

echo "❌ Error: Bot failed to connect to Gateway within 30 seconds."
echo "Here are the recent logs:"
sudo journalctl -u rye-chan --since "$START_TIME" --no-pager
exit 1
