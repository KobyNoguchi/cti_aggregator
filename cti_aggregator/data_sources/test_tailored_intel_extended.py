#!/usr/bin/env python3
"""
Test script for querying CrowdStrike Tailored Intelligence data with extended fields.
This script tests the ability to query and display the following fields:
- Source
- Hit Type
- Matched rule names
- Details
- First Seen

Usage:
    python test_tailored_intel_extended.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    sys.exit(1)

def test_query_tailored_intel_extended():
    """
    Test querying CrowdStrike Tailored Intelligence data with extended fields.
    """
    logger.info("Testing query for CrowdStrike Tailored Intelligence with extended fields")
    
    # Get API credentials from environment variables
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.error("CrowdStrike API credentials not found in environment variables")
        logger.error("Please set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET in your .env file")
        return False
    
    try:
        # Initialize the Intel API client
        intel_client = Intel(client_id=client_id, client_secret=client_secret)
        
        # Test authentication
        logger.info("Testing API authentication...")
        response = intel_client.query_intel_indicators_v1(limit=1)
        
        if response["status_code"] != 200:
            logger.error(f"Authentication failed: {response}")
            return False
        
        logger.info("Authentication successful!")
        
        # Query for tailored intelligence with extended fields
        logger.info("Querying for tailored intelligence with extended fields...")
        
        # First, query for indicators to get IDs
        query_params = {
            "limit": 10,  # Limit to 10 results for testing
            "sort": "first_seen.desc"  # Sort by first seen date, newest first
        }
        
        response = intel_client.query_intel_indicators_v1(**query_params)
        
        if response["status_code"] != 200:
            logger.error(f"Failed to query indicators: {response}")
            return False
        
        if not response["body"]["resources"] or len(response["body"]["resources"]) == 0:
            logger.warning("No indicators found")
            return False
        
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
            return False
        
        if not details_response["body"]["resources"] or len(details_response["body"]["resources"]) == 0:
            logger.warning("No indicator details found")
            return False
        
        # Process and display the results
        indicators = details_response["body"]["resources"]
        logger.info(f"Retrieved details for {len(indicators)} indicators")
        
        # Display the results with the requested fields
        print("\n=== CrowdStrike Tailored Intelligence Indicators ===\n")
        for indicator in indicators:
            print(f"Indicator: {indicator.get('indicator', 'N/A')}")
            print(f"Type: {indicator.get('type', 'N/A')}")
            print(f"Source: {indicator.get('source', 'N/A')}")
            print(f"Hit Type: {indicator.get('malicious_confidence', 'N/A')}")
            
            # Matched rule names (if available)
            rules = indicator.get('rule_names', [])
            if rules:
                print("Matched Rules:")
                for rule in rules:
                    print(f"  - {rule}")
            else:
                print("Matched Rules: None")
            
            # Details
            print(f"Details: {indicator.get('description', 'N/A')}")
            
            # First Seen
            first_seen = indicator.get('first_seen', 'N/A')
            if first_seen:
                print(f"First Seen: {first_seen}")
            else:
                print("First Seen: N/A")
            
            print("\n" + "-" * 50 + "\n")
        
        logger.info("Test completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error testing tailored intelligence query: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_query_tailored_intel_extended()
    sys.exit(0 if success else 1) 