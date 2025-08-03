import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WiFi Configuration
WIFI_CONFIG = {
    'login_url': 'https://172.16.16.16:8090/httpclient.html',
    'username_field': 'username',  # This might need to be adjusted based on actual form
    'password_field': 'password',  # This might need to be adjusted based on actual form
    'submit_button': 'submit'      # This might need to be adjusted based on actual form
}

# Credentials (load from environment variables for security)
CREDENTIALS = {
    'username': os.getenv('WIFI_USERNAME', ''),
    'password': os.getenv('WIFI_PASSWORD', '')
}

# Browser Configuration
BROWSER_CONFIG = {
    'headless': False,  # Set to True to run without opening browser window
    'timeout': 30,
    'retry_attempts': 3
}

# Network Detection
NETWORK_CONFIG = {
    'target_ssid': os.getenv('TARGET_SSID', ''),  # Your hostel WiFi SSID
    'check_interval': 5  # seconds between network checks
} 