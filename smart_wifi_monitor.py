#!/usr/bin/env python3
"""
Smart WiFi Monitor - Only runs automation when needed
"""

import time
import subprocess
import platform
import logging
import os
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wifi_automation.log'),
        logging.StreamHandler()
    ]
)

def check_gvph_wifi():
    """Check if connected to GVPH WiFi"""
    try:
        result = subprocess.run(["system_profiler", "SPAirPortDataType"], 
                             capture_output=True, text=True, timeout=10)
        return "GVPH:" in result.stdout
    except:
        return False

def check_internet_connectivity():
    """Check if internet is accessible (already logged in)"""
    try:
        import requests
        response = requests.get('http://www.google.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def run_automation():
    """Run the WiFi automation"""
    try:
        current_dir = os.getcwd()
        script_path = os.path.join(current_dir, "simple_form_filler.py")
        python_path = sys.executable
        
        result = subprocess.run([python_path, script_path], 
                             cwd=current_dir, 
                             timeout=60,
                             capture_output=True,
                             text=True)
        
        if result.returncode == 0:
            print("✅ Automation completed successfully")
            return True
        else:
            print(f"❌ Automation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Automation timed out")
        return False
    except Exception as e:
        print(f"❌ Automation error: {e}")
        return False

def main():
    """Main monitoring function"""
    print("🔍 Smart WiFi Monitor Started")
    print("📡 Monitoring for GVPH WiFi connection...")
    print("💡 Only runs automation when login is needed")
    print("⏹️  Press Ctrl+C to stop\n")
    
    last_run_time = 0
    cooldown_period = 300  # 5 minutes between runs
    
    while True:
        try:
            current_time = time.time()
            
            # Check if connected to GVPH WiFi
            if check_gvph_wifi():
                print("📶 GVPH WiFi detected")
                
                # Check if already logged in
                if check_internet_connectivity():
                    print("✅ Already logged in - no action needed")
                else:
                    print("🌐 Internet not accessible - login needed")
                    
                    # Check cooldown to prevent spam
                    if current_time - last_run_time > cooldown_period:
                        print("🔄 Starting WiFi automation...")
                        if run_automation():
                            last_run_time = current_time
                            print("✅ Automation completed successfully")
                        else:
                            print("❌ Automation failed")
                    else:
                        remaining = int(cooldown_period - (current_time - last_run_time))
                        print(f"⏳ Cooldown active - {remaining} seconds remaining")
            else:
                print("📶 Not connected to GVPH WiFi")
            
            # Wait before next check
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Smart WiFi Monitor stopped")
            break
        except Exception as e:
            logging.error(f"Error in monitor: {e}")
            print(f"❌ Monitor error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main() 