#!/usr/bin/env python3
"""
Utility script to help update CSS selectors for threat intelligence sources.
This script analyzes the HTML structure of intelligence source websites and suggests
updated selectors when the current selectors are no longer working.
"""

import os
import sys
import json
import logging
import requests
import argparse
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Common user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
]

def get_random_user_agent():
    """Return a random user agent."""
    import random
    return random.choice(USER_AGENTS)

def get_page_content(url: str) -> Tuple[bool, Optional[str]]:
    """
    Fetch the HTML content of a webpage.
    
    Args:
        url: The URL to fetch
        
    Returns:
        Tuple of (success, content)
    """
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True, response.text
        else:
            logger.error(f"Failed to fetch content: Status code {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"Error fetching content: {str(e)}")
        return False, None

def escape_css_class(class_name: str) -> str:
    """
    Escape special characters in CSS class names.
    Particularly useful for Tailwind CSS classes that contain colons.
    
    Args:
        class_name: CSS class name to escape
        
    Returns:
        Escaped class name
    """
    # Escape colons in class names (common in Tailwind CSS)
    return class_name.replace(':', '\\:')

def analyze_html_structure(html_content: str) -> Dict[str, Any]:
    """
    Analyze the HTML structure to identify common patterns.
    
    Args:
        html_content: HTML content to analyze
        
    Returns:
        Dictionary with analysis results
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for common containers
    analysis = {
        "article_containers": [],
        "title_elements": [],
        "link_elements": [],
        "date_elements": [],
        "summary_elements": []
    }
    
    # Article containers
    container_candidates = [
        ("article", {}),
        ("div", {"class": re.compile(r"(post|article|entry|item|card|blog|content)")}),
        ("section", {"class": re.compile(r"(post|article|entry|item|card|blog|content)")})
    ]
    
    # Check each candidate
    for tag, attrs in container_candidates:
        elements = soup.find_all(tag, attrs)
        if elements:
            logger.info(f"Found {len(elements)} potential article containers: {tag}")
            element_info = {
                "tag": tag,
                "count": len(elements),
                "classes": []
            }
            
            # Get class names from the first few elements
            for element in elements[:3]:
                if element.get('class'):
                    element_info["classes"].extend(element.get('class'))
            
            # Deduplicate class names
            element_info["classes"] = list(set(element_info["classes"]))
            
            # Generate sample selector
            if element_info["classes"]:
                # Escape special characters in class names
                escaped_classes = [escape_css_class(c) for c in element_info["classes"][:2]]
                element_info["sample_selector"] = f"{tag}.{'.'.join(escaped_classes)}"
            else:
                element_info["sample_selector"] = tag
                
            analysis["article_containers"].append(element_info)
    
    # Find all divs with multiple children as potential containers
    divs = soup.find_all('div')
    potential_containers = []
    
    for div in divs:
        children = div.find_all(recursive=False)
        if len(children) >= 3:  # At least 3 children might be a list of articles
            potential_containers.append(div)
    
    # Add the top 5 potential containers by child count
    potential_containers.sort(key=lambda x: len(x.find_all(recursive=False)), reverse=True)
    
    for container in potential_containers[:5]:
        if container.get('class'):
            # Escape special characters in class names
            escaped_classes = [escape_css_class(c) for c in container.get('class')]
            selector = f"div.{'.'.join(escaped_classes)}"
            
            # Check if this selector is already in the list
            if not any(info["sample_selector"] == selector for info in analysis["article_containers"]):
                analysis["article_containers"].append({
                    "tag": "div",
                    "count": len(container.find_all(recursive=False)),
                    "classes": container.get('class'),
                    "sample_selector": selector
                })
    
    # Title elements (look inside the first container if available)
    title_candidates = ["h1", "h2", "h3", "h4", ".title", ".headline", ".post-title"]
    container = None
    
    # Use the first container if available
    if analysis["article_containers"]:
        try:
            container_selector = analysis["article_containers"][0]["sample_selector"]
            container_elements = soup.select(container_selector)
            if container_elements:
                container = container_elements[0]
            else:
                container = soup
        except Exception as e:
            logger.warning(f"Error selecting container: {str(e)}")
            container = soup
    else:
        container = soup
    
    # Check for title elements
    for candidate in title_candidates:
        try:
            elements = container.select(candidate)
            if elements:
                logger.info(f"Found {len(elements)} potential title elements: {candidate}")
                
                # Check if any of them contain links
                links_count = sum(1 for e in elements if e.find('a'))
                
                analysis["title_elements"].append({
                    "selector": candidate,
                    "count": len(elements),
                    "with_links": links_count,
                    "sample_text": elements[0].text.strip()[:50] if elements[0].text else ""
                })
        except Exception as e:
            logger.warning(f"Error selecting title elements with {candidate}: {str(e)}")
    
    # Link elements (often contain the article URL)
    if container:
        links = container.find_all('a')
        if links:
            # Group links by their parent's tag name
            by_parent = {}
            for link in links:
                if link.parent:
                    parent_tag = link.parent.name
                    if parent_tag not in by_parent:
                        by_parent[parent_tag] = []
                    by_parent[parent_tag].append(link)
            
            # Find patterns in links
            for parent_tag, parent_links in by_parent.items():
                if len(parent_links) > 1:  # Only consider patterns with multiple links
                    analysis["link_elements"].append({
                        "parent_tag": parent_tag,
                        "count": len(parent_links),
                        "sample_selector": f"{parent_tag} a",
                        "sample_text": parent_links[0].text.strip()[:50] if parent_links[0].text else ""
                    })
    
    # Date elements (look for time tags or date-related classes)
    date_candidates = [
        ("time", {}),
        ("span", {"class": re.compile(r"(date|time|posted|published)")}),
        ("div", {"class": re.compile(r"(date|time|posted|published)")})
    ]
    
    for tag, attrs in date_candidates:
        elements = soup.find_all(tag, attrs)
        if elements:
            logger.info(f"Found {len(elements)} potential date elements: {tag}")
            
            element_info = {
                "tag": tag,
                "count": len(elements),
                "classes": []
            }
            
            # Get class names
            for element in elements[:3]:
                if element.get('class'):
                    element_info["classes"].extend(element.get('class'))
            
            # Deduplicate class names
            element_info["classes"] = list(set(element_info["classes"]))
            
            # Generate sample selector
            if element_info["classes"]:
                # Escape special characters in class names
                escaped_classes = [escape_css_class(c) for c in element_info["classes"][:1]]
                element_info["sample_selector"] = f"{tag}.{'.'.join(escaped_classes)}"
            else:
                element_info["sample_selector"] = tag
                
            element_info["sample_text"] = elements[0].text.strip()[:50] if elements[0].text else ""
            analysis["date_elements"].append(element_info)
    
    # Summary elements (look for paragraphs or content classes)
    summary_candidates = [
        "p", 
        ".summary", 
        ".excerpt", 
        ".description", 
        ".content", 
        ".entry-content",
        ".post-content"
    ]
    
    if container:
        for candidate in summary_candidates:
            try:
                elements = container.select(candidate)
                if elements:
                    analysis["summary_elements"].append({
                        "selector": candidate,
                        "count": len(elements),
                        "sample_text": elements[0].text.strip()[:100] if elements[0].text else ""
                    })
            except Exception as e:
                logger.warning(f"Error selecting summary elements with {candidate}: {str(e)}")
    
    return analysis

def test_selector(html_content: str, selector: str) -> List[str]:
    """
    Test a CSS selector on HTML content and return the text of matching elements.
    
    Args:
        html_content: HTML content to analyze
        selector: CSS selector to test
        
    Returns:
        List of text content from matching elements
    """
    if not selector or not selector.strip():
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.select(selector)
        
        results = []
        for elem in elements[:5]:  # Limit to first 5 matches
            text = elem.text.strip()
            results.append(text[:100] + "..." if len(text) > 100 else text)
        
        return results
    except Exception as e:
        logger.warning(f"Error testing selector '{selector}': {str(e)}")
        return []

def suggest_selectors(analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    Suggest new selectors based on the HTML analysis.
    
    Args:
        analysis: HTML structure analysis
        
    Returns:
        Dictionary with suggested selectors
    """
    suggestions = {
        "article_selector": "",
        "title_selector": "",
        "url_selector": "",
        "date_selector": "",
        "summary_selector": ""
    }
    
    # Article selector
    if analysis["article_containers"]:
        # Choose the one with most occurrences
        best_container = max(analysis["article_containers"], key=lambda x: x["count"])
        suggestions["article_selector"] = best_container["sample_selector"]
    
    # Title selector
    if analysis["title_elements"]:
        # Prefer elements with links
        with_links = [e for e in analysis["title_elements"] if e["with_links"] > 0]
        if with_links:
            best_title = max(with_links, key=lambda x: x["with_links"])
            suggestions["title_selector"] = f"{suggestions['article_selector']} {best_title['selector']} a"
            suggestions["url_selector"] = suggestions["title_selector"]
        else:
            best_title = analysis["title_elements"][0]
            suggestions["title_selector"] = f"{suggestions['article_selector']} {best_title['selector']}"
    
    # URL selector - if not already set by title
    if not suggestions["url_selector"] and analysis["link_elements"]:
        best_link = max(analysis["link_elements"], key=lambda x: x["count"])
        suggestions["url_selector"] = f"{suggestions['article_selector']} {best_link['sample_selector']}"
    
    # Date selector
    if analysis["date_elements"]:
        best_date = analysis["date_elements"][0]
        suggestions["date_selector"] = f"{suggestions['article_selector']} {best_date['sample_selector']}"
    
    # Summary selector
    if analysis["summary_elements"]:
        best_summary = analysis["summary_elements"][0]
        suggestions["summary_selector"] = f"{suggestions['article_selector']} {best_summary['selector']}"
    
    return suggestions

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Update CSS selectors for threat intelligence sources')
    parser.add_argument('--url', '-u', type=str, required=True, help='URL of the threat intelligence source')
    parser.add_argument('--name', '-n', type=str, help='Name of the source (defaults to domain name)')
    parser.add_argument('--output', '-o', type=str, help='Output file for the results')
    parser.add_argument('--test', '-t', action='store_true', help='Test the suggested selectors')
    args = parser.parse_args()
    
    # Extract domain from URL if name not provided
    if not args.name:
        import re
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', args.url)
        if domain_match:
            args.name = domain_match.group(1)
        else:
            args.name = "Unknown Source"
    
    print(f"\nAnalyzing threat intelligence source: {args.name}")
    print(f"URL: {args.url}\n")
    
    # Get the page content
    success, content = get_page_content(args.url)
    
    if not success or not content:
        print("Failed to fetch page content. Exiting.")
        return 1
    
    print(f"Successfully fetched page content ({len(content)} bytes)")
    
    # Analyze the HTML structure
    print("\nAnalyzing HTML structure...")
    try:
        analysis = analyze_html_structure(content)
    except Exception as e:
        print(f"Error analyzing HTML structure: {str(e)}")
        return 1
    
    # Suggest new selectors
    print("\nSuggesting new selectors...")
    suggestions = suggest_selectors(analysis)
    
    # Display the suggestions
    print("\nSuggested selectors:")
    for selector_type, selector in suggestions.items():
        print(f"  {selector_type}: {selector}")
    
    # Test the selectors if requested
    if args.test and content:
        print("\nTesting selectors...")
        
        # Test article selector
        if suggestions["article_selector"]:
            try:
                articles = test_selector(content, suggestions["article_selector"])
                print(f"\nFound {len(articles)} articles with selector: {suggestions['article_selector']}")
                
                if articles:
                    # Create a subset of the HTML with just the first article for cleaner testing
                    article_soup = BeautifulSoup(content, 'html.parser')
                    first_article = article_soup.select(suggestions["article_selector"])[0]
                    article_html = str(first_article)
                    
                    # Test title selector
                    if suggestions["title_selector"]:
                        title_selector = suggestions["title_selector"].replace(f"{suggestions['article_selector']} ", "")
                        titles = test_selector(article_html, title_selector)
                        print(f"\nTitle selector: {suggestions['title_selector']}")
                        if titles:
                            print(f"Sample title: {titles[0]}")
                        else:
                            print("No titles found with this selector")
                    else:
                        print("\nNo title selector suggested")
                    
                    # Test URL selector
                    if suggestions["url_selector"]:
                        url_selector = suggestions["url_selector"].replace(f"{suggestions['article_selector']} ", "")
                        url_elements = BeautifulSoup(article_html, 'html.parser').select(url_selector)
                        print(f"\nURL selector: {suggestions['url_selector']}")
                        if url_elements and url_elements[0].get('href'):
                            print(f"Sample URL: {url_elements[0].get('href')}")
                        else:
                            print("No URLs found with this selector")
                    else:
                        print("\nNo URL selector suggested")
                    
                    # Test date selector
                    if suggestions["date_selector"]:
                        date_selector = suggestions["date_selector"].replace(f"{suggestions['article_selector']} ", "")
                        dates = test_selector(article_html, date_selector)
                        print(f"\nDate selector: {suggestions['date_selector']}")
                        if dates:
                            print(f"Sample date: {dates[0]}")
                        else:
                            print("No dates found with this selector")
                    else:
                        print("\nNo date selector suggested")
                    
                    # Test summary selector
                    if suggestions["summary_selector"]:
                        summary_selector = suggestions["summary_selector"].replace(f"{suggestions['article_selector']} ", "")
                        summaries = test_selector(article_html, summary_selector)
                        print(f"\nSummary selector: {suggestions['summary_selector']}")
                        if summaries:
                            print(f"Sample summary: {summaries[0]}")
                        else:
                            print("No summaries found with this selector")
                    else:
                        print("\nNo summary selector suggested")
            except Exception as e:
                print(f"Error testing selectors: {str(e)}")
        else:
            print("No article selector found, cannot test other selectors")
    
    # Save the results to a file if requested
    if args.output:
        result = {
            "timestamp": datetime.now().isoformat(),
            "source": {
                "name": args.name,
                "url": args.url
            },
            "analysis": analysis,
            "selectors": {
                "current": {},  # Would need to fetch from existing code
                "suggested": suggestions
            }
        }
        
        try:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to {args.output}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    
    # Print the Python code to update selectors
    print("\nPython code to update selectors:")
    print(f"""
# Update selectors for {args.name}
source_config = {{
    "name": "{args.name}",
    "url": "{args.url}",
    "article_selector": "{suggestions['article_selector']}",
    "title_selector": "{suggestions['title_selector']}",
    "url_selector": "{suggestions['url_selector']}",
    "date_selector": "{suggestions['date_selector']}",
    "summary_selector": "{suggestions['summary_selector']}",
    "url_prefix": None  # Update this if needed for relative URLs
}}
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 