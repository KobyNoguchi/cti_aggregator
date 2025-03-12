#!/usr/bin/env python
"""
Script to fetch and populate the database with CrowdStrike Tailored Intelligence data.
Run this script to fetch data from the CrowdStrike API and save it to the database.
"""

import os
import sys
import django
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Apply Django settings before importing models
django.setup()

# Import data sources module after Django setup
from data_sources.tailored_intelligence import run_update, get_falcon_api
from falconpy import APIHarness

# Import Django models
from ioc_scraper.models import CrowdStrikeTailoredIntel

def list_api_operations():
    """List all available API operations for debugging."""
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.error("API credentials not found in environment variables.")
        return
    
    try:
        falcon = APIHarness(client_id=client_id, client_secret=client_secret)
        
        # The commands attribute is a list of operation names
        operations = falcon.commands
        logger.info(f"Available API operations: {len(operations)}")
        
        # Print operations related to intelligence, reports, or entities
        intel_ops = [op for op in operations if isinstance(op, str) and ('intel' in op.lower() or 'report' in op.lower() or 'entities' in op.lower())]
        logger.info(f"Intelligence-related operations: {len(intel_ops)}")
        for op in sorted(intel_ops):
            logger.info(f"  - {op}")
            
    except Exception as e:
        logger.error(f"Error listing API operations: {str(e)}")
        logger.exception(e)  # Print full exception for debugging

def save_to_database(reports):
    """Save reports to the database manually."""
    created_count = 0
    updated_count = 0
    
    for report in reports:
        try:
            # Try to get existing report
            try:
                obj = CrowdStrikeTailoredIntel.objects.get(report_id=report['id'])
                created = False
            except CrowdStrikeTailoredIntel.DoesNotExist:
                obj = CrowdStrikeTailoredIntel(report_id=report['id'])
                created = True
            
            # Update fields
            obj.title = report['name']
            obj.publish_date = report['publish_date']
            obj.last_updated = report['last_updated']
            obj.summary = report['summary']
            obj.report_url = report['url']
            obj.threat_groups = ','.join(report['threat_groups']) if report.get('threat_groups') else ''
            obj.targeted_sectors = ','.join(report['targeted_sectors']) if report.get('targeted_sectors') else ''
            
            # Save to database
            obj.save()
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as e:
            logger.error(f"Error updating database for report {report['id']}: {str(e)}")
    
    return created_count, updated_count, len(reports)

def main():
    """Main function to fetch and populate the database."""
    logger.info("Starting tailored intelligence data population")
    
    # List available API operations for debugging
    list_api_operations()
    
    # Check if API credentials are available
    falcon = get_falcon_api()
    if not falcon:
        logger.error("Failed to initialize CrowdStrike API client. Please check your environment variables.")
        logger.error("Make sure FALCON_CLIENT_ID and FALCON_CLIENT_SECRET are set in your .env file.")
        return 1
    
    # Fetch reports from the API
    reports = run_update(use_cache=False, force_refresh=True)
    
    if not reports:
        logger.error("Failed to fetch tailored intelligence data.")
        return 1
    
    # Save reports to database
    created, updated, total = save_to_database(reports)
    logger.info(f"Database update complete: {created} created, {updated} updated, {total} total")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 