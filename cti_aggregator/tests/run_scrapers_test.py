#!/usr/bin/env python3
"""
Script to test intelligence scrapers from within the Django environment.
This helps ensure that the scrapers are properly configured and working.

Run this script from the Django shell:
python manage.py shell < ../tests/run_scrapers_test.py
"""

import os
import sys
import logging
from datetime import datetime
from django.utils import timezone
from django.db.models import Count

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import scraper tasks
try:
    from ioc_scraper.tasks import (
        fetch_all_intelligence,
        fetch_cisco_talos_intelligence,
        fetch_microsoft_intelligence,
        fetch_mandiant_intelligence,
        fetch_unit42_intelligence,
        fetch_zscaler_intelligence,
        fetch_dark_reading_intelligence,
        fetch_dark_reading_enhanced,
        fetch_google_tag_intelligence
    )
    from ioc_scraper.models import IntelligenceArticle
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def run_single_scraper(name, task_func):
    """Run a single scraper and report results"""
    logger.info(f"Testing {name} scraper...")
    
    # Count articles before
    before_count = IntelligenceArticle.objects.filter(source=name).count()
    logger.info(f"  Before: {before_count} articles from {name}")
    
    # Run the scraper
    start_time = datetime.now()
    try:
        result = task_func()
        logger.info(f"  Scraper result: {result}")
    except Exception as e:
        logger.error(f"  Scraper failed with error: {e}")
        return False
    
    # Count articles after
    after_count = IntelligenceArticle.objects.filter(source=name).count()
    logger.info(f"  After: {after_count} articles from {name}")
    
    # Calculate time taken
    time_taken = (datetime.now() - start_time).total_seconds()
    logger.info(f"  Completed in {time_taken:.2f} seconds")
    
    # Report success/failure
    if after_count > before_count:
        logger.info(f"  ✅ SUCCESS: Added {after_count - before_count} new articles")
        return True
    else:
        logger.info(f"  ⚠️ NO NEW ARTICLES: This could be normal if there is no new content")
        return True  # Still consider this a success
        
def test_all_scrapers():
    """Test all individual scrapers"""
    scrapers = [
        ("Cisco Talos", fetch_cisco_talos_intelligence),
        ("Microsoft", fetch_microsoft_intelligence),
        ("Mandiant", fetch_mandiant_intelligence),
        ("Palo Alto Unit 42", fetch_unit42_intelligence),
        ("Zscaler", fetch_zscaler_intelligence),
        ("Dark Reading", fetch_dark_reading_intelligence),
        ("Google TAG", fetch_google_tag_intelligence)
    ]
    
    successes = 0
    failures = 0
    
    for name, task_func in scrapers:
        if run_single_scraper(name, task_func):
            successes += 1
        else:
            failures += 1
    
    logger.info(f"Scraper tests completed: {successes} successful, {failures} failed")
    
    # Show summary of all sources in database
    sources = IntelligenceArticle.objects.values('source').annotate(count=Count('source'))
    logger.info("Intelligence sources in database:")
    for source in sources:
        logger.info(f"  - {source['source']}: {source['count']} articles")
    
    return successes, failures

if __name__ == "__main__":
    # This won't run directly in Django shell, but we include it for completeness
    logger.info("Running intelligence scraper tests...")
    test_all_scrapers()

# When run from Django shell, this will execute:
logger.info("Running intelligence scraper tests...")
successes, failures = test_all_scrapers()
print(f"\nSCRAPER TEST RESULTS: {successes} successful, {failures} failed\n") 