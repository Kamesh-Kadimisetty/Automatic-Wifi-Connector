# WiFi Connector - Hostel WiFi Automation

Automate your hostel WiFi login process! This tool automatically detects when you need to authenticate with your hostel's captive portal and handles the login process for you.

## Features

- 🔄 **Automatic Detection**: Monitors your WiFi connection and detects when authentication is needed
- 🤖 **Auto-Login**: Automatically fills in your roll number and password
- 🔒 **Secure**: Stores credentials in environment variables, not in code
- 📱 **Cross-Platform**: Works on Windows, macOS, and Linux
- 📊 **Logging**: Detailed logs to track what's happening
- 🛡️ **Error Handling**: Robust error handling and retry mechanisms

## Quick Start

### 1. Setup

Run the setup script to configure your credentials:

```bash
python setup.py
```

This will:
- Install required dependencies
- Create a `.env` file with your credentials
- Test the configuration

### 2. Manual Setup (Alternative)

If you prefer manual setup:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   ```bash
   cp env_example.txt .env
   ```

3. **Edit `.env` file** with your credentials:
   ```
   WIFI_USERNAME=your_roll_number_here
   WIFI_PASSWORD=your_password_here
   TARGET_SSID=your_hostel_wifi_name_here
   ```

### 3. Run the Automation

```bash
python wifi_automation.py
```

The tool will:
- Monitor your WiFi connection
- Detect when you need to login
- Automatically fill and submit the login form
- Keep running until you stop it (Ctrl+C)

## How It Works

1. **Network Monitoring**: Continuously checks your WiFi connection
2. **Portal Detection**: Detects when the captive portal is active
3. **Browser Automation**: Opens a browser and navigates to the login page
4. **Form Filling**: Automatically fills in your credentials
5. **Submission**: Submits the form and verifies success

## Configuration

### WiFi Settings (`config.py`)

The tool is pre-configured for your hostel's login page (`https://172.16.16.16:8090/httpclient.html`). If the form fields are different, you can adjust:

```python
WIFI_CONFIG = {
    'login_url': 'https://172.16.16.16:8090/httpclient.html',
    'username_field': 'username',  # Form field name for username
    'password_field': 'password',  # Form field name for password
    'submit_button': 'submit'      # Form field name for submit button
}
```

### Browser Settings

```python
BROWSER_CONFIG = {
    'headless': False,  # Set to True to run without browser window
    'timeout': 30,
    'retry_attempts': 3
}
```

### Network Settings

```python
NETWORK_CONFIG = {
    'target_ssid': '',  # Your hostel WiFi name (optional)
    'check_interval': 5  # Seconds between checks
}
```

## Troubleshooting

### Common Issues

1. **"ChromeDriver not found"**
   - The tool automatically downloads ChromeDriver
   - Make sure you have Chrome browser installed

2. **"Credentials not working"**
   - Check your `.env` file has correct credentials
   - Verify your roll number and password are correct

3. **"Form fields not found"**
   - The tool tries multiple selectors to find form fields
   - Check the logs to see which selectors are being tried
   - You may need to adjust the field names in `config.py`

4. **"SSL Certificate errors"**
   - The tool is configured to ignore SSL errors for captive portals
   - This is normal for internal network pages

### Logs

The tool creates detailed logs in `wifi_automation.log`. Check this file if you encounter issues.

## Security Notes

- ✅ Credentials are stored in `.env` file (not in code)
- ✅ `.env` file should be added to `.gitignore`
- ⚠️ Keep your `.env` file secure and don't share it
- ⚠️ The tool runs a browser - be careful with sensitive sites

## Advanced Usage

### Running in Background

To run the tool in the background:

```bash
nohup python wifi_automation.py > wifi_automation.log 2>&1 &
```

### Headless Mode

Edit `config.py` to run without browser window:

```python
BROWSER_CONFIG = {
    'headless': True,  # Run without browser window
    # ... other settings
}
```

### Custom Network Detection

If you need to customize network detection, modify the `get_current_wifi_ssid()` method in `wifi_automation.py`.

## Requirements

- Python 3.7+
- Chrome browser
- WiFi connection to your hostel network

## Dependencies

- `selenium`: Browser automation
- `requests`: HTTP requests for connectivity checks
- `webdriver-manager`: Automatic ChromeDriver management
- `python-dotenv`: Environment variable management
- `psutil`: System utilities
- `pyautogui`: GUI automation (backup method)

## License

This project is for educational and personal use. Please respect your institution's terms of service.

## Contributing

Feel free to submit issues and enhancement requests!

---

**Note**: This tool is designed for legitimate use with your own credentials. Please ensure you have permission to automate login processes on your network. 