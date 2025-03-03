import sys
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from ioc_scraper.models import IntelligenceArticle
from datetime import datetime

# Add the parent directories to the path to allow imports from data_sources
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

class Command(BaseCommand):
    help = 'Fetch intelligence articles using the free proxy scraper'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='Specific source to fetch (default: all)')
        parser.add_argument('--use-proxies', type=bool, default=True, help='Whether to use proxies for scraping')
        parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries for failed requests')
        parser.add_argument('--test-only', action='store_true', help='Run in test mode without saving to database')

    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        source = options.get('source')
        use_proxies = options.get('use_proxies')
        max_retries = options.get('max_retries')
        test_only = options.get('test_only')
        
        self.stdout.write(self.style.SUCCESS(f'Starting intelligence fetch with free proxies'))
        self.stdout.write(f'Source: {source if source else "All"}')
        self.stdout.write(f'Use proxies: {use_proxies}')
        self.stdout.write(f'Max retries: {max_retries}')
        self.stdout.write(f'Test mode: {test_only}')
        
        try:
            # Import our free enhanced scraper
            from data_sources.free_enhanced_scraper import scrape_intelligence_articles, is_free_proxy_configured
            
            # Check if free proxy system is configured
            if use_proxies:
                proxy_status = is_free_proxy_configured()
                self.stdout.write(f'Free proxy system configured: {proxy_status}')
            
            # Define our sources and their scraping configurations
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
                    'date_selector': '.item-label',
                    'date_format': '%B %d, %Y',
                    'summary_selector': '.home-desc',
                    'url_prefix': ''
                }
            }
            
            # Filter sources if a specific one was requested
            if source and source in sources:
                source_configs = {source: sources[source]}
            else:
                source_configs = sources
            
            # Track total articles
            total_articles = 0
            
            # Process each source
            for source_name, config in source_configs.items():
                self.stdout.write(f'\nFetching articles from {source_name}...')
                
                try:
                    # Scrape articles using our enhanced scraper
                    articles = scrape_intelligence_articles(
                        url=config['url'],
                        source_name=source_name,
                        article_selector=config['article_selector'],
                        title_selector=config['title_selector'],
                        date_selector=config['date_selector'],
                        date_format=config['date_format'],
                        summary_selector=config['summary_selector'],
                        url_prefix=config['url_prefix'],
                        use_proxies=use_proxies,
                        max_retries=max_retries
                    )
                    
                    if articles:
                        self.stdout.write(self.style.SUCCESS(f'Found {len(articles)} articles from {source_name}'))
                        
                        # If not in test-only mode, save to database
                        if not test_only:
                            count = 0
                            for article in articles:
                                try:
                                    # Create or update the article in the database
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
                                    self.stderr.write(f"Error saving article {article.get('title', 'Unknown')}: {str(e)}")
                            
                            self.stdout.write(self.style.SUCCESS(f'Saved {count} articles from {source_name} to database'))
                            total_articles += count
                        else:
                            # In test mode, just print the first few articles
                            self.stdout.write('Test mode - not saving to database')
                            for i, article in enumerate(articles[:3]):
                                self.stdout.write(f"{i+1}. {article['title']}")
                                self.stdout.write(f"   URL: {article['url']}")
                                self.stdout.write(f"   Date: {article['published_date']}")
                                
                            total_articles += len(articles)
                    else:
                        self.stderr.write(f'No articles found from {source_name}')
                        
                        # If proxy scraping failed, try direct connection
                        if use_proxies:
                            self.stdout.write('Trying direct connection without proxies...')
                            articles = scrape_intelligence_articles(
                                url=config['url'],
                                source_name=source_name,
                                article_selector=config['article_selector'],
                                title_selector=config['title_selector'],
                                date_selector=config['date_selector'],
                                date_format=config['date_format'],
                                summary_selector=config['summary_selector'],
                                url_prefix=config['url_prefix'],
                                use_proxies=False,
                                max_retries=max_retries
                            )
                            
                            if articles:
                                self.stdout.write(self.style.SUCCESS(
                                    f'Found {len(articles)} articles from {source_name} using direct connection'
                                ))
                                
                                # If not in test-only mode, save to database
                                if not test_only:
                                    count = 0
                                    for article in articles:
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
                                            self.stderr.write(f"Error saving article {article.get('title', 'Unknown')}: {str(e)}")
                                    
                                    self.stdout.write(self.style.SUCCESS(
                                        f'Saved {count} articles from {source_name} to database using direct connection'
                                    ))
                                    total_articles += count
                                else:
                                    # In test mode, just print the first few articles
                                    self.stdout.write('Test mode - not saving to database')
                                    for i, article in enumerate(articles[:3]):
                                        self.stdout.write(f"{i+1}. {article['title']}")
                                        self.stdout.write(f"   URL: {article['url']}")
                                        self.stdout.write(f"   Date: {article['published_date']}")
                                        
                                    total_articles += len(articles)
                            else:
                                self.stderr.write(f'No articles found from {source_name} even with direct connection')
                
                except Exception as e:
                    self.stderr.write(f'Error processing {source_name}: {str(e)}')
            
            # Summary
            self.stdout.write('\n' + self.style.SUCCESS('-' * 50))
            if test_only:
                self.stdout.write(self.style.SUCCESS(f'Test completed - found {total_articles} articles from all sources'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Saved {total_articles} articles from all sources to database'))
            
        except ImportError as e:
            self.stderr.write(f'Import error: {str(e)}')
            self.stderr.write('Make sure you have installed all the required dependencies from requirements.txt')
        except Exception as e:
            self.stderr.write(f'Unexpected error: {str(e)}')
            import traceback
            self.stderr.write(traceback.format_exc()) 