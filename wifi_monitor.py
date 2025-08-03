#!/usr/bin/env python3
"""
WiFi Monitor - Automatically login when connected to hostel WiFi
"""

import time
import requests
import subprocess
import platform
import logging
from config import WIFI_CONFIG, CREDENTIALS, NETWORK_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wifi_automation.log'),
        logging.StreamHandler()
    ]
)

class WiFiMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Track login attempts to avoid spam
        self.last_login_attempt = 0
        self.login_cooldown = 30  # seconds between login attempts (reduced from 60)
    
    def check_internet_connectivity(self):
        """Check if internet is accessible"""
        try:
            response = self.session.get('http://www.google.com', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_current_wifi_ssid(self):
        """Get the current WiFi SSID"""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # Try system_profiler method first
                try:
                    result = subprocess.run(["system_profiler", "SPAirPortDataType"], 
                                         capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        output = result.stdout
                        if "GVPH:" in output:
                            return "GVPH"
                except:
                    pass
                
                # Try networksetup method
                try:
                    result = subprocess.run(["networksetup", "-getairportnetwork", "en0"], 
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and "GVPH" in result.stdout:
                        return "GVPH"
                except:
                    pass
                
                # Check if we have an IP address (indicates WiFi connection)
                try:
                    result = subprocess.run(["ifconfig", "en0"], 
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and "inet " in result.stdout:
                        # We have an IP, likely connected to GVPH
                        return "GVPH"
                except:
                    pass
                    
            elif system == "Windows":
                cmd = ["netsh", "wlan", "show", "interfaces"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'SSID' in line and 'BSSID' not in line:
                        return line.split(':')[1].strip()
            
            elif system == "Linux":
                cmd = ["iwgetid", "-r"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip()
                
        except Exception as e:
            logging.error(f"Error getting WiFi SSID: {e}")
        
        return None
    
    def attempt_login(self):
        """Attempt to login to the WiFi portal"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_login_attempt < self.login_cooldown:
            logging.info("Skipping login attempt due to cooldown")
            return False
        
        self.last_login_attempt = current_time
        
        try:
            logging.info("Attempting WiFi login...")
            print("🔐 Attempting WiFi login...")
            
            # Try to access the login page first
            try:
                response = self.session.get(WIFI_CONFIG['login_url'], timeout=10)
                logging.info(f"Login page response: {response.status_code}")
            except Exception as e:
                logging.error(f"Error accessing login page: {e}")
                return False
            
            # Try multiple field name combinations
            field_combinations = [
                {WIFI_CONFIG['username_field']: CREDENTIALS['username'], 
                 WIFI_CONFIG['password_field']: CREDENTIALS['password']},
                {'username': CREDENTIALS['username'], 'password': CREDENTIALS['password']},
                {'user': CREDENTIALS['username'], 'pass': CREDENTIALS['password']},
                {'login': CREDENTIALS['username'], 'password': CREDENTIALS['password']},
                {'roll': CREDENTIALS['username'], 'pwd': CREDENTIALS['password']},
                {'id': CREDENTIALS['username'], 'passwd': CREDENTIALS['password']}
            ]
            
            for i, login_data in enumerate(field_combinations):
                try:
                    logging.info(f"Trying field combination {i+1}: {list(login_data.keys())}")
                    print(f"🔄 Trying login method {i+1}...")
                    
                    response = self.session.post(WIFI_CONFIG['login_url'], 
                                              data=login_data, timeout=15)
                    logging.info(f"POST response status: {response.status_code}")
                    
                    # Test if login worked
                    if self.check_internet_connectivity():
                        logging.info(f"✅ Login successful with combination {i+1}!")
                        print(f"✅ Login successful with method {i+1}!")
                        return True
                    else:
                        logging.info(f"❌ Login failed with combination {i+1}")
                        print(f"❌ Login method {i+1} failed")
                        
                except Exception as e:
                    logging.error(f"Error with combination {i+1}: {e}")
                    print(f"❌ Error with login method {i+1}")
                    continue
            
            logging.warning("All login attempts failed")
            print("❌ All login attempts failed")
            return False
            
        except Exception as e:
            logging.error(f"Error during login attempt: {e}")
            print(f"❌ Login error: {e}")
            return False
    
    def run_monitor(self):
        """Main monitoring loop"""
        logging.info("Starting WiFi Monitor...")
        logging.info("This will monitor your connection and attempt login when needed.")
        logging.info("Press Ctrl+C to stop.")
        print("\n🔍 WiFi Monitor is running...")
        print("📡 Monitoring for WiFi connection and login opportunities")
        print("⏹️  Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Check current WiFi
                current_ssid = self.get_current_wifi_ssid()
                
                if current_ssid:
                    logging.info(f"Connected to WiFi: {current_ssid}")
                    print(f"📶 Connected to WiFi: {current_ssid}")
                    
                    # Always attempt login when connected to GVPH (regardless of internet check)
                    print("🌐 Attempting login to WiFi portal...")
                    if self.attempt_login():
                        logging.info("🎉 Successfully logged in!")
                        print("✅ WiFi login successful!")
                    else:
                        logging.warning("Login attempt failed")
                        print("❌ Login attempt failed")
                else:
                    logging.info("Not connected to WiFi")
                    print("📶 Not connected to WiFi")
                
                # Wait before next check
                time.sleep(NETWORK_CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                logging.info("Monitor stopped by user")
                print("\n🛑 WiFi Monitor stopped")
                break
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                time.sleep(NETWORK_CONFIG['check_interval'])

if __name__ == "__main__":
    monitor = WiFiMonitor()
    monitor.run_monitor() 