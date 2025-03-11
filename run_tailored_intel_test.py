#!/usr/bin/env python3
"""
Test script for running the tailored intelligence update
"""

import sys
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join('cti_aggregator', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"Warning: .env file not found at {env_path}")

# Check if we have the required environment variables
client_id = os.environ.get('FALCON_CLIENT_ID')
client_secret = os.environ.get('FALCON_CLIENT_SECRET')

if not client_id or not client_secret:
    logger.error("CrowdStrike API credentials not found in environment variables")
    logger.error("Please set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET")
    sys.exit(1)

logger.info(f"Using client ID: {client_id[:5]}...{client_id[-5:] if len(client_id) > 10 else ''}")

# Check if FalconPy is available
try:
    from falconpy import Intel
    logger.info("FalconPy is installed")
except ImportError:
    logger.error("FalconPy is not installed. Please install it with: pip install crowdstrike-falconpy")
    sys.exit(1)

def fetch_intel_reports():
    """Fetch intelligence reports directly using the Intel API"""
    try:
        # Initialize the Intel API client
        logger.info("Initializing Intel API client...")
        intel_client = Intel(client_id=client_id, client_secret=client_secret)
        logger.info("Successfully initialized Intel API connection")
        
        # Query for report IDs
        logger.info("Querying for intelligence report IDs...")
        params = {
            "limit": 20,  # Get a reasonable number of reports
            "sort": "created_date.desc"  # Sort by creation date, newest first
        }
        
        # Query for report IDs
        response = intel_client.query_report_ids(**params)
        
        if response["status_code"] != 200:
            error_msg = response.get("body", {}).get("errors", ["Unknown error"])
            logger.error(f"API request failed: {error_msg}")
            return []
        
        # Extract report IDs from the response
        report_ids = response["body"].get("resources", [])
        
        if not report_ids:
            logger.warning("No intelligence report IDs returned from API")
            return []
        
        logger.info(f"Found {len(report_ids)} intelligence report IDs")
        
        # Get details for the reports
        if not report_ids:
            return []
            
        # Get details for the first 5 reports as an example
        sample_ids = report_ids[:5]
        logger.info(f"Getting details for {len(sample_ids)} reports...")
        
        report_response = intel_client.get_report_entities(ids=sample_ids)
        
        if report_response["status_code"] != 200:
            error_msg = report_response.get("body", {}).get("errors", ["Unknown error"])
            logger.error(f"Failed to get report details: {error_msg}")
            return []
        
        reports = report_response["body"].get("resources", [])
        
        if not reports:
            logger.warning("No report details returned from API")
            return []
        
        logger.info(f"Successfully retrieved {len(reports)} reports")
        
        # Process the reports
        processed_reports = []
        for report in reports:
            processed_report = {
                "id": report.get("id", ""),
                "name": report.get("name", ""),
                "publish_date": report.get("created_date", ""),
                "last_updated": report.get("last_modified_date", ""),
                "summary": report.get("short_description", report.get("description", "")),
                "url": report.get("url", ""),
                "threat_groups": [actor.get("name", "") for actor in report.get("actors", [])],
                "targeted_sectors": [industry.get("value", "") for industry in report.get("target_industries", [])],
                "nation_affiliations": [origin.get("value", "") for origin in report.get("origins", []) 
                                      if origin.get("type", "") == "country"],
                "targeted_countries": [country.get("value", "") for country in report.get("target_countries", [])],
            }
            processed_reports.append(processed_report)
        
        return processed_reports
    except Exception as e:
        logger.error(f"Error fetching intelligence reports: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Run the test and print results"""
    
    # Fetch reports directly using the Intel API
    logger.info("Fetching intelligence reports...")
    reports = fetch_intel_reports()
    
    # Print results
    logger.info(f"Retrieved {len(reports)} reports")
    
    if not reports:
        logger.warning("No reports retrieved")
        return 1
    
    # Print details of the reports
    for i, report in enumerate(reports):
        logger.info(f"Report {i+1}:")
        logger.info(f"  ID: {report.get('id', 'N/A')}")
        logger.info(f"  Title: {report.get('name', 'N/A')}")
        logger.info(f"  Date: {report.get('publish_date', 'N/A')}")
        logger.info(f"  URL: {report.get('url', 'N/A')}")
        logger.info(f"  Summary: {report.get('summary', 'N/A')[:100]}...")
        logger.info(f"  Threat Groups: {report.get('threat_groups', [])}")
        logger.info(f"  Targeted Sectors: {report.get('targeted_sectors', [])}")
        logger.info("")
    
    # Save the reports to a JSON file for reference
    output_file = "intel_reports.json"
    with open(output_file, "w") as f:
        json.dump(reports, f, indent=2)
    
    logger.info(f"Saved reports to {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 