#!/usr/bin/env python3
"""
One-Time WiFi Login - Runs once and exits
"""

import time
import subprocess
import platform
import logging
import pyautogui
import sys
import os
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

class OneTimeWiFiLogin:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        # Run with browser window visible for debugging
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--window-size=800,600')
        chrome_options.add_argument('--window-position=100,100')
        
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
    
    def check_if_already_logged_in(self):
        """Check if we're already logged in by testing internet connectivity"""
        try:
            import requests
            response = requests.get('http://www.google.com', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def fill_login_form(self):
        """Fill the login form using keyboard automation"""
        try:
            logging.info("Starting form filling process")
            print("🔐 Starting form filling process...")
            
            # Navigate to the login page
            self.driver.get(WIFI_CONFIG['login_url'])
            logging.info(f"Navigated to login page: {WIFI_CONFIG['login_url']}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("📄 Login page loaded successfully")
            
            # Wait a moment for the page to fully load
            time.sleep(2)
            
            # Try to find and fill username field
            username_found = False
            username_selectors = [
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.NAME, "user"),
                (By.NAME, "login"),
                (By.NAME, "roll"),
                (By.NAME, "id"),
                (By.XPATH, "//input[@type='text']")
            ]
            
            for selector_type, selector in username_selectors:
                try:
                    username_field = self.driver.find_element(selector_type, selector)
                    username_field.clear()
                    username_field.send_keys(CREDENTIALS['username'])
                    print("✅ Username field found and filled")
                    username_found = True
                    break
                except:
                    continue
            
            if not username_found:
                print("❌ Could not find username field")
                return False
            
            # Try to find and fill password field
            password_found = False
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.NAME, "pass"),
                (By.NAME, "pwd"),
                (By.NAME, "passwd"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for selector_type, selector in password_selectors:
                try:
                    password_field = self.driver.find_element(selector_type, selector)
                    password_field.clear()
                    password_field.send_keys(CREDENTIALS['password'])
                    print("✅ Password field found and filled")
                    password_found = True
                    break
                except:
                    continue
            
            if not password_found:
                print("❌ Could not find password field")
                return False
            
            # Try to submit the form
            print("🔄 Attempting to submit form...")
            
            # Method 1: Try to find and click submit button
            submit_selectors = [
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button"),
                (By.CSS_SELECTOR, "button")
            ]
            
            submit_clicked = False
            for selector_type, selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(selector_type, selector)
                    submit_button.click()
                    print("✅ Submit button clicked")
                    submit_clicked = True
                    break
                except:
                    continue
            
            # Method 2: If no submit button found, try pressing Enter
            if not submit_clicked:
                print("🔄 No submit button found, trying Enter key...")
                try:
                    # Focus on the password field and press Enter
                    password_field.send_keys("\n")
                    print("✅ Enter key pressed")
                    submit_clicked = True
                except:
                    pass
            
            # Method 3: Use pyautogui to press Enter
            if not submit_clicked:
                print("🔄 Trying pyautogui Enter key...")
                try:
                    time.sleep(1)
                    pyautogui.press('enter')
                    print("✅ PyAutoGUI Enter key pressed")
                    submit_clicked = True
                except:
                    pass
            
            if submit_clicked:
                print("✅ Form submitted successfully")
                time.sleep(3)  # Wait for login to process
                return True
            else:
                print("❌ Could not submit form")
                return False
                
        except Exception as e:
            logging.error(f"Error during form filling: {e}")
            print(f"❌ Form filling error: {e}")
            return False
    
    def run_once_and_exit(self):
        """Run the automation once and exit completely"""
        logging.info("Starting one-time WiFi automation")
        print("\n🔍 WiFi Automation - One Time Run")
        print("📡 Checking WiFi connection and attempting login...")
        
        try:
            current_ssid = self.get_current_wifi_ssid()
            
            if current_ssid:
                logging.info(f"Connected to WiFi: {current_ssid}")
                print(f"📶 Connected to WiFi: {current_ssid}")
                
                # Check if already logged in
                if self.check_if_already_logged_in():
                    print("✅ Already logged in - no action needed")
                    print("🎉 Exiting...")
                    return True
                
                # Attempt form filling
                print("🌐 Attempting to fill login form...")
                if self.fill_login_form():
                    logging.info("🎉 Form filled successfully!")
                    print("✅ Form filled successfully!")
                    print("🔄 Closing browser and exiting...")
                    
                    # Close browser and exit
                    self.cleanup()
                    print("🎉 WiFi login automation completed successfully!")
                    print("🎯 Exiting completely...")
                    return True
                else:
                    logging.warning("Form filling failed")
                    print("❌ Form filling failed")
                    print("🎯 Exiting...")
                    return False
            else:
                logging.info("Not connected to WiFi")
                print("📶 Not connected to WiFi")
                print("🎯 Exiting...")
                return False
                
        except Exception as e:
            logging.error(f"Error in automation: {e}")
            print(f"❌ Automation error: {e}")
            print("🎯 Exiting...")
            return False
        finally:
            self.cleanup()
            print("🎯 Process completed and exiting...")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    automation = OneTimeWiFiLogin()
    try:
        success = automation.run_once_and_exit()
        print("🎯 One-time WiFi automation completed")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Automation stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 