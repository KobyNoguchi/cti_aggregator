#!/usr/bin/env python
"""
Comprehensive test for the enhanced scraper
This tests all three scraping methods: direct requests, free proxies, and headless browser
"""

import sys
import os
import logging
import time
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_source(source_name, config, use_proxies=True, use_headless=True, test_only=True):
    """Test scraping a specific source with different methods"""
    from data_sources.free_enhanced_scraper import scrape_intelligence_articles
    
    logger.info(f"===== Testing {source_name} =====")
    start_time = time.time()
    
    # Test direct requests (no proxies)
    logger.info(f"Testing {source_name} with direct requests (no proxies)")
    direct_articles = scrape_intelligence_articles(
        url=config["url"],
        source_name=source_name,
        article_selector=config["article_selector"],
        title_selector=config["title_selector"],
        date_selector=config.get("date_selector"),
        date_format=config.get("date_format"),
        summary_selector=config.get("summary_selector"),
        url_selector=config.get("url_selector"),
        url_prefix=config.get("url_prefix", ""),
        use_proxies=False,
        use_headless_fallback=False,
        max_retries=2
    )
    
    if direct_articles:
        logger.info(f"Direct requests found {len(direct_articles)} articles")
        for i, article in enumerate(direct_articles[:2]):  # Show just 2 articles
            logger.info(f"{i+1}. {article['title']}")
            logger.info(f"   URL: {article['url']}")
    else:
        logger.warning("Direct requests failed to find any articles")
    
    # Test with proxies if requested
    proxy_articles = []
    if use_proxies:
        logger.info(f"Testing {source_name} with free proxies")
        proxy_articles = scrape_intelligence_articles(
            url=config["url"],
            source_name=source_name,
            article_selector=config["article_selector"],
            title_selector=config["title_selector"],
            date_selector=config.get("date_selector"),
            date_format=config.get("date_format"),
            summary_selector=config.get("summary_selector"),
            url_selector=config.get("url_selector"),
            url_prefix=config.get("url_prefix", ""),
            use_proxies=True,
            use_headless_fallback=False,
            max_retries=2
        )
        
        if proxy_articles:
            logger.info(f"Proxy requests found {len(proxy_articles)} articles")
            for i, article in enumerate(proxy_articles[:2]):  # Show just 2 articles
                logger.info(f"{i+1}. {article['title']}")
                logger.info(f"   URL: {article['url']}")
        else:
            logger.warning("Proxy requests failed to find any articles")
    
    # Test with headless browser if requested and available
    headless_articles = []
    if use_headless:
        try:
            from data_sources.headless_browser import is_headless_available, scrape_intelligence_articles_headless
            
            if is_headless_available():
                logger.info(f"Testing {source_name} with headless browser")
                headless_articles = scrape_intelligence_articles_headless(
                    url=config["url"],
                    source_name=source_name,
                    article_selector=config["article_selector"],
                    title_selector=config["title_selector"],
                    date_selector=config.get("date_selector"),
                    date_format=config.get("date_format"),
                    summary_selector=config.get("summary_selector"),
                    url_selector=config.get("url_selector"),
                    url_prefix=config.get("url_prefix", "")
                )
                
                if headless_articles:
                    logger.info(f"Headless browser found {len(headless_articles)} articles")
                    for i, article in enumerate(headless_articles[:2]):  # Show just 2 articles
                        logger.info(f"{i+1}. {article['title']}")
                        logger.info(f"   URL: {article['url']}")
                else:
                    logger.warning("Headless browser failed to find any articles")
            else:
                logger.warning("Headless browser not available")
        except ImportError:
            logger.warning("Headless browser module not available")
    
    # Test the full enhanced scraper with all methods
    logger.info(f"Testing {source_name} with full enhanced scraper (all methods)")
    full_articles = scrape_intelligence_articles(
        url=config["url"],
        source_name=source_name,
        article_selector=config["article_selector"],
        title_selector=config["title_selector"],
        date_selector=config.get("date_selector"),
        date_format=config.get("date_format"),
        summary_selector=config.get("summary_selector"),
        url_selector=config.get("url_selector"),
        url_prefix=config.get("url_prefix", ""),
        use_proxies=use_proxies,
        use_headless_fallback=use_headless,
        max_retries=2
    )
    
    if full_articles:
        logger.info(f"Enhanced scraper found {len(full_articles)} articles")
        for i, article in enumerate(full_articles[:3]):  # Show just 3 articles
            logger.info(f"{i+1}. {article['title']}")
            logger.info(f"   URL: {article['url']}")
            logger.info(f"   Date: {article['published_date']}")
            summary = article['summary'][:100] + "..." if len(article.get('summary', '')) > 100 else article.get('summary', '')
            logger.info(f"   Summary: {summary}")
    else:
        logger.warning("Enhanced scraper failed to find any articles")
    
    # If not in test-only mode, save to database
    if not test_only:
        try:
            # Need to set up Django environment
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
            import django
            django.setup()
            
            # Now import the model
            from ioc_scraper.models import IntelligenceArticle
            
            if full_articles:
                count = 0
                for article in full_articles:
                    try:
                        IntelligenceArticle.objects.update_or_create(
                            url=article['url'],
                            defaults={
                                'title': article['title'],
                                'source': article['source'],
                                'published_date': article['published_date'],
                                'summary': article['summary']
                            }
                        )
                        count += 1
                    except Exception as e:
                        logger.error(f"Error saving article: {str(e)}")
                
                logger.info(f"Saved {count} articles to database")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
    
    # Calculate elapsed time
    elapsed = time.time() - start_time
    logger.info(f"Total time for {source_name}: {elapsed:.2f} seconds")
    
    # Summary of results
    results = {
        'source': source_name,
        'direct_count': len(direct_articles),
        'proxy_count': len(proxy_articles),
        'headless_count': len(headless_articles),
        'enhanced_count': len(full_articles),
        'elapsed_time': elapsed
    }
    
    return results

def main():
    """Main test function for the full enhanced scraper"""
    parser = argparse.ArgumentParser(description='Test the enhanced scraper with different methods')
    parser.add_argument('--source', type=str, help='Specify a source to test (default: all)')
    parser.add_argument('--no-proxies', action='store_true', help='Disable proxy testing')
    parser.add_argument('--no-headless', action='store_true', help='Disable headless browser testing')
    parser.add_argument('--save', action='store_true', help='Save results to database')
    args = parser.parse_args()
    
    # Source configurations
    sources = {
        'Dark Reading': {
            'url': 'https://www.darkreading.com/threat-intelligence',
            'article_selector': '.article-info',
            'title_selector': 'h3 a',
            'date_selector': '.timestamp',
            'date_format': '%b %d, %Y',
            'summary_selector': '.deck',
            'url_prefix': 'https://www.darkreading.com'
        },
        'Krebs on Security': {
            'url': 'https://krebsonsecurity.com',
            'article_selector': 'article.post',
            'title_selector': 'h2 a',
            'date_selector': 'time.entry-date',
            'date_format': '%B %d, %Y',
            'summary_selector': '.entry-content p:first-of-type',
            'url_prefix': ''
        },
        'The Hacker News': {
            'url': 'https://thehackernews.com',
            'article_selector': '.body-post',
            'title_selector': 'h2.home-title',
            'url_selector': 'a',
            'date_selector': '.item-label',
            'date_format': '%b %d, %Y',
            'summary_selector': '.home-desc',
            'url_prefix': ''
        }
    }
    
    start_time = time.time()
    logger.info("Starting comprehensive enhanced scraper test")
    
    if args.source and args.source in sources:
        test_sources = {args.source: sources[args.source]}
    else:
        test_sources = sources
    
    results = []
    for source_name, config in test_sources.items():
        result = test_source(
            source_name, 
            config, 
            use_proxies=not args.no_proxies, 
            use_headless=not args.no_headless,
            test_only=not args.save
        )
        results.append(result)
        logger.info("-" * 50)
    
    # Print summary table
    logger.info("\n===== SUMMARY =====")
    logger.info(f"{'Source':<20} {'Direct':<10} {'Proxy':<10} {'Headless':<10} {'Enhanced':<10} {'Time (s)':<10}")
    logger.info("-" * 70)
    
    for result in results:
        logger.info(f"{result['source']:<20} {result['direct_count']:<10} {result['proxy_count']:<10} "
                   f"{result['headless_count']:<10} {result['enhanced_count']:<10} {result['elapsed_time']:<10.2f}")
    
    total_time = time.time() - start_time
    logger.info("-" * 70)
    logger.info(f"Total test time: {total_time:.2f} seconds")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Enhanced scraper test completed successfully!")
        else:
            print("\n❌ Enhanced scraper test failed. Check the logs for details.")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc()) 