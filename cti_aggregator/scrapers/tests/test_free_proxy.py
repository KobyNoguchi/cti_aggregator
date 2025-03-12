#!/usr/bin/env python
"""
Test script for free proxy scraper implementation
This script tests the functionality of our free proxy solution
"""

import sys
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main test function to verify free proxy scraper functionality"""
    start_time = time.time()
    logger.info("Starting free proxy scraper test")
    
    try:
        # Import our free proxy modules
        from data_sources.free_proxy_scraper import proxy_manager, get, get_soup
        from data_sources.free_enhanced_scraper import FreeEnhancedScraper, scrape_intelligence_articles, is_free_proxy_configured
        
        # Test the proxy manager
        logger.info("Testing proxy manager...")
        proxy_manager.refresh_proxies(force=True)
        logger.info(f"Found {len(proxy_manager.working_proxies)} working proxies")
        logger.info(f"Proxy manager configured: {is_free_proxy_configured()}")
        
        # Test basic requests
        logger.info("Testing basic request...")
        response = get("https://httpbin.org/ip")
        if response.status_code == 200:
            logger.info(f"Basic request successful with proxy IP: {response.text.strip()}")
        else:
            logger.warning(f"Basic request failed with status code: {response.status_code}")
            
        # Test the enhanced scraper for a simple request
        logger.info("Testing enhanced scraper for simple request...")
        scraper = FreeEnhancedScraper(use_proxies=True, max_retries=2)
        response = scraper.get("https://httpbin.org/user-agent")
        if response.status_code == 200:
            logger.info(f"Enhanced scraper request successful with user agent: {response.text.strip()}")
        else:
            logger.warning(f"Enhanced scraper request failed with status code: {response.status_code}")
            
        # Test scraping a website
        logger.info("Testing scraping example.com...")
        soup = get_soup("https://example.com")
        if soup:
            title = soup.find('title')
            logger.info(f"Successfully scraped page with title: {title.text if title else 'No title'}")
        else:
            logger.warning("Failed to scrape example.com")
            
        # Test the intelligence article scraper
        logger.info("Testing intelligence article scraper for Dark Reading...")
        articles = scrape_intelligence_articles(
            url="https://www.darkreading.com/threat-intelligence",
            source_name="Dark Reading",
            article_selector=".article-info",
            title_selector="h3 a",
            date_selector=".timestamp",
            date_format="%b %d, %Y",
            summary_selector=".deck",
            url_prefix="https://www.darkreading.com",
            use_proxies=True,
            max_retries=2
        )
        
        if articles:
            logger.info(f"Successfully scraped {len(articles)} articles from Dark Reading")
            # Print the first 3 articles
            for i, article in enumerate(articles[:3]):
                logger.info(f"{i+1}. {article['title']}")
                logger.info(f"   URL: {article['url']}")
                logger.info(f"   Date: {article['published_date']}")
                logger.info(f"   Summary: {article['summary'][:100]}..." if len(article['summary']) > 100 else article['summary'])
        else:
            logger.warning("Failed to scrape articles from Dark Reading")
            
            # Try fallback to direct connection
            logger.info("Trying direct connection without proxies...")
            articles = scrape_intelligence_articles(
                url="https://www.darkreading.com/threat-intelligence",
                source_name="Dark Reading",
                article_selector=".article-info",
                title_selector="h3 a",
                date_selector=".timestamp",
                date_format="%b %d, %Y",
                summary_selector=".deck",
                url_prefix="https://www.darkreading.com",
                use_proxies=False,
                max_retries=2
            )
            
            if articles:
                logger.info(f"Successfully scraped {len(articles)} articles from Dark Reading using direct connection")
                # Print the first 3 articles
                for i, article in enumerate(articles[:3]):
                    logger.info(f"{i+1}. {article['title']}")
                    logger.info(f"   URL: {article['url']}")
            else:
                logger.error("Failed to scrape articles from Dark Reading even with direct connection")
        
        elapsed = time.time() - start_time
        logger.info(f"Free proxy scraper test completed in {elapsed:.2f} seconds")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Make sure you've installed all the required dependencies from requirements.txt")
        return False
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Free proxy scraper test completed successfully!")
        else:
            print("\n❌ Free proxy scraper test failed. Check the logs above for details.")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc()) 