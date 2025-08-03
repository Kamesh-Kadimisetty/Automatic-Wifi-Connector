#!/usr/bin/env python3
"""
WiFi Automation Setup Script
This script helps you set up the WiFi automation tool for your hostel network.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    print("=== WiFi Automation Setup ===")
    print("This will create a .env file with your credentials.")
    print("Your credentials will be stored securely and not shared.\n")
    
    # Get user input
    username = input("Enter your roll number: ").strip()
    password = input("Enter your WiFi password: ").strip()
    ssid = input("Enter your hostel WiFi network name (optional, press Enter to skip): ").strip()
    
    # Create .env file
    env_content = f"""# WiFi Credentials
WIFI_USERNAME={username}
WIFI_PASSWORD={password}

# WiFi Network Settings
TARGET_SSID={ssid}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("⚠️  Keep this file secure and don't share it with others.")

def install_dependencies():
    """Install required Python packages"""
    print("\n=== Installing Dependencies ===")
    
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def test_setup():
    """Test the setup"""
    print("\n=== Testing Setup ===")
    
    try:
        # Test imports
        from config import WIFI_CONFIG, CREDENTIALS
        print("✅ Configuration loaded successfully")
        
        # Check if credentials are set
        if CREDENTIALS['username'] and CREDENTIALS['password']:
            print("✅ Credentials are configured")
        else:
            print("❌ Credentials are not set in .env file")
            return False
        
        print("✅ Setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Welcome to WiFi Automation Setup!")
    print("This tool will help you automate your hostel WiFi login.\n")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        overwrite = input("A .env file already exists. Overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please try manually:")
        print("pip install -r requirements.txt")
        return
    
    # Test setup
    if test_setup():
        print("\n🎉 Setup completed successfully!")
        print("\nTo start the WiFi automation:")
        print("python wifi_automation.py")
        print("\nThe tool will automatically:")
        print("- Monitor your WiFi connection")
        print("- Detect when you need to login")
        print("- Automatically fill in your credentials")
        print("- Submit the login form")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 