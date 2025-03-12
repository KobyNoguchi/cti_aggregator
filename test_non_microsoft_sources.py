#!/usr/bin/env python3
"""
Test script to verify if non-Microsoft threat intelligence sources are successfully scraping data.
This test checks multiple sources like Cisco Talos, Palo Alto Unit42, Zscaler, and Google TAG.
"""

import os
import sys
import logging
from datetime import datetime
import unittest
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cti_aggregator')))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join('cti_aggregator', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")
except ImportError:
    print("python-dotenv not installed, using existing environment variables")

class NonMicrosoftSourcesTest(unittest.TestCase):
    """Test non-Microsoft sources for the threat intelligence scrapers."""
    
    def setUp(self):
        """Set up the test environment."""
        self.sources = [
            {
                "name": "Cisco Talos",
                "url": "https://blog.talosintelligence.com/",
                "article_selector": "article.post",
                "title_selector": "h2.post-title a",
                "url_selector": "h2.post-title a",
                "date_selector": "time.published",
                "summary_selector": ".entry-content",
                "url_prefix": None
            },
            {
                "name": "Unit42",
                "url": "https://unit42.paloaltonetworks.com/category/threat-research/",
                "article_selector": "article.type-post",
                "title_selector": "h2.entry-title a",
                "url_selector": "h2.entry-title a",
                "date_selector": ".entry-date",
                "summary_selector": ".entry-summary",
                "url_prefix": None
            },
            {
                "name": "Zscaler",
                "url": "https://www.zscaler.com/blogs/security-research",
                "article_selector": ".blog-post",
                "title_selector": "h3.blog-title a",
                "url_selector": "h3.blog-title a",
                "date_selector": ".blog-date",
                "summary_selector": ".blog-summary",
                "url_prefix": "https://www.zscaler.com"
            },
            {
                "name": "Google TAG",
                "url": "https://blog.google/threat-analysis-group/",
                "article_selector": ".blogPost",
                "title_selector": "h2 a",
                "url_selector": "h2 a",
                "date_selector": ".blogPost__byline-info time",
                "summary_selector": ".post-snippet",
                "url_prefix": None
            }
        ]
    
    def test_source_availability(self):
        """Test if the source URLs are accessible."""
        import requests
        
        for source in self.sources:
            with self.subTest(source=source["name"]):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(source["url"], headers=headers)
                    self.assertEqual(response.status_code, 200, f"Failed to access {source['name']} at {source['url']}")
                    logger.info(f"✅ Successfully accessed {source['name']} at {source['url']}")
                except Exception as e:
                    logger.error(f"❌ Error accessing {source['name']} at {source['url']}: {str(e)}")
                    self.fail(f"Error accessing {source['name']}: {str(e)}")
    
    def test_enhanced_scraper_import(self):
        """Test if the enhanced scraper module can be imported."""
        try:
            from data_sources.free_enhanced_scraper import scrape_intelligence_articles, FreeEnhancedScraper
            logger.info("✅ Successfully imported free_enhanced_scraper module")
            self.assertTrue(True)
        except ImportError as e:
            logger.error(f"❌ Error importing free_enhanced_scraper module: {str(e)}")
            self.fail(f"Error importing free_enhanced_scraper module: {str(e)}")
    
    def test_scrape_non_microsoft_sources(self):
        """Test scraping data from non-Microsoft sources."""
        try:
            from data_sources.free_enhanced_scraper import scrape_intelligence_articles
            
            for source in self.sources:
                with self.subTest(source=source["name"]):
                    logger.info(f"Testing scraping for {source['name']}...")
                    
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
                    
                    # Check if any articles were scraped
                    self.assertIsNotNone(articles, f"No articles returned for {source['name']}")
                    self.assertTrue(len(articles) > 0, f"No articles found for {source['name']}")
                    
                    # Check the structure of the first article
                    first_article = articles[0]
                    self.assertIn('title', first_article, f"Title missing in article from {source['name']}")
                    self.assertIn('url', first_article, f"URL missing in article from {source['name']}")
                    self.assertIn('source', first_article, f"Source missing in article from {source['name']}")
                    self.assertIn('published_date', first_article, f"Published date missing in article from {source['name']}")
                    self.assertIn('summary', first_article, f"Summary missing in article from {source['name']}")
                    
                    # Log success
                    logger.info(f"✅ Successfully scraped {len(articles)} articles from {source['name']}")
                    logger.info(f"  First article: {first_article['title']}")
        except Exception as e:
            logger.error(f"❌ Error in scraping test: {str(e)}")
            self.fail(f"Error in scraping test: {str(e)}")
    
    def test_compare_with_microsoft(self):
        """Test to compare non-Microsoft sources with Microsoft Threat Intelligence."""
        try:
            # First check if we can import CrowdStrike modules
            try:
                import sys
                from data_sources.tailored_intelligence import fetch_tailored_intel
                has_crowdstrike = True
                logger.info("✅ Successfully imported tailored_intelligence module")
            except ImportError:
                has_crowdstrike = False
                logger.warning("⚠️ Could not import tailored_intelligence module, skipping Microsoft comparison")
            
            if has_crowdstrike:
                # Get Microsoft data
                ms_reports = fetch_tailored_intel(use_cache=True)
                self.assertIsNotNone(ms_reports, "No Microsoft Threat Intelligence data returned")
                self.assertTrue(len(ms_reports) > 0, "No Microsoft Threat Intelligence reports found")
                
                # Log Microsoft data count
                logger.info(f"✅ Successfully fetched {len(ms_reports)} Microsoft Threat Intelligence reports")
            
            # Now get non-Microsoft data
            from data_sources.free_enhanced_scraper import scrape_intelligence_articles
            
            non_ms_articles = []
            for source in self.sources:
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
                
                if articles:
                    non_ms_articles.extend(articles)
            
            # Check if non-Microsoft data exists
            self.assertTrue(len(non_ms_articles) > 0, "No non-Microsoft articles found")
            logger.info(f"✅ Successfully scraped {len(non_ms_articles)} non-Microsoft articles")
            
            # If we have both types of data, compare them
            if has_crowdstrike and len(ms_reports) > 0 and len(non_ms_articles) > 0:
                # Simple comparison: check if we have at least some percentage of non-Microsoft data
                # compared to Microsoft data
                non_ms_percentage = (len(non_ms_articles) / len(ms_reports)) * 100
                logger.info(f"Non-Microsoft data is {non_ms_percentage:.2f}% of the volume of Microsoft data")
                
                # This is a very basic success criteria - you may want to adjust this
                self.assertTrue(non_ms_percentage > 10, 
                               f"Non-Microsoft data ({len(non_ms_articles)} articles) is too small compared to Microsoft data ({len(ms_reports)} reports)")
                
                logger.info("✅ Non-Microsoft data volume is acceptable compared to Microsoft data")
        except Exception as e:
            logger.error(f"❌ Error in comparison test: {str(e)}")
            self.fail(f"Error in comparison test: {str(e)}")

def run_tests():
    """Run the tests."""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    print("==========================================")
    print("Testing Non-Microsoft Threat Intel Sources")
    print("==========================================")
    run_tests() 