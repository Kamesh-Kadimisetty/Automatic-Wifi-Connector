#!/bin/bash

# WiFi Automation Startup Script
# Add this to your shell profile to run on terminal startup

echo "🔍 Checking WiFi connection..."
WIFI_SSID=$(system_profiler SPAirPortDataType | grep -A 1 "Current Network Information" | grep "GVPH:" | head -1)

if [[ -n "$WIFI_SSID" ]]; then
    echo "📶 Connected to GVPH WiFi, starting automation..."
    cd "/Users/kameshkadimisetty/Desktop/Wifi Connector"
    python3 "one_time_wifi_login.py" &
    echo "✅ WiFi automation started in background"
else
    echo "📶 Not connected to GVPH WiFi"
fi
