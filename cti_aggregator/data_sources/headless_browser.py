"""
Headless Browser Scraper

This module provides a fallback scraping solution using a headless browser (Selenium)
for websites with strong anti-scraping protections.
"""

import logging
import time
import random
import os
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Global flag to track if selenium is available
SELENIUM_AVAILABLE = False
WEBDRIVER_AVAILABLE = False

# Try to import selenium, but don't fail if it's not installed
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
    
    # Check if webdriver is available
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        # Create a temporary browser instance to verify it works
        with webdriver.Chrome(options=options) as driver:
            WEBDRIVER_AVAILABLE = True
    except WebDriverException:
        logger.warning("Chrome WebDriver not found or not compatible")
    except Exception as e:
        logger.warning(f"Error initializing Chrome WebDriver: {str(e)}")

except ImportError:
    logger.warning("Selenium not installed. Headless browser fallback not available.")

def is_headless_available() -> bool:
    """
    Check if headless browser scraping is available.
    
    Returns:
        bool: True if selenium and webdriver are available
    """
    return SELENIUM_AVAILABLE and WEBDRIVER_AVAILABLE

def get_user_agent() -> str:
    """
    Get a random user agent for the headless browser.
    
    Returns:
        str: User agent string
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76'
    ]
    return random.choice(user_agents)

def get_soup_with_headless(url: str, wait_for_selector: Optional[str] = None, 
                          timeout: int = 30, wait_time: int = 2) -> Optional[BeautifulSoup]:
    """
    Get BeautifulSoup object using a headless browser.
    
    Args:
        url: URL to scrape
        wait_for_selector: CSS selector to wait for (ensures page is loaded)
        timeout: Maximum time to wait for page to load
        wait_time: Additional time to wait after page load (for JS rendering)
        
    Returns:
        BeautifulSoup object or None if scraping failed
    """
    if not is_headless_available():
        logger.error("Headless browser not available. Install selenium with 'pip install selenium'")
        return None
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument(f"user-agent={get_user_agent()}")
    
    try:
        logger.info(f"Starting headless browser for {url}")
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            
            # Wait for specific element if selector provided
            if wait_for_selector:
                try:
                    WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for selector {wait_for_selector}")
            
            # Additional wait time for JavaScript to render
            time.sleep(wait_time)
            
            # Get the page source and parse with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            logger.info(f"Successfully scraped {url} with headless browser")
            return soup
            
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Error with headless browser: {str(e)}")
    
    return None

def scrape_intelligence_articles_headless(url: str, source_name: str,
                                         article_selector: str,
                                         title_selector: str,
                                         url_selector: str = None,
                                         date_selector: str = None,
                                         date_format: str = None,
                                         summary_selector: str = None,
                                         url_prefix: str = None,
                                         threat_actor_type_selector: str = None,
                                         target_industries_selector: str = None,
                                         wait_time: int = 3) -> List[Dict[str, Any]]:
    """
    Scrape intelligence articles using a headless browser.
    
    Args:
        url: URL to scrape
        source_name: Name of the intelligence source
        article_selector: CSS selector for article containers
        title_selector: CSS selector for article titles
        url_selector: CSS selector for article URLs
        date_selector: CSS selector for published dates
        date_format: Format string for parsing dates
        summary_selector: CSS selector for article summaries
        url_prefix: Prefix to add to relative URLs
        threat_actor_type_selector: CSS selector for threat actor type
        target_industries_selector: CSS selector for target industries
        wait_time: Additional time to wait after page load
        
    Returns:
        List of dictionaries containing article information
    """
    from datetime import datetime
    
    logger.info(f"Scraping {source_name} with headless browser")
    
    # Get the page content with headless browser
    soup = get_soup_with_headless(url, wait_for_selector=article_selector, wait_time=wait_time)
    
    if not soup:
        logger.error(f"Failed to get content from {url} with headless browser")
        return []
    
    # Process the articles
    articles = []
    article_elements = soup.select(article_selector)
    logger.info(f"Found {len(article_elements)} article elements on the page")
    
    for article in article_elements:
        try:
            # Extract title
            title_elem = article.select_one(title_selector)
            if not title_elem:
                continue
            
            title = title_elem.text.strip()
            
            # Extract URL
            if url_selector:
                url_elem = article.select_one(url_selector)
                article_url = url_elem['href'] if url_elem else None
            else:
                article_url = title_elem.get('href')
            
            # Add prefix to URL if needed
            if article_url and url_prefix and not article_url.startswith(('http://', 'https://')):
                article_url = url_prefix + article_url
            
            # Skip if no URL found
            if not article_url:
                continue
            
            # Extract date
            published_date = datetime.now()  # Default to current date
            if date_selector:
                date_elem = article.select_one(date_selector)
                if date_elem and date_elem.text.strip():
                    try:
                        if date_format:
                            published_date = datetime.strptime(date_elem.text.strip(), date_format)
                        else:
                            # Try common date formats
                            date_text = date_elem.text.strip()
                            for fmt in ['%Y-%m-%d', '%b %d, %Y', '%d %b %Y', '%B %d, %Y', '%m/%d/%Y', '%d/%m/%Y']:
                                try:
                                    published_date = datetime.strptime(date_text, fmt)
                                    break
                                except ValueError:
                                    continue
                    except ValueError as e:
                        logger.warning(f"Failed to parse date '{date_elem.text.strip()}': {str(e)}")
            
            # Extract summary
            summary = ""
            if summary_selector:
                summary_elem = article.select_one(summary_selector)
                if summary_elem:
                    summary = summary_elem.text.strip()
            
            # Truncate summary if too long
            if len(summary) > 500:
                summary = summary[:500] + '...'
            
            # Extract threat actor type
            threat_actor_type = None
            if threat_actor_type_selector:
                threat_actor_elem = article.select_one(threat_actor_type_selector)
                if threat_actor_elem:
                    threat_actor_type = threat_actor_elem.text.strip()
            
            # Extract target industries
            target_industries = None
            if target_industries_selector:
                target_industries_elem = article.select_one(target_industries_selector)
                if target_industries_elem:
                    target_industries = target_industries_elem.text.strip()
            
            # Add the article to the list
            articles.append({
                'title': title,
                'url': article_url,
                'source': source_name,
                'published_date': published_date,
                'summary': summary,
                'threat_actor_type': threat_actor_type,
                'target_industries': target_industries
            })
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            continue
    
    logger.info(f"Successfully scraped {len(articles)} articles from {source_name} using headless browser")
    return articles

def headless_browser_example():
    """Example usage of the headless browser scraper"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not is_headless_available():
        print("Headless browser not available. Install selenium with 'pip install selenium'")
        return
    
    print("Testing headless browser scraper...")
    
    # Test on a simple website
    soup = get_soup_with_headless("https://example.com")
    if soup:
        title = soup.find('title')
        print(f"Successfully scraped example.com - Title: {title.text if title else 'No title'}")
    
    # Test on Dark Reading
    articles = scrape_intelligence_articles_headless(
        url="https://www.darkreading.com/threat-intelligence",
        source_name="Dark Reading",
        article_selector=".article-info",
        title_selector="h3 a",
        date_selector=".timestamp",
        date_format="%b %d, %Y",
        summary_selector=".deck",
        url_prefix="https://www.darkreading.com"
    )
    
    print(f"\nScraped {len(articles)} articles from Dark Reading:")
    for i, article in enumerate(articles[:3]):  # Print first 3 articles
        print(f"{i+1}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Date: {article['published_date']}")
        print(f"   Summary: {article['summary'][:100]}...")

if __name__ == "__main__":
    headless_browser_example() 