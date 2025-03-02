#!/usr/bin/env python3
"""
Module for fetching and processing CrowdStrike Tailored Intelligence data.
This module uses the CrowdStrike Falcon API to fetch tailored intelligence
reports and updates the database with the results.
"""

import os
import sys
import json
import logging
import datetime
import redis
from uuid import uuid4
import django
import random
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Union

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
django.setup()

# Import models after Django setup
from ioc_scraper.models import CrowdStrikeTailoredIntel
from django.conf import settings

try:
    from falconpy import Intel
except ImportError:
    print("Could not import FalconPy. Install with: pip install falconpy")
    print("Proceeding with mock data mode.")
    Intel = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Redis connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_CACHE_DB', 0))
REDIS_KEY_PREFIX = 'crowdstrike:tailored_intel:'
REDIS_CACHE_EXPIRY = 86400  # 24 hours

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test connection
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {str(e)}")
    REDIS_AVAILABLE = False

# Add the backend directory to the path for importing Django models
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Try to import Django models and Redis cache
try:
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    import django
    django.setup()
    
    # Import models
    from ioc_scraper.models import CrowdStrikeTailoredIntel
    
    # Import Redis cache
    from ioc_scraper.redis_cache import (
        cache_tailored_intelligence,
        get_tailored_intelligence,
        clear_tailored_intelligence_cache
    )
    
    DJANGO_AVAILABLE = True
    logger.info("Django environment set up successfully")
except ImportError as e:
    DJANGO_AVAILABLE = False
    logger.warning(f"Django environment not available: {str(e)}")
except Exception as e:
    DJANGO_AVAILABLE = False
    logger.warning(f"Error setting up Django environment: {str(e)}")

# Sample data for testing
SAMPLE_THREAT_GROUPS = [
    "FANCY BEAR", "COZY BEAR", "LAZARUS GROUP", "APT29", "APT28", 
    "DARKSIDE", "REVIL", "CONTI", "LAPSUS$", "SANDWORM"
]

SAMPLE_SECTORS = [
    "Financial Services", "Healthcare", "Government", "Energy", "Technology",
    "Manufacturing", "Telecommunications", "Education", "Retail", "Defense"
]

def get_falcon_api():
    """
    Initialize the CrowdStrike Falcon API client.
    
    Returns:
        Intel: The FalconPy Intel API client or None if using mock data.
    """
    # Check if we have credentials
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret or not Intel:
        logger.info("Using mock data mode for CrowdStrike Tailored Intelligence")
        return None
    
    try:
        falcon = Intel(client_id=client_id, client_secret=client_secret)
        logger.info("Successfully initialized CrowdStrike Falcon API client")
        return falcon
    except Exception as e:
        logger.error(f"Failed to initialize CrowdStrike Falcon API client: {str(e)}")
        return None

def fetch_tailored_intel(falcon=None, limit=100, use_cache=True):
    """
    Fetch tailored intelligence reports from the CrowdStrike API
    or return mock data if no API client is provided.
    
    Args:
        falcon (Intel, optional): FalconPy Intel API client. Defaults to None.
        limit (int, optional): Maximum number of reports to fetch. Defaults to 100.
        use_cache (bool, optional): Whether to use Redis cache. Defaults to True.
    
    Returns:
        list: List of intelligence reports.
    """
    cache_key = f"{REDIS_KEY_PREFIX}reports"
    
    # Try to get data from cache if Redis is available and we want to use cache
    if REDIS_AVAILABLE and use_cache:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info("Retrieved tailored intelligence reports from Redis cache")
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                logger.warning("Could not decode cached data from Redis")
    
    # If no cached data or Redis is not available, fetch from API or generate mock data
    if falcon:
        try:
            # Query actual API
            response = falcon.query_intel_reports(
                parameters={
                    'limit': limit,
                    'sort': 'created_date|desc',
                    'type': 'report',
                    'filter': "report_type:'tailored_intelligence'"
                }
            )
            
            if response['status_code'] != 200:
                logger.error(f"Error querying intel reports: {response['body']}")
                return []
            
            # Get report IDs
            report_ids = response['body'].get('resources', [])
            if not report_ids:
                logger.warning("No tailored intelligence report IDs found")
                return []
            
            # Get report details
            response = falcon.get_intel_report_entities(
                ids=report_ids
            )
            
            if response['status_code'] != 200:
                logger.error(f"Error getting intel report details: {response['body']}")
                return []
            
            reports = response['body'].get('resources', [])
            logger.info(f"Retrieved {len(reports)} tailored intelligence reports")
            
            # Cache the data if Redis is available
            if REDIS_AVAILABLE:
                try:
                    redis_client.setex(cache_key, REDIS_CACHE_EXPIRY, json.dumps(reports))
                    logger.info(f"Cached {len(reports)} tailored intelligence reports in Redis")
                except Exception as e:
                    logger.warning(f"Failed to cache tailored intelligence reports: {str(e)}")
            
            return reports
        except Exception as e:
            logger.error(f"Exception while fetching tailored intelligence: {str(e)}")
            return []
    else:
        # Generate mock data
        reports = generate_mock_data(limit)
        
        # Cache the mock data if Redis is available
        if REDIS_AVAILABLE:
            try:
                redis_client.setex(cache_key, REDIS_CACHE_EXPIRY, json.dumps(reports))
                logger.info(f"Cached {len(reports)} mock tailored intelligence reports in Redis")
            except Exception as e:
                logger.warning(f"Failed to cache mock tailored intelligence reports: {str(e)}")
        
        return reports

def generate_mock_data(count=20):
    """
    Generate mock data for testing when no API client is available.
    
    Args:
        count (int, optional): Number of mock reports to generate. Defaults to 20.
    
    Returns:
        list: List of mock intelligence reports.
    """
    # Define some sample data
    threat_groups = [
        "WICKED PANDA", "PRIMITIVE BEAR", "JUDGMENT PANDA", "VELVET CHOLLIMA",
        "WIZARD SPIDER", "MUMMY SPIDER", "VAGRANT SPIDER", "DAGGER ARES",
        "SCATTERED SPIDER", "GRACEFUL MAMMOTH", "OUTLAW SPIDER", "VOODOO BEAR"
    ]
    
    nations = [
        "China", "Russia", "North Korea", "Iran", "Unknown"
    ]
    
    sectors = [
        "Technology", "Finance", "Healthcare", "Government", "Defense", 
        "Energy", "Telecommunications", "Manufacturing", "Retail"
    ]
    
    countries = [
        "United States", "United Kingdom", "Germany", "France", "Japan", 
        "Australia", "Canada", "South Korea", "Ukraine", "Taiwan", 
        "India", "Brazil", "Israel"
    ]
    
    report_titles = [
        "Analysis of {threat_group} Targeting {sector} Sector",
        "New Campaign by {threat_group} Against {country} Organizations",
        "{threat_group} Deploys Novel Malware Against {sector} Entities",
        "State-Sponsored {nation} Group {threat_group} Increases Activity",
        "Supply Chain Compromise Campaign by {threat_group}",
        "{threat_group} Targets Critical Infrastructure in {country}",
        "Evolving TTPs of {nation}-based Threat Actor {threat_group}",
        "{threat_group} Exploits Zero-Day Vulnerability in {sector} Systems"
    ]
    
    mock_reports = []
    
    # Generate random reports
    for i in range(count):
        # Select random elements
        threat_group = random.choice(threat_groups)
        nation = random.choice(nations)
        sector = random.choice(sectors)
        country = random.choice(countries)
        
        # Create report title
        title_template = random.choice(report_titles)
        title = title_template.format(
            threat_group=threat_group,
            nation=nation,
            sector=sector,
            country=country
        )
        
        # Random date within the last year
        days_ago = random.randint(0, 365)
        pub_date = datetime.now() - timedelta(days=days_ago)
        updated_date = pub_date + timedelta(days=random.randint(0, min(30, days_ago)))
        
        # Random sectors and countries targeted (1-3)
        targeted_sectors = random.sample(sectors, random.randint(1, min(3, len(sectors))))
        targeted_countries = random.sample(countries, random.randint(1, min(3, len(countries))))
        
        # Generate a mock report
        report = {
            'id': str(uuid4()),
            'name': title,
            'publish_date': pub_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'last_update': updated_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'summary': f"This report details activities attributed to {threat_group}, a threat group with suspected ties to {nation}. The group has been observed targeting {', '.join(targeted_sectors)} sectors in {', '.join(targeted_countries)}. Activities include spear-phishing campaigns, exploitation of VPN vulnerabilities, and deployment of custom malware for data exfiltration. Organizations in these sectors should apply patches promptly and implement enhanced monitoring for indicators of compromise described in this report.",
            'threat_groups': [threat_group],
            'nation_affiliations': [nation] if nation != "Unknown" else [],
            'targeted_sectors': targeted_sectors,
            'targeted_countries': targeted_countries,
            'url': f"https://example.com/intelligence/reports/{i+1}",
        }
        
        mock_reports.append(report)
    
    logger.info(f"Generated {len(mock_reports)} mock tailored intelligence reports")
    return mock_reports

def process_reports(reports):
    """
    Process and normalize intelligence reports for storage.
    
    Args:
        reports (list): List of intelligence reports from the API or mock data.
    
    Returns:
        list: List of normalized report dictionaries.
    """
    processed_reports = []
    
    for report in reports:
        # Extract data based on whether it's real API data or mock data
        if 'id' in report and 'name' in report:  # Mock data format
            processed = {
                'id': report['id'],
                'name': report['name'],
                'publish_date': report.get('publish_date'),
                'last_updated': report.get('last_update'),
                'summary': report.get('summary', ''),
                'url': report.get('url', ''),
                'threat_groups': report.get('threat_groups', []),
                'nation_affiliations': report.get('nation_affiliations', []),
                'targeted_sectors': report.get('targeted_sectors', []),
                'targeted_countries': report.get('targeted_countries', []),
                'raw_data': report
            }
        else:  # Real API data format (adjust as needed based on actual API response)
            processed = {
                'id': report.get('id', str(uuid4())),
                'name': report.get('title', report.get('name', 'Untitled Report')),
                'publish_date': report.get('created_date'),
                'last_updated': report.get('last_modified_date'),
                'summary': report.get('description', report.get('summary', '')),
                'url': report.get('url', ''),
                'threat_groups': [],  # Extract from real data
                'nation_affiliations': [],  # Extract from real data
                'targeted_sectors': [],  # Extract from real data
                'targeted_countries': [],  # Extract from real data
                'raw_data': report
            }
            
            # Extract structured data from tags, actors, targets, etc.
            # This would need to be adjusted based on the actual structure of the API response
            
            # Example: Extract threat groups from actors
            if 'actors' in report:
                processed['threat_groups'] = [actor.get('name') for actor in report.get('actors', [])]
            
            # Example: Extract targeted sectors and countries
            if 'targets' in report:
                sectors = []
                countries = []
                for target in report.get('targets', []):
                    if target.get('type') == 'industry':
                        sectors.append(target.get('value'))
                    elif target.get('type') == 'country':
                        countries.append(target.get('value'))
                
                processed['targeted_sectors'] = sectors
                processed['targeted_countries'] = countries
            
            # Example: Extract nation affiliations
            if 'origins' in report:
                processed['nation_affiliations'] = [origin.get('value') for origin in report.get('origins', []) if origin.get('type') == 'country']
        
        processed_reports.append(processed)
    
    return processed_reports

def update_database(reports):
    """
    Update the database with the processed intelligence reports.
    
    Args:
        reports (list): List of normalized report dictionaries.
    
    Returns:
        tuple: (created_count, updated_count, total_count)
    """
    created_count = 0
    updated_count = 0
    
    for report in reports:
        try:
            # Try to get existing report
            obj, created = CrowdStrikeTailoredIntel.objects.update_or_create(
                id=report['id'],
                defaults={
                    'name': report['name'],
                    'publish_date': report['publish_date'],
                    'last_updated': report['last_updated'],
                    'summary': report['summary'],
                    'url': report['url'],
                    'threat_groups': report['threat_groups'],
                    'nation_affiliations': report['nation_affiliations'],
                    'targeted_sectors': report['targeted_sectors'],
                    'targeted_countries': report['targeted_countries'],
                    'raw_data': report['raw_data']
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as e:
            logger.error(f"Error updating database for report {report['id']}: {str(e)}")
    
    return created_count, updated_count, len(reports)

def generate_sample_data(count: int = 10) -> List[Dict]:
    """Generate sample tailored intelligence data for testing."""
    reports = []
    
    for i in range(count):
        # Generate a random date within the last 30 days
        days_ago = random.randint(0, 30)
        publish_date = datetime.now() - timedelta(days=days_ago)
        
        # Select random threat groups (1-3)
        num_groups = random.randint(1, 3)
        threat_groups = random.sample(SAMPLE_THREAT_GROUPS, num_groups)
        
        # Select random targeted sectors (1-4)
        num_sectors = random.randint(1, 4)
        targeted_sectors = random.sample(SAMPLE_SECTORS, num_sectors)
        
        report = {
            "id": f"CS-TI-{100000 + i}",
            "name": f"Tailored Intelligence Report {i+1}",
            "publish_date": publish_date.strftime("%Y-%m-%d"),
            "summary": f"This is a sample tailored intelligence report {i+1} describing recent threat activity.",
            "threat_groups": threat_groups,
            "targeted_sectors": targeted_sectors,
            "random_value": random.random()  # Add a random value to ensure data changes between runs
        }
        
        reports.append(report)
    
    # Sort by publish date (newest first)
    reports.sort(key=lambda x: x["publish_date"], reverse=True)
    return reports

def save_to_database(reports: List[Dict]) -> Tuple[int, int]:
    """Save reports to the database."""
    if not DJANGO_AVAILABLE:
        logger.warning("Django not available, skipping database save")
        return 0, 0
    
    created_count = 0
    updated_count = 0
    
    try:
        for report in reports:
            # Check if report already exists
            obj, created = CrowdStrikeTailoredIntel.objects.update_or_create(
                report_id=report["id"],
                defaults={
                    "title": report["name"],
                    "publish_date": report["publish_date"],
                    "summary": report["summary"],
                    "threat_groups": ",".join(report["threat_groups"]),
                    "targeted_sectors": ",".join(report["targeted_sectors"]),
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Database save complete: {created_count} created, {updated_count} updated")
        return created_count, updated_count
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return 0, 0

def load_from_database() -> List[Dict]:
    """Load reports from the database."""
    if not DJANGO_AVAILABLE:
        logger.warning("Django not available, skipping database load")
        return []
    
    try:
        reports = []
        db_reports = CrowdStrikeTailoredIntel.objects.all().order_by('-publish_date')
        
        for report in db_reports:
            reports.append({
                "id": report.report_id,
                "name": report.title,
                "publish_date": report.publish_date.strftime("%Y-%m-%d") if hasattr(report.publish_date, 'strftime') else report.publish_date,
                "summary": report.summary,
                "threat_groups": report.threat_groups.split(",") if report.threat_groups else [],
                "targeted_sectors": report.targeted_sectors.split(",") if report.targeted_sectors else [],
            })
        
        logger.info(f"Loaded {len(reports)} reports from database")
        return reports
    except Exception as e:
        logger.error(f"Error loading from database: {str(e)}")
        return []

def run_update(use_cache: bool = True, force_refresh: bool = False) -> List[Dict]:
    """
    Run the tailored intelligence update process.
    
    Args:
        use_cache: Whether to use Redis caching
        force_refresh: Whether to force a refresh of the data
        
    Returns:
        List of tailored intelligence reports
    """
    logger.info("Starting tailored intelligence update")
    
    # Check if data is in cache and use_cache is True
    if use_cache and not force_refresh:
        cached_data = get_tailored_intelligence()
        if cached_data:
            logger.info(f"Using cached data with {len(cached_data)} reports")
            return cached_data
    
    # If we're here, we need to get fresh data
    logger.info("Getting fresh tailored intelligence data")
    
    # First try to load from database
    reports = load_from_database()
    
    # If no data in database or force refresh, generate sample data
    if not reports or force_refresh:
        logger.info("Generating sample data")
        reports = generate_sample_data(15)  # Generate 15 sample reports
        
        # Save to database if available
        if DJANGO_AVAILABLE:
            created, updated = save_to_database(reports)
            logger.info(f"Saved to database: {created} created, {updated} updated")
    
    # Cache the data if caching is enabled
    if use_cache:
        if force_refresh:
            # Clear existing cache first if forcing refresh
            clear_tailored_intelligence_cache()
        
        # Cache the new data
        cache_success = cache_tailored_intelligence(reports)
        if cache_success:
            logger.info(f"Successfully cached {len(reports)} reports")
        else:
            logger.warning("Failed to cache reports")
    
    logger.info(f"Tailored intelligence update complete with {len(reports)} reports")
    return reports

def run_tests() -> bool:
    """Run tests for the tailored intelligence module."""
    logger.info("Running tailored intelligence tests")
    
    try:
        # Test 1: Generate sample data
        logger.info("Test 1: Generate sample data")
        sample_data = generate_sample_data(5)
        if not sample_data or len(sample_data) != 5:
            logger.error("Test 1 failed: Could not generate sample data")
            return False
        logger.info("Test 1 passed: Sample data generated successfully")
        
        # Test 2: Database operations (if available)
        if DJANGO_AVAILABLE:
            logger.info("Test 2: Database operations")
            created, updated = save_to_database(sample_data)
            if created + updated != 5:
                logger.error(f"Test 2 failed: Database save returned {created} created, {updated} updated")
                return False
            
            db_data = load_from_database()
            if not db_data:
                logger.error("Test 2 failed: Could not load data from database")
                return False
            logger.info("Test 2 passed: Database operations successful")
        else:
            logger.warning("Test 2 skipped: Django not available")
        
        # Test 3: Redis caching (if available)
        try:
            from ioc_scraper.redis_cache import redis_cache
            
            logger.info("Test 3: Redis caching")
            # Clear cache first
            clear_tailored_intelligence_cache()
            
            # Cache test data
            cache_success = cache_tailored_intelligence(sample_data)
            if not cache_success:
                logger.error("Test 3 failed: Could not cache data")
                return False
            
            # Retrieve cached data
            cached_data = get_tailored_intelligence()
            if not cached_data or len(cached_data) != 5:
                logger.error(f"Test 3 failed: Retrieved {len(cached_data) if cached_data else 0} items from cache, expected 5")
                return False
            
            logger.info("Test 3 passed: Redis caching successful")
        except ImportError:
            logger.warning("Test 3 skipped: Redis cache not available")
        
        # Test 4: Full update process
        logger.info("Test 4: Full update process")
        reports = run_update(force_refresh=True)
        if not reports:
            logger.error("Test 4 failed: run_update returned no data")
            return False
        logger.info(f"Test 4 passed: run_update returned {len(reports)} reports")
        
        logger.info("All tests passed successfully")
        return True
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tailored Intelligence Update Tool")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--force-refresh", action="store_true", help="Force refresh of data")
    parser.add_argument("--no-cache", action="store_true", help="Disable Redis caching")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        reports = run_update(use_cache=not args.no_cache, force_refresh=args.force_refresh)
        print(f"Updated {len(reports)} tailored intelligence reports") 