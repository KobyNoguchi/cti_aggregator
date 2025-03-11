#!/usr/bin/env python3
"""
Module for fetching and processing extended CrowdStrike Tailored Intelligence data.
This module extends the existing tailored_intelligence.py to include additional fields:
- Source
- Hit Type
- Matched rule names
- Details
- First Seen

It uses the FalconPy API to fetch data from CrowdStrike.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logger.info(f"Loaded environment variables from {dotenv_path}")
    else:
        logger.warning(f"No .env file found at {dotenv_path}")
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables must be set manually.")

# Try to import FalconPy
try:
    from falconpy import Intel
    FALCONPY_AVAILABLE = True
except ImportError:
    logger.error("Could not import FalconPy. Install with: pip install falconpy")
    FALCONPY_AVAILABLE = False

# Set up Django environment
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    import django
    django.setup()
    
    # Import models
    from ioc_scraper.models import CrowdStrikeTailoredIntel
    DJANGO_AVAILABLE = True
except Exception as e:
    logger.warning(f"Django environment not available: {str(e)}")
    DJANGO_AVAILABLE = False

def get_intel_client():
    """
    Get a FalconPy Intel client instance with credentials from env variables.
    
    Returns:
        Intel: FalconPy Intel client instance or None if credentials are missing
    """
    # Get API credentials from environment variables
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.error("CrowdStrike API credentials not found in environment variables")
        logger.error("Please set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET in your .env file")
        return None
    
    try:
        # Initialize the Intel API client
        intel_client = Intel(client_id=client_id, client_secret=client_secret)
        return intel_client
    except Exception as e:
        logger.error(f"Error initializing Intel client: {str(e)}")
        return None

def fetch_extended_tailored_intel(limit: int = 100) -> List[Dict]:
    """
    Fetch extended tailored intelligence data from CrowdStrike API.
    
    Args:
        limit: Maximum number of indicators to fetch
        
    Returns:
        List of indicator dictionaries with extended fields
    """
    if not FALCONPY_AVAILABLE:
        logger.error("FalconPy library not available")
        return []
    
    # Get Intel client
    intel_client = get_intel_client()
    if not intel_client:
        return []
    
    try:
        # Query for indicators
        query_params = {
            "limit": limit,
            "sort": "first_seen.desc"  # Sort by first seen date, newest first
        }
        
        response = intel_client.query_intel_indicators_v1(**query_params)
        
        if response["status_code"] != 200:
            logger.error(f"Failed to query indicators: {response}")
            return []
        
        if not response["body"]["resources"] or len(response["body"]["resources"]) == 0:
            logger.warning("No indicators found")
            return []
        
        logger.info(f"Found {len(response['body']['resources'])} indicators")
        
        # Get details for the indicators
        indicator_ids = response["body"]["resources"]
        
        # Get details for each indicator
        details_params = {
            "ids": indicator_ids
        }
        
        details_response = intel_client.get_intel_indicators_entities_v1(**details_params)
        
        if details_response["status_code"] != 200:
            logger.error(f"Failed to get indicator details: {details_response}")
            return []
        
        if not details_response["body"]["resources"] or len(details_response["body"]["resources"]) == 0:
            logger.warning("No indicator details found")
            return []
        
        # Process the results
        indicators = details_response["body"]["resources"]
        logger.info(f"Retrieved details for {len(indicators)} indicators")
        
        # Transform the data into our expected format
        processed_indicators = []
        for indicator in indicators:
            processed = {
                "id": indicator.get("id", ""),
                "indicator": indicator.get("indicator", ""),
                "type": indicator.get("type", ""),
                "source": indicator.get("source", ""),
                "hit_type": indicator.get("malicious_confidence", ""),
                "matched_rule_names": indicator.get("rule_names", []),
                "details": indicator.get("description", ""),
                "first_seen": indicator.get("first_seen", ""),
                "last_seen": indicator.get("last_seen", ""),
                "published_date": indicator.get("published_date", ""),
                "malware_families": indicator.get("malware_families", []),
                "threat_groups": indicator.get("actors", []),
                "raw_data": indicator
            }
            processed_indicators.append(processed)
        
        return processed_indicators
    
    except Exception as e:
        logger.error(f"Error fetching extended tailored intelligence: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def update_model_for_extended_fields():
    """
    Update the Django model to support the extended fields.
    This function should be called once to migrate the database.
    
    Note: In a production environment, you would use Django migrations instead.
    """
    if not DJANGO_AVAILABLE:
        logger.error("Django not available, cannot update model")
        return False
    
    try:
        from django.db import models
        
        # Check if the model already has the extended fields
        model_fields = [f.name for f in CrowdStrikeTailoredIntel._meta.get_fields()]
        
        # List of fields to add
        new_fields = [
            ('source', models.CharField(max_length=255, null=True, blank=True)),
            ('hit_type', models.CharField(max_length=255, null=True, blank=True)),
            ('matched_rule_names', models.JSONField(default=list, null=True, blank=True)),
            ('details', models.TextField(null=True, blank=True)),
            ('first_seen', models.DateTimeField(null=True, blank=True))
        ]
        
        # Add fields that don't already exist
        for field_name, field_type in new_fields:
            if field_name not in model_fields:
                logger.info(f"Adding field {field_name} to CrowdStrikeTailoredIntel model")
                field_type.contribute_to_class(CrowdStrikeTailoredIntel, field_name)
        
        logger.info("Model updated successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating model: {str(e)}")
        return False

def save_extended_tailored_intel(indicators: List[Dict]) -> Tuple[int, int]:
    """
    Save extended tailored intelligence data to the database.
    
    Args:
        indicators: List of processed indicators
        
    Returns:
        Tuple of (created_count, updated_count)
    """
    if not DJANGO_AVAILABLE:
        logger.error("Django not available, cannot save to database")
        return (0, 0)
    
    created_count = 0
    updated_count = 0
    
    try:
        # Update the model to support extended fields
        update_model_for_extended_fields()
        
        # Save each indicator
        for indicator in indicators:
            # Try to get existing record or create a new one
            obj, created = CrowdStrikeTailoredIntel.objects.update_or_create(
                report_id=indicator["id"],
                defaults={
                    'title': indicator["indicator"],
                    'summary': indicator["details"],
                    'publish_date': indicator["published_date"] or indicator["first_seen"],
                    'last_updated': indicator["last_seen"],
                    'report_url': f"https://falcon.crowdstrike.com/intelligence/indicators/{indicator['id']}",
                    'threat_groups': ','.join(indicator["threat_groups"]) if indicator["threat_groups"] else '',
                    'threat_groups_json': indicator["threat_groups"],
                    'source': indicator["source"],
                    'hit_type': indicator["hit_type"],
                    'matched_rule_names': indicator["matched_rule_names"],
                    'details': indicator["details"],
                    'first_seen': indicator["first_seen"]
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Saved {created_count} new and updated {updated_count} existing indicators")
        return (created_count, updated_count)
    
    except Exception as e:
        logger.error(f"Error saving extended tailored intelligence: {str(e)}")
        import traceback
        traceback.print_exc()
        return (0, 0)

def run_update(limit: int = 100) -> List[Dict]:
    """
    Run the extended tailored intelligence update process.
    
    Args:
        limit: Maximum number of indicators to fetch
        
    Returns:
        List of processed indicators
    """
    logger.info("Starting extended tailored intelligence update")
    
    # Fetch data
    indicators = fetch_extended_tailored_intel(limit)
    
    if not indicators:
        logger.warning("No extended tailored intelligence indicators fetched")
        return []
    
    # Save to database
    if DJANGO_AVAILABLE:
        created, updated = save_extended_tailored_intel(indicators)
        logger.info(f"Database update complete: {created} indicators created, {updated} indicators updated")
    
    return indicators

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extended Tailored Intelligence Update Tool")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of indicators to fetch")
    
    args = parser.parse_args()
    
    indicators = run_update(args.limit)
    print(f"Updated {len(indicators)} extended tailored intelligence indicators") 