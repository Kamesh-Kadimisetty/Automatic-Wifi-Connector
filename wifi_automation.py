import time
import requests
import subprocess
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import WIFI_CONFIG, CREDENTIALS, BROWSER_CONFIG, NETWORK_CONFIG
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wifi_automation.log'),
        logging.StreamHandler()
    ]
)

class WiFiAutomation:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if BROWSER_CONFIG['headless']:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(BROWSER_CONFIG['timeout'])
            logging.info("WebDriver setup successful")
        except Exception as e:
            logging.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def check_internet_connectivity(self):
        """Check if internet is accessible"""
        try:
            response = requests.get('http://www.google.com', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def is_captive_portal_active(self):
        """Check if captive portal is active by trying to access a known site"""
        try:
            response = requests.get('http://www.google.com', timeout=5)
            # If we get redirected to the login page, captive portal is active
            return '172.16.16.16' in response.url or response.status_code != 200
        except:
            return True
    
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
        """Automate the WiFi login process"""
        try:
            logging.info("Starting WiFi login automation")
            
            # Navigate to the login page
            self.driver.get(WIFI_CONFIG['login_url'])
            logging.info(f"Navigated to login page: {WIFI_CONFIG['login_url']}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and fill username field
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, WIFI_CONFIG['username_field']))
                )
                username_field.clear()
                username_field.send_keys(CREDENTIALS['username'])
                logging.info("Username entered")
            except Exception as e:
                logging.warning(f"Could not find username field by name, trying other selectors: {e}")
                # Try alternative selectors
                selectors = [
                    (By.ID, WIFI_CONFIG['username_field']),
                    (By.CSS_SELECTOR, f"input[name*='user'], input[id*='user'], input[placeholder*='user']"),
                    (By.XPATH, "//input[@type='text']")
                ]
                
                for selector_type, selector in selectors:
                    try:
                        username_field = self.driver.find_element(selector_type, selector)
                        username_field.clear()
                        username_field.send_keys(CREDENTIALS['username'])
                        logging.info("Username entered using alternative selector")
                        break
                    except:
                        continue
            
            # Find and fill password field
            try:
                password_field = self.driver.find_element(By.NAME, WIFI_CONFIG['password_field'])
                password_field.clear()
                password_field.send_keys(CREDENTIALS['password'])
                logging.info("Password entered")
            except Exception as e:
                logging.warning(f"Could not find password field by name, trying other selectors: {e}")
                # Try alternative selectors
                selectors = [
                    (By.ID, WIFI_CONFIG['password_field']),
                    (By.CSS_SELECTOR, f"input[name*='pass'], input[id*='pass'], input[type='password']"),
                    (By.XPATH, "//input[@type='password']")
                ]
                
                for selector_type, selector in selectors:
                    try:
                        password_field = self.driver.find_element(selector_type, selector)
                        password_field.clear()
                        password_field.send_keys(CREDENTIALS['password'])
                        logging.info("Password entered using alternative selector")
                        break
                    except:
                        continue
            
            # Find and click submit button
            try:
                submit_button = self.driver.find_element(By.NAME, WIFI_CONFIG['submit_button'])
                submit_button.click()
                logging.info("Submit button clicked")
            except Exception as e:
                logging.warning(f"Could not find submit button by name, trying other selectors: {e}")
                # Try alternative selectors
                selectors = [
                    (By.ID, WIFI_CONFIG['submit_button']),
                    (By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], button"),
                    (By.XPATH, "//input[@type='submit'] | //button[@type='submit'] | //button")
                ]
                
                for selector_type, selector in selectors:
                    try:
                        submit_button = self.driver.find_element(selector_type, selector)
                        submit_button.click()
                        logging.info("Submit button clicked using alternative selector")
                        break
                    except:
                        continue
            
            # Wait a moment for the login to process
            time.sleep(3)
            
            # Check if login was successful
            if self.check_internet_connectivity():
                logging.info("WiFi login successful!")
                return True
            else:
                logging.warning("Login may have failed - internet not accessible")
                return False
                
        except Exception as e:
            logging.error(f"Error during WiFi login: {e}")
            return False
    
    def run_automation(self):
        """Main automation loop"""
        logging.info("Starting WiFi automation service")
        
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
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    automation = WiFiAutomation()
    try:
        automation.run_automation()
    finally:
        automation.cleanup() 