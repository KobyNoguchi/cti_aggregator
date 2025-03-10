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
from typing import Dict, List, Optional, Tuple, Union, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"Loaded environment variables from {dotenv_path}")
    else:
        print(f"No .env file found at {dotenv_path}")
except ImportError:
    print("python-dotenv not installed. Environment variables must be set manually.")

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

# Set up Redis connection if available
try:
    import redis
    REDIS_AVAILABLE = True
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = int(os.environ.get('REDIS_PORT', 6379))
    redis_db = int(os.environ.get('REDIS_DB', 0))
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    logger.info(f"Redis connection established to {redis_host}:{redis_port} db={redis_db}")
except (ImportError, redis.exceptions.ConnectionError) as e:
    REDIS_AVAILABLE = False
    redis_client = None
    logger.warning(f"Redis not available: {str(e)}")

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
    """Get a FalconAPI instance with credentials from env variables."""
    import os
    
    # Check for environment variables
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.error("CrowdStrike API credentials not found in environment variables")
        logger.error("Please set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET in your .env file")
        
        # Debug information
        logger.info("Available environment variables: " + ", ".join(list(os.environ.keys())))
        logger.info("Current working directory: " + os.getcwd())
        
        return None
    
    try:
        # Use FalconPy SDK for API access
        from falconpy import APIHarness
        falcon = APIHarness(client_id=client_id, client_secret=client_secret)
        logger.info("Successfully initialized Falcon API connection")
        return falcon
    except ImportError:
        logger.error("FalconPy library not installed. Please install it with: pip install crowdstrike-falconpy")
        return None
    except Exception as e:
        logger.error(f"Error initializing Falcon API: {str(e)}")
        return None

def fetch_tailored_intel(falcon=None, limit=100, use_cache=True):
    """
    Fetch tailored intelligence reports from CrowdStrike API.
    
    Args:
        falcon: FalconAPI instance
        limit: Maximum number of reports to fetch
        use_cache: Whether to use Redis caching
        
    Returns:
        List of reports
    """
    if use_cache:
        cache_key = f"tailored_intel_{limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            logger.info(f"Using cached tailored intelligence data ({len(cached_data)} reports)")
            return cached_data
    
    if not falcon:
        falcon = get_falcon_api()
        if not falcon:
            logger.error("Failed to initialize Falcon API, cannot fetch tailored intelligence")
            return []
    
    try:
        # Log available operations for debugging
        logger.info(f"Available operations: {len(falcon.commands)}")
        intel_ops = [op for op in falcon.commands if isinstance(op, str) and 'intel' in op.lower()]
        logger.info(f"Intelligence operations: {', '.join(intel_ops[:10])}...")
        
        # Fetch reports - let's try a different filter to see if we get results
        logger.info("Fetching intelligence reports...")
        params = {
            "limit": limit
        }
        
        # Try to get any kind of intel reports
        response = falcon.command("QueryIntelIndicatorEntities", parameters=params)
        
        if response["status_code"] != 200:
            logger.error(f"API request failed with status {response['status_code']}: {response.get('body', {}).get('errors', [])}")
            
            # Let's try another endpoint as a fallback
            logger.info("Trying alternate endpoint...")
            response = falcon.command("GetIntelReports", parameters=params)
            
            if response["status_code"] != 200:
                logger.error(f"Alternate API request failed with status {response['status_code']}: {response.get('body', {}).get('errors', [])}")
                return []
        
        # Log response body structure to understand what we're getting
        for key in response.get("body", {}).keys():
            logger.info(f"Response body contains key: {key}")
        
        # Try to find resources - could be under different keys depending on the endpoint
        report_ids = response["body"].get("resources", [])
        if not report_ids:
            # Try alternate keys
            report_ids = response["body"].get("reports", [])
            
        if not report_ids:
            logger.warning("No intelligence report IDs or data returned from API")
            return []
        
        logger.info(f"Found {len(report_ids)} intelligence reports")
        
        # Initialize reports variable
        reports = []
        
        # If we directly got full reports instead of just IDs, process them
        if isinstance(report_ids[0], dict) and "name" in report_ids[0]:
            logger.info("Received full report data, processing directly")
            reports = report_ids
        else:
            # We got IDs, need to fetch details
            logger.info("Received report IDs, fetching details...")
            # Process reports in batches to avoid exceeding API limits
            batch_size = 20
            
            for i in range(0, len(report_ids), batch_size):
                batch_ids = report_ids[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} with {len(batch_ids)} reports...")
                
                # Get details for each report
                batch_params = {
                    "ids": batch_ids
                }
                
                batch_response = falcon.command("GetIntelReportEntities", parameters=batch_params)
                
                if batch_response["status_code"] != 200:
                    logger.error(f"Failed to fetch report details for batch {i//batch_size + 1}: {batch_response.get('body', {}).get('errors', [])}")
                    continue
                
                batch_reports = batch_response["body"].get("resources", [])
                if not batch_reports:
                    logger.warning(f"No report data returned for batch {i//batch_size + 1}")
                    continue
                    
                logger.info(f"Successfully fetched {len(batch_reports)} reports in batch {i//batch_size + 1}")
                reports.extend(batch_reports)
        
        # If we still don't have any reports, return an empty list
        if not reports:
            logger.warning("No report data could be retrieved from the API")
            return []
        
        # Process the fetched reports
        processed_reports = []
        for report in reports:
            # Extract and transform relevant fields
            processed_report = {
                "id": report.get("id", ""),
                "name": report.get("name", ""),
                "publish_date": report.get("created_date", ""),
                "last_updated": report.get("last_modified_date", ""),
                "summary": report.get("short_description", ""),
                "url": report.get("url", ""),  # This should be the actual report URL from CrowdStrike
                "threat_groups": [actor.get("name", "") for actor in report.get("actors", [])],
                "targeted_sectors": [industry.get("value", "") for industry in report.get("target_industries", [])],
                "nation_affiliations": [],
                "targeted_countries": [country.get("value", "") for country in report.get("target_countries", [])],
                "raw_data": report
            }
            processed_reports.append(processed_report)
        
        if use_cache and processed_reports:
            set_cached_data(cache_key, processed_reports, 3600)  # Cache for 1 hour
        
        logger.info(f"Successfully processed {len(processed_reports)} intelligence reports")
        return processed_reports
        
    except Exception as e:
        logger.error(f"Error fetching tailored intelligence: {str(e)}")
        logger.exception(e)  # Print full exception traceback for debugging
        return []

def generate_top_news_reports(count=10):
    """
    Generate sample intelligence reports using real-world URLs from top cybersecurity news sources.
    This is used to demonstrate how real report URLs would work in the application.
    """
    logger.info("Generating sample intelligence reports with real URLs")
    
    # List of real cybersecurity news sources with realistic URLs
    reports = [
        {
            "id": "cs-report-1",
            "name": "CSA-250243: LightBasin Likely Deploys TinyShell Variant Targeting South American Financial Entity",
            "publish_date": "2025-03-02T12:30:00Z",
            "last_updated": "2025-03-04T15:45:00Z",
            "summary": "Topic: TinyShell || Adversary: LightBasin || Target Industry: Financial Services || Target Geography: South America, Americas\n\nIn January 2025, CrowdStrike Falcon OverWatch detected a TinyShell variant deployment at a South American financial entity.",
            "url": "https://falcon.crowdstrike.com/intelligence/reports/csa-250243",
            "threat_groups": ["LightBasin"],
            "targeted_sectors": ["Financial Services"],
            "nation_affiliations": [],
            "targeted_countries": ["South America"],
            "raw_data": {}
        },
        {
            "id": "cs-report-2",
            "name": "CSA-250242: Russian IO Campaign Storm-1516 Continues to Target Germany's 2025 Snap Elections",
            "publish_date": "2025-03-01T10:15:00Z",
            "last_updated": "2025-03-03T09:30:00Z",
            "summary": "Topic: IO || Adversary: Russia || Target Industry: Germany || Target Geography: Europe\n\nThroughout February 2025, an ongoing Russia-nexus information operations (IO) campaign, Storm-1516, has targeted electoral parties and candidates ahead of Germany's snap federal elections.",
            "url": "https://falcon.crowdstrike.com/intelligence/reports/csa-250242",
            "threat_groups": ["Storm-1516"],
            "targeted_sectors": ["Government", "Media"],
            "nation_affiliations": ["Russia"],
            "targeted_countries": ["Germany", "Europe"],
            "raw_data": {}
        },
        {
            "id": "cs-report-3",
            "name": "CSA-250241: Sitecore Deserialization Vulnerabilities CVE-2019-9874 and CVE-2019-9875 Highly Likely Exploited by RADIANT SPIDER",
            "publish_date": "2025-02-28T16:45:00Z",
            "last_updated": "2025-03-02T14:20:00Z",
            "summary": "Topic: CVE-2019-9874 and CVE-2019-9875 || Adversary: RADIANT SPIDER || Target Industry: Multiple || Target Geography: Multiple\n\nBeginning on 19 February 2025, CrowdStrike Falcon OverWatch and Falcon Complete responded to multiple incidents against U.S.-based education, healthcare, manufacturing, services, state government, and telecom entities.",
            "url": "https://falcon.crowdstrike.com/intelligence/reports/csa-250241",
            "threat_groups": ["RADIANT SPIDER"],
            "targeted_sectors": ["Education", "Healthcare", "Manufacturing", "Government", "Telecom"],
            "nation_affiliations": [],
            "targeted_countries": ["United States"],
            "raw_data": {}
        },
        {
            "id": "cs-report-4",
            "name": "CSA-250240: Threat Actor j332332 Maintain Telegram Channel Dedicated to the Recruitment of Workers at Compounds Likely Linked to Pig-Butchering",
            "publish_date": "2025-02-27T09:10:00Z",
            "last_updated": "2025-03-01T11:30:00Z",
            "summary": "Topic: Fraud Techniques\n\nOn 19 February 2025, threat actor j332332 posted three job advertisements recruiting Southeast Asia-based 'live models' and call center operators on the Telegram channel 'Cambodian working model' (hereafter referred to as CWM).",
            "url": "https://falcon.crowdstrike.com/intelligence/reports/csa-250240",
            "threat_groups": ["j332332"],
            "targeted_sectors": ["Financial Services", "Individuals"],
            "nation_affiliations": [],
            "targeted_countries": ["Southeast Asia"],
            "raw_data": {}
        },
        {
            "id": "cs-report-5",
            "name": "CSA-250239: DonBenitoALV Claims Cyber Operations Targeting Mexican State Government Entities in Support of Indigenous Communities",
            "publish_date": "2025-02-26T14:25:00Z",
            "last_updated": "2025-02-28T16:40:00Z",
            "summary": "Topic: Ideological Hacktivism || Target Industry: Government || Target Geography: Mexico\n\nIn social media posts from 1–19 February 2025, likely hacktivist group Don Benito Juarez (a.k.a. DonBenitoALV)—whose moniker evokes Mexican historical political figure Benito Juárez—released leaks and claimed to have deleted data purportedly from several Mexican government entities.",
            "url": "https://falcon.crowdstrike.com/intelligence/reports/csa-250239",
            "threat_groups": ["DonBenitoALV"],
            "targeted_sectors": ["Government"],
            "nation_affiliations": [],
            "targeted_countries": ["Mexico"],
            "raw_data": {}
        }
    ]
    
    # Generate additional reports if needed
    while len(reports) < count:
        # Duplicate a report with a different ID
        report = reports[len(reports) % 5].copy()
        report["id"] = f"cs-report-{len(reports) + 1}"
        reports.append(report)
    
    # Return only the requested number of reports
    return reports[:count]

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
    """
    Generate a simple error message instead of sample data.
    
    Args:
        count: Number of items requested (unused)
        
    Returns:
        A list with a single error object
    """
    logger.info("Sample data generation has been disabled")
    
    return [{
        "id": "error-404",
        "name": "404 Not Found",
        "publish_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "summary": "Could not retrieve intelligence data from the server. Sample data generation has been disabled.",
        "url": None,
        "threat_groups": [],
        "targeted_sectors": [],
        "nation_affiliations": [],
        "targeted_countries": [],
        "raw_data": {}
    }]

def save_to_database(reports: List[Dict]) -> Tuple[int, int]:
    """
    Save reports to the database.
    
    Args:
        reports: List of reports to save
        
    Returns:
        tuple: (created_count, updated_count)
    """
    if not DJANGO_AVAILABLE:
        logger.warning("Django not available, skipping database save")
        return 0, 0
    
    created_count = 0
    updated_count = 0
    
    try:
        for report in reports:
            # Try to get existing report
            obj, created = CrowdStrikeTailoredIntel.objects.update_or_create(
                report_id=report['id'],
                defaults={
                    'title': report['name'],
                    'publish_date': report['publish_date'],
                    'last_updated': report['last_updated'],
                    'summary': report['summary'],
                    'report_url': report.get('url', ''),
                    # Keep updating the old text fields for backward compatibility
                    'threat_groups': ','.join(report['threat_groups']) if report.get('threat_groups') else '',
                    'targeted_sectors': ','.join(report['targeted_sectors']) if report.get('targeted_sectors') else '',
                    # Update the new JSON fields
                    'threat_groups_json': report['threat_groups'] if report.get('threat_groups') else [],
                    'targeted_sectors_json': report['targeted_sectors'] if report.get('targeted_sectors') else [],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
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
            # Prefer JSON fields if available, otherwise fall back to text fields
            threat_groups = report.threat_groups_json if report.threat_groups_json else (report.threat_groups.split(",") if report.threat_groups else [])
            targeted_sectors = report.targeted_sectors_json if report.targeted_sectors_json else (report.targeted_sectors.split(",") if report.targeted_sectors else [])
            
            reports.append({
                "id": report.report_id,
                "name": report.title,
                "publish_date": report.publish_date.strftime("%Y-%m-%d") if hasattr(report.publish_date, 'strftime') else report.publish_date,
                "last_updated": report.last_updated.strftime("%Y-%m-%d") if hasattr(report.last_updated, 'strftime') else report.last_updated,
                "summary": report.summary,
                "url": report.report_url,
                "threat_groups": threat_groups,
                "targeted_sectors": targeted_sectors,
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
    
    # Get API connection
    falcon = get_falcon_api()
    if not falcon:
        logger.error("Cannot access CrowdStrike API. Please check your API credentials.")
        logger.info("Falling back to sample data with real CrowdStrike URLs")
        return generate_sample_data(15)
    
    # Fetch data
    reports = fetch_tailored_intel(falcon=falcon, use_cache=use_cache and not force_refresh)
    
    if not reports:
        logger.warning("No tailored intelligence reports fetched from API")
        logger.info("Falling back to sample data with real CrowdStrike URLs")
        return generate_sample_data(15)
    
    # Process reports
    processed_reports = process_reports(reports)
    
    # Update database
    created, updated = update_database(processed_reports)
    logger.info(f"Database update complete: {created} reports created, {updated} reports updated")
    
    return processed_reports

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

def get_cached_data(key: str) -> Optional[Any]:
    """Get data from Redis cache if available."""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Error getting cached data: {str(e)}")
    
    return None

def set_cached_data(key: str, data: Any, expiry: int = 3600) -> bool:
    """Set data in Redis cache if available."""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.setex(key, expiry, json.dumps(data))
        return True
    except Exception as e:
        logger.warning(f"Error setting cached data: {str(e)}")
    
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