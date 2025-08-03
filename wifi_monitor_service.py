#!/usr/bin/env python3
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
                subprocess.run(["/Library/Frameworks/Python.framework/Versions/3.12/bin/python3", "/Users/kameshkadimisetty/Desktop/Wifi Connector/one_time_wifi_login.py"], 
                             cwd="/Users/kameshkadimisetty/Desktop/Wifi Connector", 
                             timeout=60)
                print("✅ Automation completed")
            except subprocess.TimeoutExpired:
                print("⏰ Automation timed out")
            except Exception as e:
                print(f"❌ Automation error: {e}")
        else:
            print("📶 Not connected to GVPH WiFi")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
