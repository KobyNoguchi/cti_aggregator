#!/usr/bin/env python3
"""
Script to update the database with the latest tailored intelligence reports
"""

import os
import sys
import logging
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

# Add the project root to the Python path
sys.path.insert(0, '.')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cti_aggregator.backend.backend.settings')

try:
    import django
    django.setup()
    logger.info("Django environment set up successfully")
except Exception as e:
    logger.error(f"Error setting up Django environment: {str(e)}")
    sys.exit(1)

def main():
    """Update the database with the latest tailored intelligence reports"""
    
    try:
        # Import the run_update function
        from cti_aggregator.data_sources.tailored_intelligence import run_update
        
        # Run the update with force_refresh=True to bypass caching
        logger.info("Running tailored intelligence update...")
        reports = run_update(force_refresh=True)
        
        # Print results
        logger.info(f"Retrieved and processed {len(reports)} reports")
        
        return 0
    except Exception as e:
        logger.error(f"Error updating tailored intelligence: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 