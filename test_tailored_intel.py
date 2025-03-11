#!/usr/bin/env python3
"""
Test script for CrowdStrike Tailored Intelligence API
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

def test_tailored_intelligence_api():
    """Test CrowdStrike Tailored Intelligence API connection and fetch reports"""
    
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
        from falconpy import TailoredIntelligence
        from falconpy import APIHarness
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
    
    # Initialize the Intel API client
    try:
        print("\n1. Initializing Intel API client...")
        intel_client = Intel(client_id=client_id, client_secret=client_secret)
        print("Successfully initialized Intel API connection")
        
        # Test query for Intel reports
        print("\n2. Testing Intel API with a report query...")
        params = {
            "limit": 5,
            "sort": "created_date.desc"
        }
        
        # Query for Intel report IDs
        response = intel_client.query_report_ids(**params)
        
        if response["status_code"] != 200:
            error_msg = response.get("body", {}).get("errors", ["Unknown error"])
            print(f"Intel API request failed: {error_msg}")
        else:
            report_ids = response["body"].get("resources", [])
            print(f"Found {len(report_ids)} Intel report IDs")
            
            if report_ids:
                print(f"First few report IDs: {report_ids[:3]}")
                
                # Get details for one report as an example
                print("\n3. Getting details for one report...")
                report_response = intel_client.get_report_entities(ids=[report_ids[0]])
                
                if report_response["status_code"] == 200:
                    reports = report_response["body"].get("resources", [])
                    if reports:
                        report = reports[0]
                        print(f"Report title: {report.get('name', 'N/A')}")
                        print(f"Report date: {report.get('created_date', 'N/A')}")
                        print(f"Report summary: {report.get('short_description', 'N/A')[:100]}...")
                    else:
                        print("No report details found")
                else:
                    print(f"Failed to get report details: {report_response.get('body', {}).get('errors', ['Unknown error'])}")
        
        # Initialize the Tailored Intelligence API client
        print("\n4. Initializing Tailored Intelligence API client...")
        tailored_client = TailoredIntelligence(client_id=client_id, client_secret=client_secret)
        print("Successfully initialized Tailored Intelligence API connection")
        
        # Available methods in TailoredIntelligence class
        available_methods = [method for method in dir(tailored_client) 
                             if callable(getattr(tailored_client, method)) and not method.startswith('_')]
        print(f"Available methods: {', '.join(available_methods[:10])}...")
        
        # Test query for Tailored Intelligence events
        print("\n5. Testing Tailored Intelligence API with an events query...")
        event_params = {
            "limit": 5,
            "sort": "date.desc"
        }
        
        try:
            # Try to query for events
            print("Querying for Tailored Intelligence events...")
            event_response = tailored_client.query_events(**event_params)
            
            print(f"API Response Status: {event_response['status_code']}")
            print(f"API Response Body: {json.dumps(event_response.get('body', {}), indent=2)}")
            
            if event_response["status_code"] != 200:
                error_msg = event_response.get("body", {}).get("errors", ["Unknown error"])
                print(f"Tailored Intelligence API events request failed: {error_msg}")
            else:
                event_ids = event_response["body"].get("resources", [])
                print(f"Found {len(event_ids)} Tailored Intelligence event IDs")
        except Exception as e:
            print(f"Error querying for events: {str(e)}")
        
        # Test query for Tailored Intelligence rules
        print("\n6. Testing Tailored Intelligence API with a rules query...")
        rule_params = {
            "limit": 5,
            "sort": "updated_date.desc" 
        }
        
        try:
            # Try to query for rules
            print("Querying for Tailored Intelligence rules...")
            rule_response = tailored_client.query_rules(**rule_params)
            
            print(f"API Response Status: {rule_response['status_code']}")
            print(f"API Response Body: {json.dumps(rule_response.get('body', {}), indent=2)}")
            
            if rule_response["status_code"] != 200:
                error_msg = rule_response.get("body", {}).get("errors", ["Unknown error"])
                print(f"Tailored Intelligence API rules request failed: {error_msg}")
            else:
                rule_ids = rule_response["body"].get("resources", [])
                print(f"Found {len(rule_ids)} Tailored Intelligence rule IDs")
        except Exception as e:
            print(f"Error querying for rules: {str(e)}")
        
        # Try using the generic API client as a fallback
        print("\n7. Testing generic API client for available Intel endpoints...")
        generic_client = APIHarness(client_id=client_id, client_secret=client_secret)
        
        # Get all available Intel-related commands
        intel_commands = [cmd for cmd in generic_client.commands if isinstance(cmd, str) and 'intel' in cmd.lower()]
        print(f"Found {len(intel_commands)} Intel-related commands")
        print(f"Sample commands: {', '.join(intel_commands[:10])}...")
        
        # Try to find Tailored Intelligence specific commands
        tailored_commands = [cmd for cmd in intel_commands if 'tailor' in cmd.lower()]
        print(f"Found {len(tailored_commands)} Tailored Intelligence specific commands: {', '.join(tailored_commands)}")
        
        return True
    except Exception as e:
        print(f"Error testing Falcon API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tailored_intelligence_api()
    print(f"\nTest {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1) 