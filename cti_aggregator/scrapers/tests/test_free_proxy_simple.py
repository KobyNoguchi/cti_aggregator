#!/usr/bin/env python
"""
Simple test script for free proxy scraper implementation
This script does a basic test of our free proxy solution
"""

import sys
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Simple test function for free proxy scraper functionality"""
    start_time = time.time()
    logger.info("Starting simple free proxy test")
    
    try:
        # Import our free proxy modules
        from data_sources.free_proxy_scraper import get, get_soup
        
        # Test a simple request
        logger.info("Testing basic scraping with example.com...")
        soup = get_soup("https://example.com")
        if soup:
            title = soup.find('title')
            logger.info(f"Successfully scraped page with title: {title.text if title else 'No title'}")
            
            # Get all links
            links = soup.find_all('a')
            logger.info(f"Found {len(links)} links on the page")
            
            # Print HTML structure (first 500 chars)
            html_sample = str(soup)[:500] + "..." if len(str(soup)) > 500 else str(soup)
            logger.info(f"HTML sample: {html_sample}")
            
            elapsed = time.time() - start_time
            logger.info(f"Test completed in {elapsed:.2f} seconds")
            return True
        else:
            logger.error("Failed to scrape example.com")
            return False
            
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Free proxy simple test completed successfully!")
    else:
        print("\n❌ Free proxy simple test failed. Check the logs above for details.") 