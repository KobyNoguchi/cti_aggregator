#!/usr/bin/env python
"""
Tailored Intelligence Update Script

This script runs the tailored intelligence update process, which fetches
tailored intelligence reports, processes them, and updates the database.

Usage:
    python run_tailored_intel_update.py [--test] [--force-refresh] [--no-cache]

Options:
    --test           Run tests for the tailored intelligence module
    --force-refresh  Force refresh of data even if cached
    --no-cache       Disable Redis caching
"""

import os
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def main():
    """Main entry point for the script."""
    start_time = time.time()
    
    try:
        # Import the tailored intelligence module
        from data_sources.tailored_intelligence import run_update, run_tests
        
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description="Tailored Intelligence Update Tool")
        parser.add_argument("--test", action="store_true", help="Run tests")
        parser.add_argument("--force-refresh", action="store_true", help="Force refresh of data")
        parser.add_argument("--no-cache", action="store_true", help="Disable Redis caching")
        
        args = parser.parse_args()
        
        if args.test:
            logger.info("Running tailored intelligence tests")
            success = run_tests()
            if success:
                logger.info("All tests passed successfully")
                print("Tailored Intelligence Tests: PASSED")
                sys.exit(0)
            else:
                logger.error("Tests failed")
                print("Tailored Intelligence Tests: FAILED")
                sys.exit(1)
        else:
            logger.info("Running tailored intelligence update")
            reports = run_update(use_cache=not args.no_cache, force_refresh=args.force_refresh)
            
            if reports:
                logger.info(f"Successfully updated {len(reports)} tailored intelligence reports")
                print(f"Updated {len(reports)} tailored intelligence reports")
                sys.exit(0)
            else:
                logger.warning("No tailored intelligence reports found")
                print("No tailored intelligence reports found")
                sys.exit(1)
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running tailored intelligence update: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Script completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main() 