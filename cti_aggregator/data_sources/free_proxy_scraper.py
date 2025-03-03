"""
Free Proxy Manager - Alternative to paid proxy services.

This module provides functionality to:
1. Fetch free proxies from various public sources
2. Validate proxies to ensure they work
3. Manage a pool of working proxies
4. Provide proxy rotation for web scraping
"""

import requests
import random
import time
import logging
import re
import concurrent.futures
import os
import json
import pickle
from typing import Dict, List, Optional, Tuple, Any, Set
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from requests.exceptions import RequestException, ProxyError, Timeout, ConnectionError

logger = logging.getLogger(__name__)

# Constants for optimization
MAX_PROXIES_TO_FETCH = 100  # Limit initial proxy pool size
PROXY_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proxy_cache.pkl')
PROXY_CACHE_EXPIRY = 60 * 60  # 1 hour in seconds

class FreeProxyManager:
    """Manages a pool of free proxies for web scraping."""
    
    def __init__(self, 
                 max_proxies: int = 20,
                 min_proxies: int = 5,
                 test_url: str = 'https://httpbin.org/ip',
                 timeout: int = 3,  # Reduced timeout for faster validation
                 refresh_interval: int = 30):
        """
        Initialize the proxy manager.
        
        Args:
            max_proxies: Maximum number of proxies to maintain in the pool
            min_proxies: Minimum number of valid proxies before refreshing
            test_url: URL used to test proxy validity
            timeout: Connection timeout for proxy testing
            refresh_interval: Minutes between proxy pool refreshes
        """
        self.proxies = set()
        self.working_proxies = set()
        self.blacklisted_proxies = set()
        self.max_proxies = max_proxies
        self.min_proxies = min_proxies
        self.test_url = test_url
        self.timeout = timeout
        self.refresh_interval = refresh_interval
        self.last_refresh = datetime.min
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/108.0.5359.112 Mobile/15E148 Safari/604.1'
        ]
        
        # Try to load cached proxies
        self._load_cached_proxies()
    
    def get_random_user_agent(self) -> str:
        """Return a random user agent from the list."""
        return random.choice(self.user_agents)
    
    def fetch_free_proxy_list(self) -> Set[str]:
        """
        Fetch proxies from free-proxy-list.net
        Returns a set of proxies in format ip:port
        """
        proxies = set()
        try:
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get('https://free-proxy-list.net/', headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'class': 'table table-striped table-bordered'})
                if table:
                    tbody = table.find('tbody')
                    count = 0
                    for row in tbody.find_all('tr'):
                        if count >= MAX_PROXIES_TO_FETCH:
                            break
                        
                        cols = row.find_all('td')
                        if len(cols) >= 8:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            https = cols[6].text.strip()
                            
                            if https == 'yes':  # Only use HTTPS proxies
                                proxy = f"{ip}:{port}"
                                proxies.add(proxy)
                                count += 1
            logger.info(f"Fetched {len(proxies)} proxies from free-proxy-list.net")
        except Exception as e:
            logger.error(f"Error fetching from free-proxy-list.net: {str(e)}")
        return proxies
    
    def fetch_geonode_proxies(self) -> Set[str]:
        """
        Fetch proxies from geonode.com free API
        Returns a set of proxies in format ip:port
        """
        proxies = set()
        try:
            url = f"https://proxylist.geonode.com/api/proxy-list?limit={MAX_PROXIES_TO_FETCH}&page=1&sort_by=lastChecked&sort_type=desc&filterUpTime=90&protocols=https"
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for proxy in data.get('data', []):
                    ip = proxy.get('ip')
                    port = proxy.get('port')
                    if ip and port:
                        proxies.add(f"{ip}:{port}")
            logger.info(f"Fetched {len(proxies)} proxies from geonode.com")
        except Exception as e:
            logger.error(f"Error fetching from geonode.com: {str(e)}")
        return proxies
    
    def fetch_proxyscrape_proxies(self) -> Set[str]:
        """
        Fetch proxies from proxyscrape.com
        Returns a set of proxies in format ip:port
        """
        proxies = set()
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                proxy_list = response.text.strip().split('\r\n')
                count = 0
                for proxy in proxy_list:
                    if count >= MAX_PROXIES_TO_FETCH:
                        break
                    
                    if proxy and ':' in proxy:
                        proxies.add(proxy)
                        count += 1
            logger.info(f"Fetched {len(proxies)} proxies from proxyscrape.com")
        except Exception as e:
            logger.error(f"Error fetching from proxyscrape.com: {str(e)}")
        return proxies
    
    def test_proxy(self, proxy: str) -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy: Proxy string in format ip:port
            
        Returns:
            bool: True if proxy is working, False otherwise
        """
        if proxy in self.blacklisted_proxies:
            return False
            
        proxies = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
        
        headers = {'User-Agent': self.get_random_user_agent()}
        
        try:
            start_time = time.time()
            response = requests.get(
                self.test_url, 
                proxies=proxies, 
                headers=headers, 
                timeout=self.timeout
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                logger.debug(f"Proxy {proxy} is working (response time: {elapsed:.2f}s)")
                return True
            else:
                logger.debug(f"Proxy {proxy} returned status code {response.status_code}")
                return False
        except Exception as e:
            logger.debug(f"Proxy {proxy} failed: {str(e)}")
            return False
    
    def validate_proxies(self, proxy_list: Set[str]) -> None:
        """
        Test multiple proxies concurrently and add working ones to the pool.
        
        Args:
            proxy_list: Set of proxy strings to test
        """
        # Use more workers but with a shorter timeout for faster validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            future_to_proxy = {executor.submit(self.test_proxy, proxy): proxy for proxy in proxy_list}
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        self.working_proxies.add(proxy)
                        if len(self.working_proxies) >= self.max_proxies:
                            break
                except Exception as e:
                    logger.error(f"Error validating proxy {proxy}: {str(e)}")
    
    def _save_cached_proxies(self) -> None:
        """Save working proxies to a cache file"""
        try:
            cache_data = {
                'timestamp': datetime.now().timestamp(),
                'working_proxies': list(self.working_proxies),
                'blacklisted_proxies': list(self.blacklisted_proxies)
            }
            with open(PROXY_CACHE_FILE, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"Saved {len(self.working_proxies)} proxies to cache")
        except Exception as e:
            logger.error(f"Error saving proxy cache: {str(e)}")
    
    def _load_cached_proxies(self) -> None:
        """Load working proxies from a cache file if it exists and is recent"""
        try:
            if os.path.exists(PROXY_CACHE_FILE):
                with open(PROXY_CACHE_FILE, 'rb') as f:
                    cache_data = pickle.load(f)
                
                timestamp = cache_data.get('timestamp', 0)
                age = datetime.now().timestamp() - timestamp
                
                # Only use cache if it's fresh
                if age < PROXY_CACHE_EXPIRY:
                    self.working_proxies = set(cache_data.get('working_proxies', []))
                    self.blacklisted_proxies = set(cache_data.get('blacklisted_proxies', []))
                    self.last_refresh = datetime.fromtimestamp(timestamp)
                    logger.info(f"Loaded {len(self.working_proxies)} proxies from cache (age: {age:.1f}s)")
                    return
                else:
                    logger.info(f"Proxy cache expired (age: {age:.1f}s)")
        except Exception as e:
            logger.error(f"Error loading proxy cache: {str(e)}")
    
    def refresh_proxies(self, force: bool = False) -> None:
        """
        Refresh the proxy pool if needed.
        
        Args:
            force: Force refresh regardless of conditions
        """
        now = datetime.now()
        time_since_refresh = now - self.last_refresh
        
        # Skip refresh if we have enough working proxies and cache is fresh
        if not force and len(self.working_proxies) >= self.min_proxies and time_since_refresh < timedelta(minutes=self.refresh_interval):
            logger.info(f"Using {len(self.working_proxies)} cached proxies (last refresh: {time_since_refresh.total_seconds():.1f}s ago)")
            return
            
        logger.info("Refreshing proxy pool...")
        self.proxies = set()
        
        # Keep track of previously working proxies
        old_working = self.working_proxies.copy()
        
        # Fetch only from most reliable source first to save time
        self.proxies.update(self.fetch_free_proxy_list())
        
        # If we don't have enough proxies, try other sources
        if len(self.proxies) < self.max_proxies * 3:  # Aim for 3x the needed proxies before validation
            self.proxies.update(self.fetch_proxyscrape_proxies())
            
        # Only try geonode as a last resort as it's often less reliable
        if len(self.proxies) < self.max_proxies * 2:
            self.proxies.update(self.fetch_geonode_proxies())
        
        # Remove blacklisted proxies
        self.proxies = self.proxies - self.blacklisted_proxies
        
        # Reset working proxies
        self.working_proxies = set()
        
        # Re-test previously working proxies first since they're more likely to work
        self.validate_proxies(old_working)
        
        # Test new proxies if we need more
        remaining_slots = self.max_proxies - len(self.working_proxies)
        if remaining_slots > 0:
            new_proxies = self.proxies - old_working
            # Only test a subset of new proxies to save time
            test_proxies = set(random.sample(list(new_proxies), min(len(new_proxies), remaining_slots * 3)))
            self.validate_proxies(test_proxies)
        
        self.last_refresh = now
        logger.info(f"Proxy pool refreshed. {len(self.working_proxies)} working proxies available.")
        
        # Save to cache for faster future startups
        self._save_cached_proxies()
    
    def get_proxy(self) -> Optional[str]:
        """
        Get a random working proxy from the pool.
        
        Returns:
            Optional[str]: A proxy string in format ip:port, or None if no working proxies
        """
        if len(self.working_proxies) < self.min_proxies:
            self.refresh_proxies()
            
        if not self.working_proxies:
            return None
            
        return random.choice(list(self.working_proxies))
    
    def get_request_session(self) -> Tuple[Optional[requests.Session], Optional[Dict]]:
        """
        Get a request session with a random proxy.
        
        Returns:
            Tuple containing:
            - requests.Session: Prepared session object
            - Dict: Proxy configuration dict or None if no proxy available
        """
        session = requests.Session()
        proxy = self.get_proxy()
        proxy_dict = None
        
        if proxy:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}'
            }
            session.proxies = proxy_dict
        
        session.headers.update({'User-Agent': self.get_random_user_agent()})
        return session, proxy_dict
    
    def mark_proxy_failed(self, proxy: str) -> None:
        """
        Mark a proxy as failed and remove it from the working pool.
        
        Args:
            proxy: Proxy string in format ip:port
        """
        if proxy:
            # Extract IP:port from proxy URL if needed
            match = re.search(r'://([^/]+)', proxy)
            if match:
                proxy = match.group(1)
                
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
            self.blacklisted_proxies.add(proxy)
            
            # Update the cache
            self._save_cached_proxies()

# Create a singleton instance for application-wide use
proxy_manager = FreeProxyManager()

def get(url: str, headers: Optional[Dict[str, str]] = None, 
        params: Optional[Dict[str, Any]] = None, 
        max_retries: int = 3, timeout: int = 30) -> requests.Response:
    """
    Make a GET request using a rotating free proxy.
    
    Args:
        url: URL to request
        headers: Optional headers to include
        params: Optional query parameters
        max_retries: Maximum number of retries
        timeout: Request timeout in seconds
        
    Returns:
        Response object from the request
    """
    if headers is None:
        headers = {}
    
    # Make sure we have proxies available
    proxy_manager.refresh_proxies()
    
    # Track which proxies we've already tried in this request
    tried_proxies = set()
    last_error = None
    
    for attempt in range(max_retries):
        session, proxy_dict = proxy_manager.get_request_session()
        
        # If we got a proxy we've already tried, get a different one
        if proxy_dict and str(proxy_dict.get('https', '')) in tried_proxies:
            continue
            
        if proxy_dict:
            proxy_url = proxy_dict.get('https', 'direct')
            tried_proxies.add(str(proxy_url))
            logger.info(f"Attempt {attempt+1}/{max_retries} using proxy {proxy_url}")
        else:
            logger.info(f"Attempt {attempt+1}/{max_retries} using direct connection (no proxy available)")
        
        try:
            response = session.get(url, headers=headers, params=params, timeout=timeout)
            
            # Check if we got a valid response
            if response.status_code < 400:
                return response
                
            # Handle specific status codes
            if response.status_code == 403 or response.status_code == 429:
                logger.warning(f"Request blocked with status code {response.status_code}")
                
                # If using a proxy, mark it as failed
                if proxy_dict:
                    proxy_url = proxy_dict.get('https')
                    if proxy_url:
                        proxy_manager.mark_proxy_failed(proxy_url)
                
                # Wait before retrying
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
                
        except (ProxyError, ConnectionError) as e:
            # The proxy is not working properly
            logger.warning(f"Proxy error: {str(e)}")
            if proxy_dict:
                proxy_url = proxy_dict.get('https')
                if proxy_url:
                    proxy_manager.mark_proxy_failed(proxy_url)
            last_error = e
            
        except Timeout as e:
            logger.warning(f"Request timeout: {str(e)}")
            last_error = e
            
        except RequestException as e:
            logger.warning(f"Request failed: {str(e)}")
            last_error = e
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            last_error = e
    
    # All retries failed, create a dummy response
    logger.error(f"All {max_retries} attempts failed when requesting {url}")
    
    # Create a dummy response to maintain a consistent interface
    dummy_response = requests.Response()
    dummy_response.status_code = 500
    dummy_response._content = b'{"error": "All proxy attempts failed"}'
    dummy_response.url = url
    
    # Attach the last error to the response
    if last_error:
        dummy_response.error = last_error
    
    return dummy_response

def get_soup(url: str, headers: Optional[Dict[str, str]] = None, 
           params: Optional[Dict[str, Any]] = None, 
           max_retries: int = 3) -> Optional[BeautifulSoup]:
    """
    Make a GET request and return BeautifulSoup object.
    
    Args:
        url: URL to request
        headers: Optional headers to include
        params: Optional query parameters
        max_retries: Maximum number of retries
        
    Returns:
        BeautifulSoup object or None if request failed
    """
    response = get(url, headers, params, max_retries)
    
    if response.status_code < 400:
        try:
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return None
    else:
        logger.error(f"Failed to get soup for {url}, status code: {response.status_code}")
        return None

def free_proxy_example():
    """Example usage of the free proxy system."""
    # Initialize and refresh the proxy pool
    proxy_manager.refresh_proxies(force=True)
    
    # Make a request through a proxy
    url = "https://httpbin.org/ip"
    print(f"Making a request to {url}")
    
    response = get(url)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response content: {response.text}")
        
    # Get a soup object
    url = "https://example.com"
    print(f"Getting soup from {url}")
    
    soup = get_soup(url)
    if soup:
        title = soup.find('title')
        if title:
            print(f"Page title: {title.text}")
    
    # Get information about the proxy pool
    print(f"Working proxies: {len(proxy_manager.working_proxies)}")
    print(f"Blacklisted proxies: {len(proxy_manager.blacklisted_proxies)}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the example
    free_proxy_example() 