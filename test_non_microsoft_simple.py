#!/usr/bin/env python3
"""
Simple standalone script to test if a non-Microsoft threat intelligence source is accessible.
This can be used for quick verification without running the full test suite.
"""

import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cti_aggregator')))

# Define common user agents for browser simulation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

def test_unit42():
    """Test if Palo Alto Unit42 intelligence source is accessible and can be scraped."""
    source_name = "Unit42"
    url = "https://unit42.paloaltonetworks.com/category/threat-research/"
    
    print(f"Testing {source_name} source at {url}")
    
    # Test if the URL is accessible
    try:
        headers = {
            'User-Agent': get_random_user_agent()
        }
        
        print(f"Sending request to {url}...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to access {source_name}: Status code {response.status_code}")
            return False
            
        print(f"✅ Successfully accessed {source_name}")
        
        # Parse the HTML with BeautifulSoup
        print("Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Define the selectors for Unit42 blog
        article_selector = "article.type-post"
        title_selector = "h2.entry-title a"
        
        # Find all the article elements
        articles = soup.select(article_selector)
        
        if not articles:
            print(f"❌ No articles found on {source_name} page using selector: {article_selector}")
            print("Analyzing page structure...")
            
            # Try to find a list of h2 tags that might contain article titles
            h2_tags = soup.find_all('h2')
            if h2_tags:
                print(f"Found {len(h2_tags)} h2 tags on the page. First 3:")
                for i, h2 in enumerate(h2_tags[:3]):
                    print(f"  {i+1}. {h2.text.strip()}")
                    print(f"     HTML: {h2}")
            
            # Look for common article containers
            containers = [
                soup.select("article"),
                soup.select(".post"),
                soup.select(".entry"),
                soup.select(".card"),
                soup.select(".blog-post")
            ]
            
            for container_name, container_items in zip(
                ["article tags", ".post class", ".entry class", ".card class", ".blog-post class"],
                containers
            ):
                if container_items:
                    print(f"Found {len(container_items)} items with {container_name}")
                    break
            
            return False
            
        print(f"✅ Found {len(articles)} articles on {source_name} page")
        
        # Extract information from the first few articles
        extracted_articles = []
        
        for article in articles[:3]:  # Process first 3 articles
            try:
                # Extract title
                title_elem = article.select_one(title_selector)
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # Extract URL
                article_url = title_elem.get('href')
                
                # Extract date (if available)
                date_elem = article.select_one(".entry-date")
                published_date = date_elem.text.strip() if date_elem else "Date not found"
                
                # Extract summary (if available)
                summary_elem = article.select_one(".entry-summary")
                summary = summary_elem.text.strip() if summary_elem else "Summary not found"
                summary = summary[:100] + "..." if len(summary) > 100 else summary
                
                extracted_articles.append({
                    'title': title,
                    'url': article_url,
                    'published_date': published_date,
                    'summary': summary
                })
                
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue
        
        # Display the extracted articles
        if extracted_articles:
            print(f"\n✅ Successfully extracted {len(extracted_articles)} articles from {source_name}:")
            for i, article in enumerate(extracted_articles, 1):
                print(f"\nArticle {i}:")
                print(f"  Title: {article['title']}")
                print(f"  URL: {article['url']}")
                print(f"  Published: {article['published_date']}")
                print(f"  Summary: {article['summary']}")
            
            print(f"\n✅ The {source_name} source is working correctly!")
            return True
        else:
            print(f"❌ Failed to extract any articles from {source_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {source_name}: {str(e)}")
        return False

def test_zscaler():
    """Test if Zscaler intelligence source is accessible and can be scraped."""
    source_name = "Zscaler"
    url = "https://www.zscaler.com/blogs/security-research"
    
    print(f"Testing {source_name} source at {url}")
    
    # Test if the URL is accessible
    try:
        headers = {
            'User-Agent': get_random_user_agent()
        }
        
        print(f"Sending request to {url}...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to access {source_name}: Status code {response.status_code}")
            return False
            
        print(f"✅ Successfully accessed {source_name}")
        
        # Parse the HTML with BeautifulSoup
        print("Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Define the selectors for Zscaler blog
        article_selector = ".blog-post"
        title_selector = "h3.blog-title a"
        
        # Find all the article elements
        articles = soup.select(article_selector)
        
        if not articles:
            print(f"❌ No articles found on {source_name} page using selector: {article_selector}")
            print("Analyzing page structure...")
            
            # Try to find a list of h3 tags that might contain article titles
            h3_tags = soup.find_all('h3')
            if h3_tags:
                print(f"Found {len(h3_tags)} h3 tags on the page. First 3:")
                for i, h3 in enumerate(h3_tags[:3]):
                    print(f"  {i+1}. {h3.text.strip()}")
            
            return False
            
        print(f"✅ Found {len(articles)} articles on {source_name} page")
        
        # Extract information from the first few articles
        extracted_articles = []
        
        for article in articles[:3]:  # Process first 3 articles
            try:
                # Extract title
                title_elem = article.select_one(title_selector)
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # Extract URL
                article_url = title_elem.get('href')
                if article_url and not article_url.startswith(('http://', 'https://')):
                    article_url = "https://www.zscaler.com" + article_url
                
                # Extract date (if available)
                date_elem = article.select_one(".blog-date")
                published_date = date_elem.text.strip() if date_elem else "Date not found"
                
                # Extract summary (if available)
                summary_elem = article.select_one(".blog-summary")
                summary = summary_elem.text.strip() if summary_elem else "Summary not found"
                summary = summary[:100] + "..." if len(summary) > 100 else summary
                
                extracted_articles.append({
                    'title': title,
                    'url': article_url,
                    'published_date': published_date,
                    'summary': summary
                })
                
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue
        
        # Display the extracted articles
        if extracted_articles:
            print(f"\n✅ Successfully extracted {len(extracted_articles)} articles from {source_name}:")
            for i, article in enumerate(extracted_articles, 1):
                print(f"\nArticle {i}:")
                print(f"  Title: {article['title']}")
                print(f"  URL: {article['url']}")
                print(f"  Published: {article['published_date']}")
                print(f"  Summary: {article['summary']}")
            
            print(f"\n✅ The {source_name} source is working correctly!")
            return True
        else:
            print(f"❌ Failed to extract any articles from {source_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {source_name}: {str(e)}")
        return False

def main():
    """Run tests for different non-Microsoft sources."""
    print("\n==============================================")
    print("Simple Non-Microsoft Threat Intel Source Test")
    print("==============================================\n")
    
    # Test at least one source directly
    success1 = test_unit42()
    print("\n==============================================")
    
    success2 = test_zscaler()
    print("\n==============================================")
    
    # Overall success if at least one source works
    success = success1 or success2
    
    print(f"Test {'PASSED' if success else 'FAILED'}")
    print("==============================================\n")
    
    # Try to import and test the enhanced scraper if available
    try:
        print("Attempting to use the enhanced scraper...\n")
        
        # Add path to cti_aggregator
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cti_aggregator'))
        
        from data_sources.free_enhanced_scraper import scrape_intelligence_articles
        
        print("Enhanced scraper module imported successfully")
        
        # Use the enhanced scraper to fetch articles from Unit42
        source = {
            "name": "Unit42",
            "url": "https://unit42.paloaltonetworks.com/category/threat-research/",
            "article_selector": "article.type-post",
            "title_selector": "h2.entry-title a",
            "url_selector": "h2.entry-title a",
            "date_selector": ".entry-date",
            "summary_selector": ".entry-summary",
            "url_prefix": None
        }
        
        print(f"Scraping {source['name']} using enhanced scraper...")
        
        articles = scrape_intelligence_articles(
            url=source["url"],
            source_name=source["name"],
            article_selector=source["article_selector"],
            title_selector=source["title_selector"],
            url_selector=source["url_selector"],
            date_selector=source["date_selector"],
            summary_selector=source["summary_selector"],
            url_prefix=source["url_prefix"],
            use_proxies=True,
            use_headless_fallback=True,
            max_retries=2
        )
        
        if articles and len(articles) > 0:
            print(f"\n✅ Enhanced scraper successfully extracted {len(articles)} articles")
            print("First article details:")
            print(f"  Title: {articles[0]['title']}")
            print(f"  URL: {articles[0]['url']}")
            print(f"  Published: {articles[0]['published_date']}")
            print(f"  Summary: {articles[0]['summary'][:100]}...")
            
            print("\n✅ Enhanced scraper is working correctly!")
        else:
            print("❌ Enhanced scraper failed to extract articles")
            
    except ImportError:
        print("❌ Enhanced scraper module not found, skipping enhanced test")
    except Exception as e:
        print(f"❌ Error using enhanced scraper: {str(e)}")

if __name__ == "__main__":
    main() 