#!/usr/bin/env python3
"""
Test script to verify if non-Microsoft threat intelligence sources are accessible.
This script directly checks various threat intelligence websites to confirm they are accessible
and can be used as sources for intelligence data.
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime
import random
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    """Return a random user agent."""
    return random.choice(USER_AGENTS)

def check_intelligence_source(source):
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

def test_non_microsoft_sources():
    """
    Test accessibility of non-Microsoft threat intelligence sources.
    
    Returns:
        Dictionary containing test results
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
    
    print(f"\nTesting {len(sources)} non-Microsoft threat intelligence sources...\n")
    
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

def main():
    """Run the test and save results to a file."""
    print("\n==============================================")
    print("Non-Microsoft Threat Intelligence Source Test")
    print("==============================================")
    
    # Run the test
    report = test_non_microsoft_sources()
    
    # Print summary results
    print("\n==============================================")
    print("Test Results Summary")
    print("==============================================")
    print(f"Total sources tested: {report['total_sources']}")
    print(f"Successful sources: {report['successful_sources']} ({report['success_rate']})")
    print(f"Failed sources: {report['failed_sources']}")
    print("==============================================")
    
    # Print details of each source
    print("\nDetailed Results:")
    for result in report["results"]:
        status_icon = "✅" if result["status"] == "SUCCESS" and result["keywords_found"] else "❌"
        print(f"{status_icon} {result['name']}: {result['status']} (Status code: {result['status_code']})")
        if result["keywords_found"]:
            print(f"   Keywords found: {', '.join(result['keywords_found'][:5])}...")
    
    # Save the report to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"non_microsoft_sources_test_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to {filename}")
    except Exception as e:
        print(f"Error saving report: {str(e)}")
    
    # Return success if at least 50% of sources were accessible
    success = report["successful_sources"] >= (report["total_sources"] / 2)
    
    print("\n==============================================")
    print(f"Test {'PASSED' if success else 'FAILED'}")
    print("==============================================")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 