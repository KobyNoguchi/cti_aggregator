#!/usr/bin/env python
"""
Ultra-simple test script for direct requests
This script tests direct requests without using proxies
"""

import sys
import os
import logging
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Ultra-simple test for direct requests"""
    logger.info("Starting direct request test")
    
    # Test a simple direct request to example.com
    try:
        logger.info("Testing direct request to example.com...")
        response = requests.get("https://example.com", timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Direct request successful with status code: {response.status_code}")
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            
            logger.info(f"Page title: {title.text if title else 'No title'}")
            logger.info("Direct request test successful!")
            return True
        else:
            logger.error(f"Direct request failed with status code: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Direct request test completed successfully!")
    else:
        print("\n❌ Direct request test failed. Check the logs above for details.") 