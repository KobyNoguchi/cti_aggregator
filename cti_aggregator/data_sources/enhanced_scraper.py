"""
Enhanced web scraping module that uses Bright Data when available,
with fallback to standard requests.

This module provides a unified interface for web scraping that can leverage
Bright Data's proxy network when properly configured, but falls back to
standard requests library otherwise.
"""

import os
import requests
import logging
import random
import time
from bs4 import BeautifulSoup
from typing import Dict, Optional, Union, Any, List, Tuple
import sys

# Add the current directory to sys.path to import bright_data module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from data_sources.bright_data import BrightDataScraper, is_bright_data_configured
    BRIGHT_DATA_AVAILABLE = True
except ImportError:
    BRIGHT_DATA_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# List of common user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
]

def get_random_user_agent() -> str:
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

class EnhancedScraper:
    """
    Unified scraper that uses Bright Data when available,
    with fallback to standard requests.
    """
    
    def __init__(self, use_bright_data: bool = True, zone: str = 'residential',
                 country: Optional[str] = None, city: Optional[str] = None,
                 max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the enhanced scraper.
        
        Args:
            use_bright_data: Whether to use Bright Data if available
            zone: The proxy zone to use if using Bright Data
            country: Two-letter country code for geo-targeting
            city: City name for geo-targeting
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.use_bright_data = use_bright_data and BRIGHT_DATA_AVAILABLE and is_bright_data_configured()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if self.use_bright_data:
            logger.info(f"Using Bright Data for scraping (zone: {zone})")
            self.bright_data_scraper = BrightDataScraper(zone, country, city)
        else:
            logger.info("Using standard requests for scraping")
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': get_random_user_agent()
            })
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
            params: Optional[Dict[str, Any]] = None, timeout: int = 30) -> requests.Response:
        """
        Make a GET request, using Bright Data if available.
        
        Args:
            url: The URL to request
            headers: Optional HTTP headers
            params: Optional query parameters
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response object
        """
        # Add a user agent rotation if not using Bright Data
        if not self.use_bright_data and not headers:
            headers = {'User-Agent': get_random_user_agent()}
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.use_bright_data:
                    return self.bright_data_scraper.get(url, headers, params, timeout)
                
                default_headers = {'User-Agent': get_random_user_agent()}
                
                if headers:
                    default_headers.update(headers)
                
                logger.info(f"Making standard request to {url} (attempt {attempt}/{self.max_retries})")
                response = self.session.get(
                    url,
                    headers=default_headers,
                    params=params,
                    timeout=timeout
                )
                
                # Check for common block indicators
                if response.status_code == 403 or response.status_code == 429:
                    logger.warning(f"Request blocked or rate limited (status code: {response.status_code})")
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * attempt
                        logger.info(f"Waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        # Rotate user agent for next attempt
                        continue
                
                logger.info(f"Standard request completed with status {response.status_code}")
                return response
            except requests.RequestException as e:
                logger.error(f"Request failed (attempt {attempt}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt
                    logger.info(f"Waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                
                # Create a dummy response if all retries failed
                dummy_response = requests.Response()
                dummy_response.status_code = 500
                dummy_response._content = str(e).encode('utf-8')
                return dummy_response
    
    def get_soup(self, url: str, headers: Optional[Dict[str, str]] = None, 
                params: Optional[Dict[str, Any]] = None) -> Optional[BeautifulSoup]:
        """
        Make a GET request and return BeautifulSoup object.
        
        Args:
            url: The URL to request
            headers: Optional HTTP headers
            params: Optional query parameters
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        response = self.get(url, headers, params)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        return None

def scrape_intelligence_articles(url: str, source_name: str, 
                                 article_selector: str,
                                 title_selector: str,
                                 url_selector: str = None,
                                 date_selector: str = None,
                                 date_format: str = None,
                                 summary_selector: str = None,
                                 url_prefix: str = None,
                                 use_bright_data: bool = True,
                                 max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Generic function to scrape intelligence articles from a website.
    
    Args:
        url: URL to scrape
        source_name: Name of the intelligence source
        article_selector: CSS selector for article elements
        title_selector: CSS selector for title element within article
        url_selector: CSS selector for URL element (defaults to title_selector)
        date_selector: CSS selector for date element
        date_format: Format string for parsing date (e.g., "%B %d, %Y")
        summary_selector: CSS selector for summary element
        url_prefix: Prefix to add to relative URLs
        use_bright_data: Whether to attempt to use Bright Data
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of article dictionaries with title, url, published_date, and summary
    """
    from datetime import datetime
    
    logger.info(f"Scraping intelligence articles from {source_name} at {url}")
    
    # Try with residential proxies first
    scraper = EnhancedScraper(use_bright_data=use_bright_data, zone='residential', max_retries=max_retries)
    soup = scraper.get_soup(url)
    
    # If residential proxies fail, try datacenter proxies
    if not soup and use_bright_data and BRIGHT_DATA_AVAILABLE:
        logger.info(f"Trying datacenter proxies for {source_name}")
        scraper = EnhancedScraper(use_bright_data=use_bright_data, zone='datacenter', max_retries=max_retries)
        soup = scraper.get_soup(url)
    
    # If both proxy types fail, try without Bright Data
    if not soup and use_bright_data:
        logger.info(f"Trying standard request for {source_name}")
        scraper = EnhancedScraper(use_bright_data=False, max_retries=max_retries)
        soup = scraper.get_soup(url)
    
    if not soup:
        logger.error(f"Failed to retrieve content from {url} after all attempts")
        return []
    
    articles_data = []
    articles = soup.select(article_selector)
    logger.info(f"Found {len(articles)} articles on the page")
    
    for article in articles:
        try:
            # Extract title
            title_elem = article.select_one(title_selector)
            if not title_elem:
                continue
            
            title = title_elem.text.strip()
            
            # Extract URL
            if url_selector:
                url_elem = article.select_one(url_selector)
            else:
                url_elem = title_elem
                
            if not url_elem or not url_elem.get('href'):
                continue
                
            article_url = url_elem['href']
            if url_prefix and not article_url.startswith(('http://', 'https://')):
                article_url = url_prefix + article_url
            
            # Extract date
            published_date = datetime.now()
            if date_selector:
                date_elem = article.select_one(date_selector)
                if date_elem:
                    date_text = date_elem.text.strip()
                    if date_elem.get('datetime'):
                        try:
                            published_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                        except ValueError:
                            logger.warning(f"Could not parse datetime attribute: {date_elem['datetime']}")
                    elif date_format:
                        try:
                            published_date = datetime.strptime(date_text, date_format)
                        except ValueError:
                            logger.warning(f"Could not parse date text with format {date_format}: {date_text}")
            
            # Extract summary
            summary = ""
            if summary_selector:
                summary_elem = article.select_one(summary_selector)
                if summary_elem:
                    summary = summary_elem.text.strip()
            
            articles_data.append({
                'title': title,
                'url': article_url,
                'source': source_name,
                'published_date': published_date,
                'summary': summary[:500] + ('...' if len(summary) > 500 else '')
            })
        except Exception as e:
            logger.error(f"Error processing article for {source_name}: {str(e)}")
            continue
    
    logger.info(f"Successfully processed {len(articles_data)} articles from {source_name}")
    return articles_data

def example_usage():
    """Example of how to use the EnhancedScraper and scrape_intelligence_articles."""
    # Test standard EnhancedScraper
    scraper = EnhancedScraper(use_bright_data=False)
    response = scraper.get('https://httpbin.org/ip')
    
    if response.status_code == 200:
        print(f"Standard request successful! IP: {response.json().get('origin')}")
    else:
        print(f"Standard request failed with status: {response.status_code}")
    
    # Test scrape_intelligence_articles
    articles = scrape_intelligence_articles(
        url="https://www.darkreading.com/threat-intelligence",
        source_name="Dark Reading",
        article_selector=".article-info",
        title_selector="h3 a",
        date_selector=".timestamp",
        date_format="%b %d, %Y",
        summary_selector=".deck",
        url_prefix="https://www.darkreading.com"
    )
    
    print(f"Retrieved {len(articles)} articles from Dark Reading")
    for i, article in enumerate(articles[:3], 1):  # Print first 3 articles
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Date: {article['published_date']}")
        print(f"Summary: {article['summary'][:100]}...")

if __name__ == "__main__":
    # Set up logging for standalone usage
    logging.basicConfig(level=logging.INFO)
    example_usage() 