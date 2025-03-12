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

# Create a proxy health tracking system
class ProxyHealthTracker:
    """
    Tracks the health and reliability of proxies to optimize proxy selection.
    """
    def __init__(self, max_failures: int = 3, recovery_time: int = 300):
        self.proxy_failures: Dict[str, int] = {}  # Count of failures per proxy
        self.blacklisted_proxies: Dict[str, float] = {}  # Blacklisted proxies with timestamp
        self.max_failures = max_failures  # Max failures before blacklisting
        self.recovery_time = recovery_time  # Time in seconds before a proxy can be tried again
        self.logger = logging.getLogger(__name__)
    
    def record_success(self, proxy: str) -> None:
        """Record a successful request through a proxy"""
        if proxy in self.proxy_failures:
            self.proxy_failures.pop(proxy)  # Reset failure count on success
            self.logger.debug(f"Proxy {proxy} succeeded, reset failure count")
    
    def record_failure(self, proxy: str) -> None:
        """Record a failed request through a proxy"""
        if proxy not in self.proxy_failures:
            self.proxy_failures[proxy] = 1
        else:
            self.proxy_failures[proxy] += 1
            
        # Check if we should blacklist the proxy
        if self.proxy_failures[proxy] >= self.max_failures:
            self.blacklist_proxy(proxy)
    
    def blacklist_proxy(self, proxy: str) -> None:
        """Blacklist a proxy temporarily"""
        self.blacklisted_proxies[proxy] = time.time()
        if proxy in self.proxy_failures:
            self.proxy_failures.pop(proxy)
        self.logger.info(f"Blacklisted proxy {proxy} for {self.recovery_time} seconds")
    
    def is_blacklisted(self, proxy: str) -> bool:
        """Check if a proxy is currently blacklisted"""
        if proxy not in self.blacklisted_proxies:
            return False
            
        # Check if blacklist period has expired
        blacklist_time = self.blacklisted_proxies[proxy]
        if time.time() - blacklist_time > self.recovery_time:
            # Proxy has served its time, remove from blacklist
            self.blacklisted_proxies.pop(proxy)
            self.logger.debug(f"Proxy {proxy} removed from blacklist")
            return False
            
        return True
    
    def get_healthy_proxies(self, all_proxies: List[str]) -> List[str]:
        """Filter out blacklisted proxies from a list"""
        return [p for p in all_proxies if not self.is_blacklisted(p)]

# Initialize the proxy health tracker
proxy_health_tracker = ProxyHealthTracker()

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
        Make a GET request using optimal proxy selection.
        
        Args:
            url: URL to request
            headers: Optional headers dictionary
            params: Optional query parameters
            
        Returns:
            Response object from request
        """
        if headers is None:
            headers = {}
            
        # Always use a random user agent
        if 'User-Agent' not in headers:
            headers['User-Agent'] = get_random_user_agent()
            
        # Get available proxies
        available_proxies = proxy_manager.get_proxies()
        
        # Filter out blacklisted proxies
        healthy_proxies = proxy_health_tracker.get_healthy_proxies(available_proxies)
        
        if not healthy_proxies:
            # If all proxies are blacklisted, try a direct request
            logger.warning("All proxies are currently blacklisted, making direct request")
            try:
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
                return response
            except Exception as e:
                logger.error(f"Direct request failed: {str(e)}")
                error_response = requests.Response()
                error_response.status_code = 500
                error_response._content = b'{"error": "All proxies unavailable"}'
                error_response.url = url
                return error_response
        
        # Try proxies in random order to distribute load
        random.shuffle(healthy_proxies)
        
        last_error = None
        attempted_proxies = set()
        
        for attempt in range(self.max_retries):
            # Select a proxy
            if not healthy_proxies:
                logger.warning("No more healthy proxies available")
                break
            
            proxy = healthy_proxies.pop(0)
            attempted_proxies.add(proxy)
            
            try:
                logger.debug(f"Attempt {attempt+1} using proxy {proxy}")
                proxies = {"http": proxy, "https": proxy}
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    proxies=proxies,
                    timeout=self.timeout
                )
                
                # Record successful proxy use
                proxy_health_tracker.record_success(proxy)
                
                # Check if we got a valid response
                if response.status_code < 400:
                    return response
                    
                # Handle specific error codes for this proxy
                if response.status_code in [403, 429]:
                    logger.warning(f"Proxy {proxy} returned status code {response.status_code}")
                    proxy_health_tracker.record_failure(proxy)
                    continue
                    
            except ProxyError as e:
                logger.warning(f"Proxy error with {proxy}: {str(e)}")
                proxy_health_tracker.record_failure(proxy)
                last_error = e
                
            except Timeout as e:
                logger.warning(f"Timeout with proxy {proxy}: {str(e)}")
                proxy_health_tracker.record_failure(proxy)
                last_error = e
                
            except RequestException as e:
                logger.warning(f"Request error with proxy {proxy}: {str(e)}")
                proxy_health_tracker.record_failure(proxy)
                last_error = e
                
            except Exception as e:
                logger.error(f"Unexpected error with proxy {proxy}: {str(e)}")
                proxy_health_tracker.record_failure(proxy)
                last_error = e
        
        # If we've tried all proxies and none worked, try again with any healthy proxies
        healthy_proxies = [p for p in proxy_manager.get_proxies() if p not in attempted_proxies and not proxy_health_tracker.is_blacklisted(p)]
        
        if healthy_proxies and len(attempted_proxies) < len(proxy_manager.get_proxies()):
            logger.info(f"Trying with {len(healthy_proxies)} additional proxies")
            # Recursively try again with remaining proxies, but one fewer retry to prevent deep recursion
            return get(url, headers, params, max(1, self.max_retries - 1), self.timeout)
        
        # All retries failed, create a simple error response
        logger.error(f"All {self.max_retries} attempts with {len(attempted_proxies)} proxies failed when requesting {url}")
        
        # Create a simple error response to maintain a consistent interface
        error_response = requests.Response()
        error_response.status_code = 404
        error_response._content = b'{"error": "404 Not Found", "message": "The requested resource could not be reached"}'
        error_response.url = url
        
        # Attach the last error to the response
        if last_error:
            error_response.error = last_error
        
        return error_response
    
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
                                 threat_actor_type_selector: str = None,
                                 target_industries_selector: str = None,
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
        threat_actor_type_selector: CSS selector for threat actor type
        target_industries_selector: CSS selector for target industries
        use_proxies: Whether to use proxies for scraping
        use_headless_fallback: Whether to use headless browser as fallback
        max_retries: Maximum number of retries for failed requests
        
    Returns:
        List of dictionaries containing article information
    """
    # Special case handling for specific sources that need custom selectors
    # These are updated based on our selector analysis
    if source_name == "Palo Alto Unit 42" and article_selector == "article.type-post":
        # Update selectors based on our analysis
        article_selector = "article"
        title_selector = "h2.entry-title a"
        url_selector = "h2.entry-title a"
        date_selector = "time.entry-date"
        summary_selector = ".entry-summary"
    
    if source_name == "Google TAG" and article_selector == ".blogPost":
        # Update selectors based on our analysis
        article_selector = "article"
        title_selector = "h2 a"
        url_selector = "h2 a"
        date_selector = "time"
        summary_selector = "article p"
    
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
                published_date = datetime.now()
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
                    url_prefix=url_prefix,
                    threat_actor_type_selector=threat_actor_type_selector,
                    target_industries_selector=target_industries_selector
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