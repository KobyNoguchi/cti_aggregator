from typing import List, Dict, Any, Optional

def scrape_intelligence_articles(
    url: str,
    source_name: str,
    article_selector: str,
    title_selector: str,
    url_selector: str,
    date_selector: str,
    date_format: Optional[str] = None,
    summary_selector: str = None,
    url_prefix: Optional[str] = None,
    threat_actor_type_selector: Optional[str] = None,
    target_industries_selector: Optional[str] = None,
    use_proxies: bool = True,
    use_headless_fallback: bool = True,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    Scrape intelligence articles from a given URL.
    
    Args:
        url: The URL to scrape
        source_name: Name of the intelligence source
        article_selector: CSS selector for article elements
        title_selector: CSS selector for title elements
        url_selector: CSS selector for URL elements
        date_selector: CSS selector for date elements
        date_format: Format string for parsing dates (None for auto-detection)
        summary_selector: CSS selector for summary elements
        url_prefix: Prefix to add to relative URLs
        threat_actor_type_selector: CSS selector for threat actor type
        target_industries_selector: CSS selector for target industries
        use_proxies: Whether to use proxies
        use_headless_fallback: Whether to fall back to headless browser
        max_retries: Maximum number of retries
        
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

    # Try to get the page content
    logger.info(f"Scraping intelligence articles from {source_name}")
    
    # ... rest of the function remains unchanged ... 