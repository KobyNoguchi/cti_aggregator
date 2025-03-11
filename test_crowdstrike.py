#!/usr/bin/env python3
"""
Test script for CrowdStrike Falcon API connection
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_crowdstrike_api():
    """Test CrowdStrike API connection and fetch intel reports"""
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        # Load .env file from cti_aggregator directory
        env_path = os.path.join('cti_aggregator', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded environment variables from {env_path}")
        else:
            print(f"Warning: .env file not found at {env_path}")
    except ImportError:
        print("python-dotenv not installed, using existing environment variables")
    
    # Check if FalconPy is available
    try:
        from falconpy import Intel
        print("FalconPy is installed")
    except ImportError:
        print("FalconPy is not installed. Please install it with: pip install crowdstrike-falconpy")
        return False
    
    # Check for API credentials
    client_id = os.environ.get('FALCON_CLIENT_ID')
    client_secret = os.environ.get('FALCON_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("CrowdStrike API credentials not found in environment variables")
        print("Please set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET")
        return False
    
    print(f"Using client ID: {client_id[:5]}...{client_id[-5:] if len(client_id) > 10 else ''}")
    
    # Initialize the API client
    try:
        print("Initializing Intel API client...")
        client = Intel(client_id=client_id, client_secret=client_secret)
        print("Successfully initialized Falcon API connection")
    except Exception as e:
        print(f"Error initializing Falcon API: {str(e)}")
        return False
    
    # Test a simple API call
    try:
        print("Testing API with a simple query...")
        
        # Query for report IDs first
        params = {
            "limit": 5,  # Just get a few reports
            "sort": "created_date.desc"  # Sort by creation date, newest first
        }
        
        # Query for report IDs
        print("Querying for intelligence report IDs...")
        response = client.query_report_ids(**params)
        
        # Print the full response for debugging
        print(f"API Response Status: {response['status_code']}")
        print(f"API Response Body: {json.dumps(response.get('body', {}), indent=2)}")
        
        if response["status_code"] != 200:
            error_msg = response.get("body", {}).get("errors", ["Unknown error"])
            print(f"API request failed: {error_msg}")
            return False
        
        # Extract report IDs from the response
        report_ids = response["body"].get("resources", [])
        
        if not report_ids:
            print("No intelligence report IDs returned from API")
            return False
        
        print(f"Found {len(report_ids)} intelligence report IDs")
        print(f"Report IDs: {report_ids}")
        
        return True
    except Exception as e:
        print(f"Error testing Falcon API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crowdstrike_api()
    print(f"Test {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1) 