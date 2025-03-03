"""
Enhanced Web Scraper using Free Proxies

This module provides an improved web scraper that:
1. Uses a rotating pool of free proxies
2. Implements user agent rotation
3. Has robust retry mechanisms
4. Provides specialized scraping functions for intelligence articles
5. Falls back to headless browser when other methods fail
"""

import requests
import random
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, ProxyError, Timeout, ConnectionError

# Import our free proxy manager
from .free_proxy_scraper import proxy_manager, get, get_soup

# Try to import headless browser module
try:
    from .headless_browser import (
        is_headless_available,
        get_soup_with_headless,
        scrape_intelligence_articles_headless
    )
    HEADLESS_AVAILABLE = is_headless_available()
except ImportError:
    HEADLESS_AVAILABLE = False

logger = logging.getLogger(__name__)

# List of common user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76'
]

def get_random_user_agent() -> str:
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

class FreeEnhancedScraper:
    """Enhanced web scraper using free proxies."""
    
    def __init__(self, 
                 use_proxies: bool = True,
                 use_headless_fallback: bool = True,
                 max_retries: int = 3, 
                 retry_delay: int = 2,
                 timeout: int = 30):
        """
        Initialize the enhanced scraper.
        
        Args:
            use_proxies: Whether to use proxies for requests
            use_headless_fallback: Whether to use headless browser as fallback
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay in seconds between retries (exponential backoff applied)
            timeout: Timeout in seconds for requests
        """
        self.use_proxies = use_proxies
        self.use_headless_fallback = use_headless_fallback and HEADLESS_AVAILABLE
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Ensure we have proxies available if requested
        if self.use_proxies:
            proxy_manager.refresh_proxies(force=False)  # Don't force refresh to use cache if available
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
            params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request using optimal settings.
        
        Args:
            url: URL to request
            headers: Optional headers to include
            params: Optional query parameters
            
        Returns:
            Response object from the request
        """
        if headers is None:
            headers = {}
            
        # Always use a random user agent
        if 'User-Agent' not in headers:
            headers['User-Agent'] = get_random_user_agent()
            
        if self.use_proxies:
            # Use our proxy manager's get function
            return get(url, headers, params, self.max_retries, self.timeout)
        else:
            # Direct request without proxies, but still with retries
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        url, 
                        headers=headers, 
                        params=params, 
                        timeout=self.timeout
                    )
                    
                    # Check if we got a valid response
                    if response.status_code < 400:
                        return response
                        
                    # Handle specific status codes
                    if response.status_code == 403 or response.status_code == 429:
                        logger.warning(f"Request blocked with status code {response.status_code}")
                        # Wait before retrying
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                
                except Timeout as e:
                    logger.warning(f"Request timeout: {str(e)}")
                    last_error = e
                    
                except RequestException as e:
                    logger.warning(f"Request failed: {str(e)}")
                    last_error = e
                    
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    last_error = e
                    
                # Wait before retrying
                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(wait_time)
            
            # All retries failed, create a dummy response
            logger.error(f"All {self.max_retries} attempts failed when requesting {url}")
            
            # Create a dummy response to maintain a consistent interface
            dummy_response = requests.Response()
            dummy_response.status_code = 500
            dummy_response._content = b'{"error": "All request attempts failed"}'
            dummy_response.url = url
            
            # Attach the last error to the response
            if last_error:
                dummy_response.error = last_error
            
            return dummy_response
    
    def get_soup(self, url: str, headers: Optional[Dict[str, str]] = None, 
                params: Optional[Dict[str, Any]] = None) -> Optional[BeautifulSoup]:
        """
        Make a GET request and return BeautifulSoup object.
        
        Args:
            url: URL to request
            headers: Optional headers to include
            params: Optional query parameters
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        if self.use_proxies:
            # Use our proxy-enabled get_soup function
            soup = get_soup(url, headers, params, self.max_retries)
            
            # If proxy method failed and headless fallback is enabled
            if not soup and self.use_headless_fallback and HEADLESS_AVAILABLE:
                logger.info(f"Proxy scraping failed for {url}, trying headless browser fallback")
                return get_soup_with_headless(url)
                
            return soup
        else:
            # Get the response and convert to soup
            response = self.get(url, headers, params)
            
            if response.status_code < 400:
                try:
                    return BeautifulSoup(response.text, 'html.parser')
                except Exception as e:
                    logger.error(f"Failed to parse HTML: {str(e)}")
                    
                    # Try headless browser as fallback
                    if self.use_headless_fallback and HEADLESS_AVAILABLE:
                        logger.info(f"HTML parsing failed for {url}, trying headless browser fallback")
                        return get_soup_with_headless(url)
                    
                    return None
            else:
                logger.error(f"Failed to get soup for {url}, status code: {response.status_code}")
                
                # Try headless browser as fallback
                if self.use_headless_fallback and HEADLESS_AVAILABLE:
                    logger.info(f"Request failed for {url}, trying headless browser fallback")
                    return get_soup_with_headless(url)
                
                return None

def scrape_intelligence_articles(url: str, source_name: str, 
                                 article_selector: str,
                                 title_selector: str,
                                 url_selector: str = None,
                                 date_selector: str = None,
                                 date_format: str = None,
                                 summary_selector: str = None,
                                 url_prefix: str = None,
                                 use_proxies: bool = True,
                                 use_headless_fallback: bool = True,
                                 max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Scrape intelligence articles from a webpage using provided selectors.
    
    Args:
        url: URL of the page to scrape
        source_name: Name of the intelligence source
        article_selector: CSS selector for article containers
        title_selector: CSS selector for article titles
        url_selector: CSS selector for article URLs (if different from title_selector)
        date_selector: CSS selector for published dates
        date_format: Format string for parsing dates
        summary_selector: CSS selector for article summaries
        url_prefix: Prefix to add to relative URLs
        use_proxies: Whether to use proxies for scraping
        use_headless_fallback: Whether to use headless browser as fallback
        max_retries: Maximum number of retries for failed requests
        
    Returns:
        List of dictionaries containing article information
    """
    logger.info(f"Scraping intelligence articles from {source_name}")
    
    # Create and configure the scraper
    scraper = FreeEnhancedScraper(
        use_proxies=use_proxies,
        use_headless_fallback=use_headless_fallback,
        max_retries=max_retries
    )
    
    # First attempt with proxies or standard scraper
    articles = []
    soup = scraper.get_soup(url)
    
    # If we got a soup, extract the articles
    if soup:
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
                
                # Add the article to the list
                articles.append({
                    'title': title,
                    'url': article_url,
                    'source': source_name,
                    'published_date': published_date,
                    'summary': summary
                })
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
    else:
        logger.warning(f"Failed to get soup for {source_name}, all standard methods failed")
        
        # If standard methods failed, try headless browser as a last resort
        if use_headless_fallback and HEADLESS_AVAILABLE:
            logger.info(f"Attempting to scrape {source_name} using headless browser")
            
            try:
                headless_articles = scrape_intelligence_articles_headless(
                    url=url,
                    source_name=source_name,
                    article_selector=article_selector,
                    title_selector=title_selector,
                    url_selector=url_selector,
                    date_selector=date_selector,
                    date_format=date_format,
                    summary_selector=summary_selector,
                    url_prefix=url_prefix
                )
                
                if headless_articles:
                    logger.info(f"Successfully scraped {len(headless_articles)} articles with headless browser")
                    return headless_articles
                else:
                    logger.error(f"Headless browser scraping also failed for {source_name}")
            except Exception as e:
                logger.error(f"Error during headless browser scraping: {str(e)}")
    
    logger.info(f"Successfully scraped {len(articles)} articles from {source_name}")
    return articles

def is_free_proxy_configured() -> bool:
    """
    Check if the free proxy system is properly configured.
    
    Returns:
        bool: True if free proxies are available, False otherwise
    """
    # Make sure we have proxies
    proxy_manager.refresh_proxies()
    
    # Return True if we have at least one working proxy
    return len(proxy_manager.working_proxies) > 0

def example_usage():
    """Example usage of the free enhanced scraper."""
    # Set up logging for the example
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"Headless browser available: {HEADLESS_AVAILABLE}")
    
    # Test direct request
    scraper = FreeEnhancedScraper(use_proxies=False)
    response = scraper.get("https://httpbin.org/ip")
    print(f"Direct request status: {response.status_code}")
    if response.status_code == 200:
        print(f"Your IP: {response.text}")
    
    # Test proxy request
    proxy_scraper = FreeEnhancedScraper(use_proxies=True)
    response = proxy_scraper.get("https://httpbin.org/ip")
    print(f"Proxy request status: {response.status_code}")
    if response.status_code == 200:
        print(f"Proxy IP: {response.text}")
    
    # Test article scraping
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
        use_headless_fallback=True
    )
    
    print(f"Scraped {len(articles)} articles:")
    for i, article in enumerate(articles[:3]):  # Print first 3 articles
        print(f"{i+1}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Date: {article['published_date']}")
        print(f"   Summary: {article['summary'][:100]}...")

if __name__ == "__main__":
    example_usage() 