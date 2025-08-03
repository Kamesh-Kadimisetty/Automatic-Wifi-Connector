#!/usr/bin/env python3
"""
Simple WiFi Automation using requests
This version avoids ChromeDriver issues by using direct HTTP requests
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

class SimpleWiFiAutomation:
    def __init__(self):
        self.session = requests.Session()
        # Configure session to ignore SSL errors for captive portals
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
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
                cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ' SSID: ' in line:
                        return line.split(' SSID: ')[1].strip()
            
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
    
    def login_to_wifi(self):
        """Attempt to login using direct HTTP request"""
        try:
            logging.info("Attempting WiFi login via HTTP request")
            
            # First, try to access the login page to get any necessary cookies
            try:
                response = self.session.get(WIFI_CONFIG['login_url'], timeout=10)
                logging.info(f"Login page response status: {response.status_code}")
            except Exception as e:
                logging.error(f"Error accessing login page: {e}")
                return False
            
            # Prepare login data
            login_data = {
                WIFI_CONFIG['username_field']: CREDENTIALS['username'],
                WIFI_CONFIG['password_field']: CREDENTIALS['password']
            }
            
            # Try to submit the login form
            try:
                # Try POST to the same URL
                response = self.session.post(WIFI_CONFIG['login_url'], data=login_data, timeout=10)
                logging.info(f"Login POST response status: {response.status_code}")
                
                # Check if login was successful
                if response.status_code == 200:
                    # Try to access a test URL to see if we're authenticated
                    test_response = self.session.get('http://www.google.com', timeout=5)
                    if test_response.status_code == 200:
                        logging.info("Login appears successful!")
                        return True
                
            except Exception as e:
                logging.error(f"Error during login POST: {e}")
            
            # If direct POST didn't work, try alternative approaches
            logging.info("Trying alternative login methods...")
            
            # Method 1: Try with different form action
            try:
                # Some captive portals use different endpoints
                alternative_urls = [
                    WIFI_CONFIG['login_url'].replace('/httpclient.html', '/login.html'),
                    WIFI_CONFIG['login_url'].replace('/httpclient.html', '/'),
                    WIFI_CONFIG['login_url'].replace('/httpclient.html', '/login')
                ]
                
                for alt_url in alternative_urls:
                    try:
                        response = self.session.post(alt_url, data=login_data, timeout=10)
                        logging.info(f"Alternative URL {alt_url} response: {response.status_code}")
                        
                        # Test connectivity
                        if self.check_internet_connectivity():
                            logging.info(f"Login successful via {alt_url}")
                            return True
                    except:
                        continue
                        
            except Exception as e:
                logging.error(f"Error with alternative URLs: {e}")
            
            # Method 2: Try with different field names
            alternative_field_names = [
                {'username': 'user', 'password': 'pass'},
                {'username': 'login', 'password': 'password'},
                {'username': 'roll', 'password': 'pwd'},
                {'username': 'id', 'password': 'passwd'}
            ]
            
            for field_mapping in alternative_field_names:
                try:
                    alt_login_data = {
                        field_mapping['username']: CREDENTIALS['username'],
                        field_mapping['password']: CREDENTIALS['password']
                    }
                    
                    response = self.session.post(WIFI_CONFIG['login_url'], data=alt_login_data, timeout=10)
                    logging.info(f"Alternative field names response: {response.status_code}")
                    
                    if self.check_internet_connectivity():
                        logging.info("Login successful with alternative field names")
                        return True
                        
                except Exception as e:
                    logging.error(f"Error with alternative field names: {e}")
                    continue
            
            logging.warning("All login methods failed")
            return False
                
        except Exception as e:
            logging.error(f"Error during WiFi login: {e}")
            return False
    
    def run_automation(self):
        """Main automation loop"""
        logging.info("Starting Simple WiFi automation service")
        
        while True:
            try:
                current_ssid = self.get_current_wifi_ssid()
                
                # Check if we're connected to the target network
                if current_ssid and (not NETWORK_CONFIG['target_ssid'] or current_ssid == NETWORK_CONFIG['target_ssid']):
                    logging.info(f"Connected to WiFi: {current_ssid}")
                    
                    # Check if internet is accessible
                    if not self.check_internet_connectivity():
                        logging.info("Internet not accessible, captive portal may be active")
                        
                        # Try to login
                        if self.login_to_wifi():
                            logging.info("Successfully logged in to WiFi")
                        else:
                            logging.warning("Failed to login to WiFi")
                    else:
                        logging.info("Internet is accessible, no login needed")
                else:
                    logging.info(f"Not connected to target WiFi network. Current: {current_ssid}")
                
                # Wait before next check
                time.sleep(NETWORK_CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                logging.info("Automation stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in automation loop: {e}")
                time.sleep(NETWORK_CONFIG['check_interval'])

if __name__ == "__main__":
    automation = SimpleWiFiAutomation()
    try:
        automation.run_automation()
    except KeyboardInterrupt:
        logging.info("Automation stopped by user") 