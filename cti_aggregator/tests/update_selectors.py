#!/usr/bin/env python3
"""
Script to update the selectors for the intelligence scrapers.
This script will check the current selectors and update them if needed.
"""

import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the data_sources directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_sources_dir = os.path.join(parent_dir, 'data_sources')
sys.path.insert(0, data_sources_dir)

# Define the sources and their current selectors
SOURCES = [
    {
        "name": "Cisco Talos",
        "url": "https://blog.talosintelligence.com/",
        "current_selectors": {
            "article_selector": "article.post",
            "title_selector": "h2.post-title a",
            "url_selector": "h2.post-title a",
            "date_selector": "time.published",
            "summary_selector": ".entry-content"
        }
    },
    {
        "name": "Palo Alto Unit 42",
        "url": "https://unit42.paloaltonetworks.com/",
        "current_selectors": {
            "article_selector": "article.type-post",
            "title_selector": "h2.entry-title a",
            "url_selector": "h2.entry-title a",
            "date_selector": ".entry-date",
            "summary_selector": ".entry-summary"
        }
    },
    {
        "name": "Mandiant",
        "url": "https://www.mandiant.com/resources/blog",
        "current_selectors": {
            "article_selector": ".blog-card",
            "title_selector": ".blog-card__title a",
            "url_selector": ".blog-card__title a",
            "date_selector": ".blog-card__date",
            "summary_selector": ".blog-card__description"
        }
    },
    {
        "name": "Zscaler",
        "url": "https://www.zscaler.com/blogs/security-research",
        "current_selectors": {
            "article_selector": ".blog-post",
            "title_selector": "h3.blog-title a",
            "url_selector": "h3.blog-title a",
            "date_selector": ".blog-date",
            "summary_selector": ".blog-summary"
        }
    },
    {
        "name": "Google TAG",
        "url": "https://blog.google/threat-analysis-group/",
        "current_selectors": {
            "article_selector": ".blogPost",
            "title_selector": "h2 a",
            "url_selector": "h2 a",
            "date_selector": ".blogPost__byline-info time",
            "summary_selector": ".post-snippet"
        }
    }
]

def check_selector_with_requests(url, selector):
    """Check if a selector works using requests and BeautifulSoup"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return False, f"Failed to fetch page: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select(selector)
        return len(elements) > 0, f"Found {len(elements)} elements"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_selector_with_selenium(url, selector):
    """Check if a selector works using Selenium"""
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if the selector works
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        return len(elements) > 0, f"Found {len(elements)} elements"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if driver:
            driver.quit()

def suggest_new_selectors(url, source_name):
    """Suggest new selectors for a source"""
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for common article selectors
        article_selectors = [
            "article", ".post", ".blog-post", ".blog-card", ".blogPost", 
            ".entry", ".article", ".post-item", ".card"
        ]
        
        # Check each selector
        suggestions = {
            "article_selector": None,
            "title_selector": None,
            "url_selector": None,
            "date_selector": None,
            "summary_selector": None
        }
        
        # Find article elements
        for selector in article_selectors:
            elements = soup.select(selector)
            if len(elements) > 0:
                suggestions["article_selector"] = selector
                
                # Try to find title, URL, date, and summary within the first article
                article = elements[0]
                
                # Look for title and URL
                title_elements = article.select("h1 a, h2 a, h3 a, .title a, .post-title a")
                if title_elements:
                    suggestions["title_selector"] = f"{selector} {title_elements[0].name}"
                    suggestions["url_selector"] = f"{selector} {title_elements[0].name}"
                
                # Look for date
                date_elements = article.select("time, .date, .published, .post-date")
                if date_elements:
                    suggestions["date_selector"] = f"{selector} {date_elements[0].name}"
                
                # Look for summary
                summary_elements = article.select("p, .summary, .excerpt, .description")
                if summary_elements:
                    suggestions["summary_selector"] = f"{selector} {summary_elements[0].name}"
                
                break
        
        return suggestions
    except Exception as e:
        logger.error(f"Error suggesting selectors for {source_name}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    """Main function to check and update selectors"""
    logger.info("Checking and updating selectors for intelligence sources...")
    
    for source in SOURCES:
        logger.info(f"\nChecking selectors for {source['name']}...")
        
        # Check if the current selectors work
        article_selector = source["current_selectors"]["article_selector"]
        works, message = check_selector_with_requests(source["url"], article_selector)
        
        if works:
            logger.info(f"✅ Current article selector works: {article_selector} - {message}")
            continue
        
        logger.warning(f"❌ Current article selector doesn't work: {article_selector} - {message}")
        
        # Try with Selenium
        works, message = check_selector_with_selenium(source["url"], article_selector)
        if works:
            logger.info(f"✅ Current article selector works with Selenium: {article_selector} - {message}")
            continue
        
        logger.warning(f"❌ Current article selector doesn't work with Selenium: {article_selector} - {message}")
        
        # Suggest new selectors
        logger.info(f"Suggesting new selectors for {source['name']}...")
        suggestions = suggest_new_selectors(source["url"], source["name"])
        
        if suggestions and suggestions["article_selector"]:
            logger.info(f"Suggested selectors for {source['name']}:")
            for key, value in suggestions.items():
                if value:
                    logger.info(f"  {key}: {value}")
        else:
            logger.warning(f"Could not suggest selectors for {source['name']}")
    
    logger.info("\nSelector check completed.")

if __name__ == "__main__":
    main() 