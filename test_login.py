#!/usr/bin/env python3
"""
Test script to directly test the WiFi login functionality
"""

import requests
import logging
from config import WIFI_CONFIG, CREDENTIALS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_login():
    """Test the login functionality directly"""
    print("=== Testing WiFi Login ===")
    print(f"Login URL: {WIFI_CONFIG['login_url']}")
    print(f"Username: {CREDENTIALS['username']}")
    print(f"Password: {'*' * len(CREDENTIALS['password'])}")
    print()
    
    # Create session
    session = requests.Session()
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        # Step 1: Try to access the login page
        print("1. Testing access to login page...")
        response = session.get(WIFI_CONFIG['login_url'], timeout=10)
        print(f"   Response status: {response.status_code}")
        print(f"   Response URL: {response.url}")
        
        if response.status_code == 200:
            print("   ✅ Successfully accessed login page")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
        
        # Step 2: Try to submit login form
        print("\n2. Testing login form submission...")
        login_data = {
            WIFI_CONFIG['username_field']: CREDENTIALS['username'],
            WIFI_CONFIG['password_field']: CREDENTIALS['password']
        }
        
        response = session.post(WIFI_CONFIG['login_url'], data=login_data, timeout=10)
        print(f"   Response status: {response.status_code}")
        print(f"   Response URL: {response.url}")
        
        if response.status_code == 200:
            print("   ✅ Login form submitted successfully")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
        
        # Step 3: Test internet connectivity
        print("\n3. Testing internet connectivity...")
        try:
            test_response = session.get('http://www.google.com', timeout=5)
            if test_response.status_code == 200:
                print("   ✅ Internet is accessible - login may have worked!")
            else:
                print(f"   ⚠️  Internet test returned status: {test_response.status_code}")
        except Exception as e:
            print(f"   ❌ Internet test failed: {e}")
        
        # Step 4: Try alternative field names
        print("\n4. Testing alternative field names...")
        alternative_field_names = [
            {'username': 'user', 'password': 'pass'},
            {'username': 'login', 'password': 'password'},
            {'username': 'roll', 'password': 'pwd'},
            {'username': 'id', 'password': 'passwd'},
            {'username': 'username', 'password': 'password'}
        ]
        
        for i, field_mapping in enumerate(alternative_field_names):
            try:
                alt_login_data = {
                    field_mapping['username']: CREDENTIALS['username'],
                    field_mapping['password']: CREDENTIALS['password']
                }
                
                response = session.post(WIFI_CONFIG['login_url'], data=alt_login_data, timeout=10)
                print(f"   Field mapping {i+1}: {field_mapping} - Status: {response.status_code}")
                
                # Test connectivity
                test_response = session.get('http://www.google.com', timeout=5)
                if test_response.status_code == 200:
                    print(f"   ✅ SUCCESS with field mapping: {field_mapping}")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Error with field mapping {field_mapping}: {e}")
        
        print("\n=== Test Complete ===")
        print("If none of the field mappings worked, you may need to:")
        print("1. Check the actual form field names on the login page")
        print("2. Update the config.py file with the correct field names")
        print("3. Try running the test_login_page.py script to analyze the form")
        
        return False
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_login() 