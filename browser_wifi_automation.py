#!/usr/bin/env python3
"""
Browser-based WiFi Automation
Uses Selenium to handle the login form more reliably
"""

import time
import subprocess
import platform
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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

class BrowserWiFiAutomation:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        # Run in headless mode (no browser window)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            # Try to use system ChromeDriver first
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logging.info("Using system ChromeDriver")
            except:
                # Fallback to webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logging.info("Using webdriver-manager ChromeDriver")
            
            self.driver.set_page_load_timeout(30)
            logging.info("WebDriver setup successful")
        except Exception as e:
            logging.error(f"Failed to setup WebDriver: {e}")
            raise
    
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
                
                # Check if we have an IP address (indicates WiFi connection)
                try:
                    result = subprocess.run(["ifconfig", "en0"], 
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and "inet " in result.stdout:
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
    
    def login_to_wifi(self):
        """Automate the WiFi login process using browser"""
        try:
            logging.info("Starting browser-based WiFi login")
            print("🔐 Starting browser-based WiFi login...")
            
            # Navigate to the login page
            self.driver.get(WIFI_CONFIG['login_url'])
            logging.info(f"Navigated to login page: {WIFI_CONFIG['login_url']}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("📄 Login page loaded successfully")
            
            # Try multiple field name combinations
            field_combinations = [
                {'username': WIFI_CONFIG['username_field'], 'password': WIFI_CONFIG['password_field']},
                {'username': 'username', 'password': 'password'},
                {'username': 'user', 'password': 'pass'},
                {'username': 'login', 'password': 'password'},
                {'username': 'roll', 'password': 'pwd'},
                {'username': 'id', 'password': 'passwd'}
            ]
            
            for i, field_mapping in enumerate(field_combinations):
                try:
                    print(f"🔄 Trying login method {i+1} with fields: {list(field_mapping.values())}")
                    
                    # Find and fill username field
                    username_selectors = [
                        (By.NAME, field_mapping['username']),
                        (By.ID, field_mapping['username']),
                        (By.CSS_SELECTOR, f"input[name*='{field_mapping['username']}']"),
                        (By.XPATH, "//input[@type='text']")
                    ]
                    
                    username_field = None
                    for selector_type, selector in username_selectors:
                        try:
                            username_field = self.driver.find_element(selector_type, selector)
                            break
                        except:
                            continue
                    
                    if username_field:
                        username_field.clear()
                        username_field.send_keys(CREDENTIALS['username'])
                        print("✅ Username entered")
                    else:
                        print("❌ Could not find username field")
                        continue
                    
                    # Find and fill password field
                    password_selectors = [
                        (By.NAME, field_mapping['password']),
                        (By.ID, field_mapping['password']),
                        (By.CSS_SELECTOR, f"input[name*='{field_mapping['password']}']"),
                        (By.XPATH, "//input[@type='password']")
                    ]
                    
                    password_field = None
                    for selector_type, selector in password_selectors:
                        try:
                            password_field = self.driver.find_element(selector_type, selector)
                            break
                        except:
                            continue
                    
                    if password_field:
                        password_field.clear()
                        password_field.send_keys(CREDENTIALS['password'])
                        print("✅ Password entered")
                    else:
                        print("❌ Could not find password field")
                        continue
                    
                    # Find and click submit button
                    submit_selectors = [
                        (By.CSS_SELECTOR, "input[type='submit']"),
                        (By.CSS_SELECTOR, "button[type='submit']"),
                        (By.XPATH, "//input[@type='submit'] | //button[@type='submit']"),
                        (By.XPATH, "//button"),
                        (By.CSS_SELECTOR, "button")
                    ]
                    
                    submit_button = None
                    for selector_type, selector in submit_selectors:
                        try:
                            submit_button = self.driver.find_element(selector_type, selector)
                            break
                        except:
                            continue
                    
                    if submit_button:
                        submit_button.click()
                        print("✅ Submit button clicked")
                    else:
                        print("❌ Could not find submit button")
                        continue
                    
                    # Wait a moment for the login to process
                    time.sleep(3)
                    
                    # Check if login was successful by trying to access a test URL
                    try:
                        test_response = self.driver.get('http://www.google.com')
                        if 'google' in self.driver.current_url.lower():
                            print(f"✅ Login successful with method {i+1}!")
                            return True
                        else:
                            print(f"❌ Login failed with method {i+1}")
                    except:
                        print(f"❌ Login failed with method {i+1}")
                        
                except Exception as e:
                    logging.error(f"Error with login method {i+1}: {e}")
                    print(f"❌ Error with login method {i+1}: {e}")
                    continue
            
            print("❌ All login methods failed")
            return False
                
        except Exception as e:
            logging.error(f"Error during WiFi login: {e}")
            print(f"❌ Login error: {e}")
            return False
    
    def run_automation(self):
        """Main automation loop"""
        logging.info("Starting Browser WiFi automation service")
        print("\n🔍 Browser WiFi Automation is running...")
        print("📡 Monitoring for WiFi connection and login opportunities")
        print("⏹️  Press Ctrl+C to stop\n")
        
        while True:
            try:
                current_ssid = self.get_current_wifi_ssid()
                
                if current_ssid:
                    logging.info(f"Connected to WiFi: {current_ssid}")
                    print(f"📶 Connected to WiFi: {current_ssid}")
                    
                    # Always attempt login when connected to GVPH
                    print("🌐 Attempting browser-based login...")
                    if self.login_to_wifi():
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
                logging.info("Automation stopped by user")
                print("\n🛑 Browser WiFi Automation stopped")
                break
            except Exception as e:
                logging.error(f"Error in automation loop: {e}")
                time.sleep(NETWORK_CONFIG['check_interval'])
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    automation = BrowserWiFiAutomation()
    try:
        automation.run_automation()
    except KeyboardInterrupt:
        print("\n🛑 Automation stopped by user")
    finally:
        automation.cleanup() 