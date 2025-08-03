#!/usr/bin/env python3
"""
Test script to analyze the WiFi login page and identify form fields.
This helps configure the automation correctly.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def analyze_login_page():
    """Analyze the login page to find form fields"""
    print("=== WiFi Login Page Analyzer ===")
    print("This script will open the login page and analyze the form fields.")
    print("This helps configure the automation correctly.\n")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to login page
        login_url = "https://172.16.16.16:8090/httpclient.html"
        print(f"Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(3)
        
        print("\n=== Page Analysis ===")
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Find all form elements
        print("\n=== Form Elements Found ===")
        
        # Input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\nFound {len(inputs)} input fields:")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type") or "text"
            input_name = input_elem.get_attribute("name") or "no-name"
            input_id = input_elem.get_attribute("id") or "no-id"
            input_placeholder = input_elem.get_attribute("placeholder") or "no-placeholder"
            
            print(f"  {i+1}. Type: {input_type}")
            print(f"     Name: {input_name}")
            print(f"     ID: {input_id}")
            print(f"     Placeholder: {input_placeholder}")
            print()
        
        # Buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nFound {len(buttons)} buttons:")
        
        for i, button in enumerate(buttons):
            button_text = button.text or "no-text"
            button_type = button.get_attribute("type") or "button"
            button_name = button.get_attribute("name") or "no-name"
            button_id = button.get_attribute("id") or "no-id"
            
            print(f"  {i+1}. Text: {button_text}")
            print(f"     Type: {button_type}")
            print(f"     Name: {button_name}")
            print(f"     ID: {button_id}")
            print()
        
        # Forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"\nFound {len(forms)} forms:")
        
        for i, form in enumerate(forms):
            form_action = form.get_attribute("action") or "no-action"
            form_method = form.get_attribute("method") or "no-method"
            
            print(f"  {i+1}. Action: {form_action}")
            print(f"     Method: {form_method}")
            print()
        
        print("=== Recommendations ===")
        print("Based on the analysis, update your config.py with the correct field names:")
        print()
        
        # Try to identify username field
        username_candidates = []
        for input_elem in inputs:
            input_type = input_elem.get_attribute("type")
            input_name = input_elem.get_attribute("name") or ""
            input_id = input_elem.get_attribute("id") or ""
            input_placeholder = input_elem.get_attribute("placeholder") or ""
            
            if (input_type == "text" and 
                any(keyword in input_name.lower() or keyword in input_id.lower() or keyword in input_placeholder.lower() 
                    for keyword in ["user", "roll", "id", "name", "login"])):
                username_candidates.append(input_name or input_id)
        
        if username_candidates:
            print(f"Username field candidates: {username_candidates}")
        else:
            print("Username field: Check the input fields above and choose the appropriate name/id")
        
        # Try to identify password field
        password_candidates = []
        for input_elem in inputs:
            input_type = input_elem.get_attribute("type")
            input_name = input_elem.get_attribute("name") or ""
            input_id = input_elem.get_attribute("id") or ""
            input_placeholder = input_elem.get_attribute("placeholder") or ""
            
            if (input_type == "password" or 
                any(keyword in input_name.lower() or keyword in input_id.lower() or keyword in input_placeholder.lower() 
                    for keyword in ["pass", "pwd", "password"])):
                password_candidates.append(input_name or input_id)
        
        if password_candidates:
            print(f"Password field candidates: {password_candidates}")
        else:
            print("Password field: Check the input fields above and choose the appropriate name/id")
        
        # Try to identify submit button
        submit_candidates = []
        for button in buttons:
            button_text = button.text or ""
            button_type = button.get_attribute("type") or ""
            button_name = button.get_attribute("name") or ""
            button_id = button.get_attribute("id") or ""
            
            if (button_type == "submit" or 
                any(keyword in button_text.lower() or keyword in button_name.lower() or keyword in button_id.lower() 
                    for keyword in ["submit", "login", "sign", "enter"])):
                submit_candidates.append(button_name or button_id or button_text)
        
        if submit_candidates:
            print(f"Submit button candidates: {submit_candidates}")
        else:
            print("Submit button: Check the buttons above and choose the appropriate name/id/text")
        
        print("\n=== Next Steps ===")
        print("1. Update the field names in config.py based on the recommendations above")
        print("2. Test the automation with: python wifi_automation.py")
        print("3. If it doesn't work, check the logs and adjust the field names")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    analyze_login_page() 