"""
Bright Data integration for enhanced web scraping capabilities.

This module provides a wrapper around Bright Data's proxy network to improve
the reliability and success rate of web scraping operations. It helps to avoid
rate limiting, IP blocks, and CAPTCHA challenges that may otherwise prevent
successful data collection.
"""

import os
import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Bright Data credentials - Replace with your own
BRIGHT_DATA_USERNAME = "demo_username" # Replace with your actual username in production
BRIGHT_DATA_PASSWORD = "demo_password" # Replace with your actual password in production

# Test mode for development
BRIGHT_DATA_TEST_MODE = True  # Set to False in production

# Bright Data proxy endpoints
PROXY_ENDPOINTS = {
    'residential': f'http://{BRIGHT_DATA_USERNAME}:{BRIGHT_DATA_PASSWORD}@brd.superproxy.io:22225',
    'datacenter': f'http://{BRIGHT_DATA_USERNAME}:{BRIGHT_DATA_PASSWORD}@brd.superproxy.io:22225',
    'mobile': f'http://{BRIGHT_DATA_USERNAME}:{BRIGHT_DATA_PASSWORD}@brd.superproxy.io:24000'
}

class BrightDataScraper:
    """Wrapper for making requests through Bright Data proxy network."""
    
    def __init__(self, zone: str = 'residential', country: Optional[str] = None, city: Optional[str] = None):
        """
        Initialize the Bright Data scraper.
        
        Args:
            zone: The proxy zone to use ('residential', 'datacenter', or 'mobile')
            country: Two-letter country code for geo-targeting
            city: City name for geo-targeting
        """
        self.zone = zone
        self.country = country
        self.city = city
        self.session = requests.Session()
        
        # Build the proxy URL with optional parameters
        self.proxy_url = PROXY_ENDPOINTS.get(zone, PROXY_ENDPOINTS['residential'])
        if country:
            self.proxy_url += f';country={country}'
        if city:
            self.proxy_url += f';city={city}'
            
        # Set the proxy for all requests in this session
        self.session.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url.replace('http://', 'https://')
        }
        
        logger.info(f"Initialized Bright Data scraper with {zone} zone")
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
            params: Optional[Dict[str, Any]] = None, timeout: int = 30) -> requests.Response:
        """
        Make a GET request through the Bright Data proxy.
        
        Args:
            url: The URL to request
            headers: Optional HTTP headers
            params: Optional query parameters
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response object
        """
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            logger.info(f"Making Bright Data request to {url}")
            response = self.session.get(
                url,
                headers=default_headers,
                params=params,
                timeout=timeout
            )
            logger.info(f"Bright Data request completed with status {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"Bright Data request failed: {str(e)}")
            # Create a dummy response to return consistent interface
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

# Function to check if Bright Data is properly configured
def is_bright_data_configured() -> bool:
    """
    Check if Bright Data credentials are properly configured.
    In test mode, returns True for demo credentials to allow testing.
    """
    if BRIGHT_DATA_TEST_MODE:
        logger.info("Bright Data running in TEST MODE with demo credentials")
        return True
        
    is_configured = (
        BRIGHT_DATA_USERNAME != "YOUR_USERNAME" and
        BRIGHT_DATA_PASSWORD != "YOUR_PASSWORD" and
        BRIGHT_DATA_USERNAME != "demo_username" and 
        BRIGHT_DATA_PASSWORD != "demo_password" and
        BRIGHT_DATA_USERNAME and
        BRIGHT_DATA_PASSWORD
    )
    
    if not is_configured:
        logger.warning("Bright Data is not properly configured with real credentials")
    
    return is_configured

# Example usage function to demonstrate how to use this module
def example_usage():
    """Example of how to use the BrightDataScraper."""
    if not is_bright_data_configured():
        print("Bright Data is not configured. Please set your credentials.")
        return
    
    scraper = BrightDataScraper(zone='residential')
    response = scraper.get('https://httpbin.org/ip')
    
    if response.status_code == 200:
        print(f"Request successful! IP: {response.json().get('origin')}")
    else:
        print(f"Request failed with status: {response.status_code}")

    # Example with BeautifulSoup
    soup = scraper.get_soup('https://www.example.com')
    if soup:
        title = soup.title.string if soup.title else "No title found"
        print(f"Page title: {title}")

if __name__ == "__main__":
    # Set up logging for standalone usage
    logging.basicConfig(level=logging.INFO)
    example_usage() 