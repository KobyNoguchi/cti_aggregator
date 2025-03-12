#!/usr/bin/env python
"""
Script to verify Selenium installation and dependencies.
Run this inside the Docker container to check if Selenium,
Chrome, and ChromeDriver are properly installed.
"""

import sys
import subprocess
import os

def check_selenium():
    try:
        import selenium
        print(f"✅ Selenium is installed (version: {selenium.__version__})")
        return True
    except ImportError:
        print("❌ Selenium is not installed")
        return False

def check_chrome():
    try:
        result = subprocess.run(
            ["google-chrome", "--version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Chrome is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Chrome is not installed or not in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return False

def check_chromedriver():
    try:
        result = subprocess.run(
            ["chromedriver", "--version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"✅ ChromeDriver is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ChromeDriver is not installed or not in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking ChromeDriver: {e}")
        return False

def test_selenium_connection():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("📋 Testing Selenium connection to Chrome...")
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        print(f"✅ Successfully connected to Chrome and loaded page: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Error testing Selenium connection: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Selenium installation and dependencies...")
    
    selenium_ok = check_selenium()
    chrome_ok = check_chrome()
    chromedriver_ok = check_chromedriver()
    
    if selenium_ok and chrome_ok and chromedriver_ok:
        selenium_test = test_selenium_connection()
        
        if selenium_test:
            print("\n✅ All components are installed and working properly!")
            sys.exit(0)
    
    print("\n❌ Some components are missing or not working properly.")
    sys.exit(1) 