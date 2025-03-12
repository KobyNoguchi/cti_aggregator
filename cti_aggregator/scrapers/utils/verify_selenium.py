#!/usr/bin/env python3
"""
Verify Selenium Installation

This script checks if Selenium and its dependencies are properly installed.
It verifies:
1. Selenium Python package
2. Chrome/Chromium browser
3. ChromeDriver
4. Ability to connect to a website

Usage:
    python verify_selenium.py
"""

import sys
import subprocess
import logging
from importlib import import_module
from importlib.util import find_spec

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_selenium():
    """Check if Selenium is installed and get its version"""
    try:
        import selenium
        logger.info(f"✅ Selenium is installed (version: {selenium.__version__})")
        return True
    except ImportError:
        logger.error("❌ Selenium is not installed. Install it with: pip install selenium")
        return False

def check_chrome():
    """Check if Chrome/Chromium is installed"""
    try:
        # Try to get Chrome version
        if sys.platform.startswith('win'):
            # Windows
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            logger.info(f"✅ Google Chrome is installed (version: {version})")
            return True
        elif sys.platform.startswith('darwin'):
            # macOS
            result = subprocess.run(
                ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                capture_output=True, text=True
            )
            logger.info(f"✅ Google Chrome is installed ({result.stdout.strip()})")
            return True
        else:
            # Linux
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Google Chrome is installed ({result.stdout.strip()})")
                return True
            
            # Try Chromium as fallback
            result = subprocess.run(['chromium-browser', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Chromium is installed ({result.stdout.strip()})")
                return True
            
            logger.error("❌ Chrome/Chromium not found")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to detect Chrome/Chromium: {str(e)}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is installed and accessible"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Try to create a Chrome driver instance
        driver = webdriver.Chrome(options=options)
        driver.quit()
        
        logger.info("✅ ChromeDriver is installed and working")
        return True
    except Exception as e:
        logger.error(f"❌ ChromeDriver error: {str(e)}")
        return False

def test_selenium_connection():
    """Test if Selenium can connect to a website"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        logger.info("Testing connection to a website...")
        driver = webdriver.Chrome(options=options)
        
        # Try to load a simple website
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        logger.info(f"✅ Successfully connected to website. Page title: {title}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to website: {str(e)}")
        return False

def main():
    """Run all checks and provide a summary"""
    logger.info("Verifying Selenium installation...")
    
    selenium_ok = check_selenium()
    chrome_ok = check_chrome()
    chromedriver_ok = check_chromedriver()
    connection_ok = test_selenium_connection()
    
    print("\n=== Selenium Verification Summary ===")
    print(f"Selenium Python package: {'✅ Installed' if selenium_ok else '❌ Not installed'}")
    print(f"Chrome/Chromium browser: {'✅ Installed' if chrome_ok else '❌ Not installed'}")
    print(f"ChromeDriver: {'✅ Working' if chromedriver_ok else '❌ Not working'}")
    print(f"Connection test: {'✅ Successful' if connection_ok else '❌ Failed'}")
    
    if selenium_ok and chrome_ok and chromedriver_ok and connection_ok:
        print("\n✅ All components are properly installed and working!")
        return 0
    else:
        print("\n❌ Some components are missing or not working properly.")
        print("Please check the logs above for details on how to fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 