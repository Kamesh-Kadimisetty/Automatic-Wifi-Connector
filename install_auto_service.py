#!/usr/bin/env python3
"""
Install WiFi Automation as Background Service
This script sets up the automation to run automatically when connecting to WiFi
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_launch_agent():
    """Create a macOS LaunchAgent to run the WiFi automation automatically"""
    
    # Get the current directory
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "one_time_wifi_login.py")
    python_path = sys.executable
    
    # Create the LaunchAgent plist content
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wifi.automation</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>NetworkState</key>
        <true/>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/wifi_automation.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/wifi_automation_error.log</string>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
</dict>
</plist>"""
    
    # Create the LaunchAgent directory if it doesn't exist
    launch_agent_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(launch_agent_dir, exist_ok=True)
    
    # Write the plist file
    plist_path = os.path.join(launch_agent_dir, "com.wifi.automation.plist")
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print(f"✅ Created LaunchAgent: {plist_path}")
    return plist_path

def create_network_trigger_script():
    """Create a script that triggers on network changes"""
    
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "one_time_wifi_login.py")
    python_path = sys.executable
    
    trigger_script_content = f"""#!/bin/bash

# WiFi Automation Trigger Script
# This script runs when network state changes

# Check if connected to GVPH WiFi
WIFI_SSID=$(system_profiler SPAirPortDataType | grep -A 1 "Current Network Information" | grep "GVPH:" | head -1)

if [[ -n "$WIFI_SSID" ]]; then
    echo "$(date): Connected to GVPH WiFi, starting automation..." >> /tmp/wifi_automation_trigger.log
    cd "{current_dir}"
    {python_path} {script_path} >> /tmp/wifi_automation.log 2>&1 &
else
    echo "$(date): Not connected to GVPH WiFi" >> /tmp/wifi_automation_trigger.log
fi
"""
    
    trigger_script_path = os.path.join(current_dir, "wifi_trigger.sh")
    with open(trigger_script_path, 'w') as f:
        f.write(trigger_script_content)
    
    # Make the script executable
    os.chmod(trigger_script_path, 0o755)
    
    print(f"✅ Created trigger script: {trigger_script_path}")
    return trigger_script_path

def create_network_monitor():
    """Create a network monitoring script that runs continuously"""
    
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "one_time_wifi_login.py")
    python_path = sys.executable
    
    monitor_script_content = f"""#!/usr/bin/env python3
import time
import subprocess
import os
import sys

def check_gvph_wifi():
    try:
        result = subprocess.run(["system_profiler", "SPAirPortDataType"], 
                             capture_output=True, text=True, timeout=10)
        return "GVPH:" in result.stdout
    except:
        return False

def main():
    print("🔍 WiFi Network Monitor Started")
    print("📡 Monitoring for GVPH WiFi connection...")
    
    while True:
        if check_gvph_wifi():
            print("📶 GVPH WiFi detected! Starting automation...")
            
            # Run the automation
            try:
                subprocess.run(["{python_path}", "{script_path}"], 
                             cwd="{current_dir}", 
                             timeout=60)
                print("✅ Automation completed")
            except subprocess.TimeoutExpired:
                print("⏰ Automation timed out")
            except Exception as e:
                print(f"❌ Automation error: {{e}}")
        else:
            print("📶 Not connected to GVPH WiFi")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
"""
    
    monitor_script_path = os.path.join(current_dir, "wifi_monitor_service.py")
    with open(monitor_script_path, 'w') as f:
        f.write(monitor_script_content)
    
    print(f"✅ Created network monitor: {monitor_script_path}")
    return monitor_script_path

def install_launch_agent():
    """Install the LaunchAgent"""
    plist_path = create_launch_agent()
    
    try:
        # Load the LaunchAgent
        subprocess.run(["launchctl", "load", plist_path], check=True)
        print("✅ LaunchAgent loaded successfully")
        print("🔄 The WiFi automation will now run automatically when you connect to WiFi")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error loading LaunchAgent: {e}")
        print("You may need to manually load it with: launchctl load ~/Library/LaunchAgents/com.wifi.automation.plist")

def create_startup_script():
    """Create a simple startup script"""
    
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "one_time_wifi_login.py")
    python_path = sys.executable
    
    startup_script_content = f"""#!/bin/bash

# WiFi Automation Startup Script
# Add this to your shell profile to run on terminal startup

echo "🔍 Checking WiFi connection..."
WIFI_SSID=$(system_profiler SPAirPortDataType | grep -A 1 "Current Network Information" | grep "GVPH:" | head -1)

if [[ -n "$WIFI_SSID" ]]; then
    echo "📶 Connected to GVPH WiFi, starting automation..."
    cd "{current_dir}"
    {python_path} {script_path} &
    echo "✅ WiFi automation started in background"
else
    echo "📶 Not connected to GVPH WiFi"
fi
"""
    
    startup_script_path = os.path.join(current_dir, "start_wifi_auto.sh")
    with open(startup_script_path, 'w') as f:
        f.write(startup_script_content)
    
    os.chmod(startup_script_path, 0o755)
    
    print(f"✅ Created startup script: {startup_script_path}")
    return startup_script_path

def main():
    """Main installation function"""
    print("=== WiFi Automation Auto-Installation ===")
    print("This will set up automatic WiFi login when you connect to GVPH")
    print()
    
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("❌ This auto-installation is designed for macOS")
        return
    
    # Create all the necessary files
    print("📁 Creating automation files...")
    create_network_monitor()
    create_startup_script()
    
    # Ask user which method they prefer
    print("\n🔧 Choose installation method:")
    print("1. LaunchAgent (recommended) - Runs automatically in background")
    print("2. Manual startup script - Run manually when needed")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        print("\n📦 Installing LaunchAgent...")
        install_launch_agent()
    
    if choice in ["2", "3"]:
        startup_script = create_startup_script()
        print(f"\n📝 To use the startup script, add this to your ~/.zshrc or ~/.bash_profile:")
        print(f"source {startup_script}")
    
    print("\n🎉 Installation completed!")
    print("\n📋 Available commands:")
    print(f"• Manual run: python3 one_time_wifi_login.py")
    print(f"• Smart monitor: python3 smart_wifi_monitor.py")
    print(f"• Startup script: ./start_wifi_auto.sh")
    
    if choice in ["1", "3"]:
        print("\n🔄 The automation will now run automatically when you connect to GVPH WiFi!")
        print("💡 To stop the auto-service: launchctl unload ~/Library/LaunchAgents/com.wifi.automation.plist")

if __name__ == "__main__":
    main() 