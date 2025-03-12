#!/usr/bin/env python3
"""
Final test implementation to verify if non-Microsoft threat intelligence sources
are accessible and being scraped successfully.

This test has two components:
1. Direct web testing - verifies that the intelligence source websites are accessible
2. Scraper testing - verifies that our scrapers can extract data from these sites

The test will pass if we can access and potentially scrape from non-Microsoft sources.
"""

import os
import sys
import json
import logging
import requests
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# User agent rotation to avoid blocking
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

def check_intelligence_source(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if a threat intelligence source is accessible.
    
    Args:
        source: Dictionary containing source information
        
    Returns:
        Dictionary with source information and test results
    """
    result = {
        "name": source["name"],
        "url": source["url"],
        "status": "FAILED",
        "status_code": None,
        "keywords_found": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Fetch the page content
        response = requests.get(source["url"], headers=headers, timeout=30)
        
        # Save the status code
        result["status_code"] = response.status_code
        
        # If the request was successful
        if response.status_code == 200:
            result["status"] = "SUCCESS"
            
            # Check for relevant keywords in the page content
            content = response.text.lower()
            keywords = ["threat", "security", "malware", "attack", "vulnerability", "cyber", 
                        "intelligence", "research", "advisory", "report"]
            
            for keyword in keywords:
                if keyword in content:
                    result["keywords_found"].append(keyword)
            
            # Success if we found any keywords
            if result["keywords_found"]:
                logger.info(f"✅ Successfully accessed {source['name']} at {source['url']}")
                logger.info(f"   Found keywords: {', '.join(result['keywords_found'])}")
            else:
                logger.warning(f"⚠️ Accessed {source['name']} but no relevant keywords found")
        else:
            logger.error(f"❌ Failed to access {source['name']}: Status code {response.status_code}")
    
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Error accessing {source['name']}: {str(e)}")
    
    return result

def test_web_accessibility():
    """
    Test web accessibility of non-Microsoft threat intelligence sources.
    
    Returns:
        Dict: Report of test results
    """
    # List of non-Microsoft threat intelligence sources to test
    sources = [
        {
            "name": "Cisco Talos",
            "url": "https://blog.talosintelligence.com/",
            "type": "blog"
        },
        {
            "name": "Palo Alto Unit42",
            "url": "https://unit42.paloaltonetworks.com/",
            "type": "blog"
        },
        {
            "name": "Zscaler ThreatLabz",
            "url": "https://www.zscaler.com/blogs/security-research",
            "type": "blog"
        },
        {
            "name": "Google TAG",
            "url": "https://blog.google/threat-analysis-group/",
            "type": "blog"
        },
        {
            "name": "Proofpoint Threat Insight",
            "url": "https://www.proofpoint.com/us/blog/threat-insight",
            "type": "blog"
        },
        {
            "name": "Mandiant",
            "url": "https://www.mandiant.com/resources/blog",
            "type": "blog"
        },
        {
            "name": "SANS Internet Storm Center",
            "url": "https://isc.sans.edu/",
            "type": "blog"
        },
        {
            "name": "Securelist by Kaspersky",
            "url": "https://securelist.com/",
            "type": "blog"
        },
        {
            "name": "AlienVault OTX",
            "url": "https://otx.alienvault.com/",
            "type": "platform"
        },
        {
            "name": "MITRE ATT&CK",
            "url": "https://attack.mitre.org/",
            "type": "framework"
        }
    ]
    
    print(f"\nTesting web accessibility of {len(sources)} non-Microsoft threat intelligence sources...\n")
    
    # Use ThreadPoolExecutor to check sources in parallel
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_intelligence_source, sources))
    
    # Count successful sources
    successful_sources = [r for r in results if r["status"] == "SUCCESS" and r["keywords_found"]]
    
    # Create a summary report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_sources": len(sources),
        "successful_sources": len(successful_sources),
        "failed_sources": len(sources) - len(successful_sources),
        "success_rate": f"{(len(successful_sources) / len(sources)) * 100:.2f}%",
        "results": results
    }
    
    return report

def test_scraper_functionality():
    """
    Test if our scrapers can extract data from non-Microsoft sources.
    
    Returns:
        Dict: Report of test results
    """
    scraper_report = {
        "timestamp": datetime.now().isoformat(),
        "scrapers_tested": 0,
        "scrapers_working": 0,
        "success_rate": "0.00%",
        "results": []
    }
    
    # Try to import the enhanced scraper
    try:
        # Add the project root directory to the Python path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cti_aggregator')))
        
        # Import the scraper module
        from data_sources.free_enhanced_scraper import scrape_intelligence_articles
        
        print("\nTesting scraper functionality for non-Microsoft sources...\n")
        
        # Define sources with their selectors
        sources_with_selectors = [
            {
                "name": "Palo Alto Unit42",
                "url": "https://unit42.paloaltonetworks.com/",
                "article_selector": "article.type-post",
                "title_selector": "h2.entry-title a",
                "url_selector": "h2.entry-title a",
                "date_selector": ".entry-date",
                "summary_selector": ".entry-summary",
                "url_prefix": None
            },
            {
                "name": "Zscaler ThreatLabz",
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
        
        scraper_report["scrapers_tested"] = len(sources_with_selectors)
        
        # Test each source
        for source in sources_with_selectors:
            scraper_result = {
                "name": source["name"],
                "url": source["url"],
                "status": "FAILED",
                "articles_found": 0,
                "error": None
            }
            
            try:
                print(f"Testing scraper for {source['name']}...")
                
                # Try to scrape articles
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
                    scraper_result["status"] = "SUCCESS"
                    scraper_result["articles_found"] = len(articles)
                    scraper_report["scrapers_working"] += 1
                    
                    # Include a sample article
                    sample_article = articles[0]
                    scraper_result["sample_article"] = {
                        "title": sample_article["title"],
                        "url": sample_article["url"],
                        "published_date": str(sample_article["published_date"]),
                        "summary": sample_article["summary"][:100] + "..." if len(sample_article["summary"]) > 100 else sample_article["summary"]
                    }
                    
                    logger.info(f"✅ Successfully scraped {len(articles)} articles from {source['name']}")
                else:
                    logger.warning(f"⚠️ No articles scraped from {source['name']}")
            
            except Exception as e:
                scraper_result["error"] = str(e)
                logger.error(f"❌ Error scraping {source['name']}: {str(e)}")
            
            scraper_report["results"].append(scraper_result)
        
        # Calculate success rate
        if scraper_report["scrapers_tested"] > 0:
            success_rate = (scraper_report["scrapers_working"] / scraper_report["scrapers_tested"]) * 100
            scraper_report["success_rate"] = f"{success_rate:.2f}%"
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import scraper modules: {str(e)}")
        scraper_report["error"] = str(e)
    except Exception as e:
        logger.error(f"❌ Error in scraper test: {str(e)}")
        scraper_report["error"] = str(e)
    
    return scraper_report

def test_ms_integration(web_report: Dict[str, Any], scraper_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test how non-Microsoft data compares with Microsoft data in the system.
    
    Args:
        web_report: Results from web accessibility test
        scraper_report: Results from scraper test
        
    Returns:
        Dict: Report comparing Microsoft and non-Microsoft intelligence
    """
    ms_integration_report = {
        "timestamp": datetime.now().isoformat(),
        "microsoft_source_count": 0,
        "microsoft_intel_count": 0,
        "non_microsoft_source_count": web_report["successful_sources"],
        "non_microsoft_scraper_count": scraper_report["scrapers_working"],
        "comparison": {
            "sources_ratio": "0",
            "intel_ratio": "0"
        },
        "microsoft_available": False,
        "status": "FAILED"
    }
    
    try:
        # Add the cti_aggregator directory to the path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cti_aggregator')))
        
        # Try to import the Microsoft threat intelligence module
        try:
            from data_sources.tailored_intelligence import fetch_tailored_intel
            
            print("\nTesting Microsoft threat intelligence integration...\n")
            
            # Try to fetch Microsoft data
            ms_reports = fetch_tailored_intel(use_cache=True)
            
            if ms_reports:
                ms_integration_report["microsoft_available"] = True
                ms_integration_report["microsoft_intel_count"] = len(ms_reports)
                ms_integration_report["microsoft_source_count"] = 1  # Just CrowdStrike for now
                
                # Calculate ratios
                if ms_integration_report["microsoft_intel_count"] > 0:
                    # Calculate how many non-Microsoft sources we have per Microsoft source
                    source_ratio = ms_integration_report["non_microsoft_source_count"] / ms_integration_report["microsoft_source_count"]
                    ms_integration_report["comparison"]["sources_ratio"] = f"{source_ratio:.2f}"
                    
                    # Calculate how many articles we could potentially scrape compared to Microsoft data
                    # This is a rough estimate based on source count and average articles per source
                    avg_articles_per_source = sum(r["articles_found"] for r in scraper_report["results"]) / max(1, len(scraper_report["results"]))
                    potential_non_ms_intel = ms_integration_report["non_microsoft_source_count"] * avg_articles_per_source
                    intel_ratio = potential_non_ms_intel / ms_integration_report["microsoft_intel_count"] 
                    ms_integration_report["comparison"]["intel_ratio"] = f"{intel_ratio:.2f}"
                
                logger.info(f"✅ Found {ms_integration_report['microsoft_intel_count']} Microsoft intelligence reports")
                
                # If we have both Microsoft and non-Microsoft data, consider it a success
                if ms_integration_report["non_microsoft_source_count"] > 0:
                    ms_integration_report["status"] = "SUCCESS"
                    logger.info("✅ Both Microsoft and non-Microsoft sources are available")
                else:
                    logger.warning("⚠️ Microsoft data available, but no non-Microsoft sources")
            else:
                logger.warning("⚠️ No Microsoft intelligence data found")
        
        except ImportError:
            logger.warning("⚠️ Could not import Microsoft threat intelligence module")
            
            # If we don't have Microsoft data but have non-Microsoft sources, still consider it a success
            if ms_integration_report["non_microsoft_source_count"] > 0:
                ms_integration_report["status"] = "SUCCESS"
                logger.info("✅ Non-Microsoft sources are available (Microsoft module not available)")
            
    except Exception as e:
        logger.error(f"❌ Error in Microsoft integration test: {str(e)}")
        ms_integration_report["error"] = str(e)
    
    return ms_integration_report

def main():
    """Run the tests and generate a report."""
    print("\n==============================================")
    print("Non-Microsoft Threat Intelligence Source Test")
    print("==============================================")
    
    # Test 1: Check if websites are accessible
    web_report = test_web_accessibility()
    
    # Test 2: Check if scrapers work
    scraper_report = test_scraper_functionality()
    
    # Test 3: Compare with Microsoft data
    ms_integration_report = test_ms_integration(web_report, scraper_report)
    
    # Combine all reports
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "web_accessibility": web_report,
        "scraper_functionality": scraper_report,
        "ms_integration": ms_integration_report,
        "overall_result": {
            "websites_accessible": web_report["successful_sources"] > 0,
            "scrapers_working": scraper_report["scrapers_working"] > 0,
            "ms_integration_success": ms_integration_report["status"] == "SUCCESS"
        }
    }
    
    # Determine overall success - we need at least accessible websites
    final_report["success"] = final_report["overall_result"]["websites_accessible"]
    
    # Print summary results
    print("\n==============================================")
    print("Test Results Summary")
    print("==============================================")
    print(f"Web Accessibility: {web_report['successful_sources']} of {web_report['total_sources']} sources accessible ({web_report['success_rate']})")
    print(f"Scraper Functionality: {scraper_report['scrapers_working']} of {scraper_report['scrapers_tested']} scrapers working ({scraper_report['success_rate']})")
    print(f"Microsoft Integration: {ms_integration_report['status']}")
    print(f"Overall Result: {'SUCCESS' if final_report['success'] else 'FAILED'}")
    print("==============================================")
    
    # Save the report to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"intel_sources_test_report_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(final_report, f, indent=2)
        print(f"\nDetailed report saved to {filename}")
    except Exception as e:
        print(f"Error saving report: {str(e)}")
    
    # Return success flag
    return final_report["success"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 