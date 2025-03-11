#!/usr/bin/env python3
"""
Script to run the extended tailored intelligence update.
This script fetches CrowdStrike Tailored Intelligence data with the additional fields:
- Source
- Hit Type
- Matched rule names
- Details
- First Seen

Usage:
    python run_tailored_intel_extended_update.py [--limit LIMIT]
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Main function to run the extended tailored intelligence update."""
    parser = argparse.ArgumentParser(description="Run Extended Tailored Intelligence Update")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of indicators to fetch")
    parser.add_argument("--test", action="store_true", help="Run in test mode (display results without saving)")
    
    args = parser.parse_args()
    
    try:
        # Import the module
        from data_sources.tailored_intel_extended import fetch_extended_tailored_intel, save_extended_tailored_intel, run_update
        
        if args.test:
            # Run in test mode
            logger.info("Running in test mode (display results without saving)")
            indicators = fetch_extended_tailored_intel(args.limit)
            
            if not indicators:
                logger.error("No indicators found")
                return 1
            
            # Display the results
            print(f"\n=== Found {len(indicators)} CrowdStrike Tailored Intelligence Indicators ===\n")
            
            for i, indicator in enumerate(indicators[:10]):  # Show first 10 for brevity
                print(f"Indicator {i+1}: {indicator['indicator']}")
                print(f"Type: {indicator['type']}")
                print(f"Source: {indicator['source']}")
                print(f"Hit Type: {indicator['hit_type']}")
                
                # Matched rule names
                if indicator['matched_rule_names']:
                    print("Matched Rules:")
                    for rule in indicator['matched_rule_names'][:3]:  # Show first 3 for brevity
                        print(f"  - {rule}")
                    if len(indicator['matched_rule_names']) > 3:
                        print(f"  - ... and {len(indicator['matched_rule_names']) - 3} more")
                else:
                    print("Matched Rules: None")
                
                # Details
                if indicator['details']:
                    details = indicator['details']
                    if len(details) > 100:
                        details = details[:100] + "..."
                    print(f"Details: {details}")
                else:
                    print("Details: None")
                
                # First Seen
                print(f"First Seen: {indicator['first_seen']}")
                
                print("\n" + "-" * 50 + "\n")
            
            if len(indicators) > 10:
                print(f"... and {len(indicators) - 10} more indicators\n")
            
            logger.info("Test completed successfully")
            return 0
        else:
            # Run the update
            logger.info(f"Running extended tailored intelligence update with limit {args.limit}")
            indicators = run_update(args.limit)
            
            if not indicators:
                logger.error("No indicators found")
                return 1
            
            logger.info(f"Successfully updated {len(indicators)} indicators")
            return 0
    
    except Exception as e:
        logger.error(f"Error running extended tailored intelligence update: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 