#!/usr/bin/env python3
"""
Test script for the CrowdStrike Tailored Intelligence module.
This script tests the functionality of the tailored_intelligence.py module.
"""

import os
import sys
import json
import logging
from datetime import datetime
from unittest.mock import patch

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_generate_mock_data():
    """Test the generate_mock_data function"""
    try:
        from tailored_intelligence import generate_mock_data
        
        # Test with default count
        mock_reports = generate_mock_data()
        assert isinstance(mock_reports, list), "Expected mock_reports to be a list"
        assert len(mock_reports) == 20, f"Expected 20 mock reports, got {len(mock_reports)}"
        
        # Test with custom count
        mock_reports = generate_mock_data(5)
        assert len(mock_reports) == 5, f"Expected 5 mock reports, got {len(mock_reports)}"
        
        # Check report structure
        required_fields = ['id', 'name', 'publish_date', 'last_update', 'summary', 
                           'threat_groups', 'nation_affiliations', 'targeted_sectors', 
                           'targeted_countries', 'url']
        
        for report in mock_reports:
            for field in required_fields:
                assert field in report, f"Required field '{field}' missing from mock report"
        
        logger.info("test_generate_mock_data passed")
        return True
    except Exception as e:
        logger.error(f"test_generate_mock_data failed: {str(e)}")
        return False

def test_process_reports():
    """Test the process_reports function"""
    try:
        from tailored_intelligence import generate_mock_data, process_reports
        
        # Generate mock data
        mock_reports = generate_mock_data(3)
        
        # Process reports
        processed_reports = process_reports(mock_reports)
        
        # Validate
        assert len(processed_reports) == 3, f"Expected 3 processed reports, got {len(processed_reports)}"
        
        # Check structure
        required_fields = ['id', 'name', 'publish_date', 'last_updated', 'summary', 
                           'url', 'threat_groups', 'nation_affiliations', 'targeted_sectors', 
                           'targeted_countries', 'raw_data']
        
        for report in processed_reports:
            for field in required_fields:
                assert field in report, f"Required field '{field}' missing from processed report"
        
        logger.info("test_process_reports passed")
        return True
    except Exception as e:
        logger.error(f"test_process_reports failed: {str(e)}")
        return False

@patch('tailored_intelligence.CrowdStrikeTailoredIntel.objects.update_or_create')
def test_update_database(mock_update_or_create):
    """Test the update_database function"""
    try:
        from tailored_intelligence import generate_mock_data, process_reports, update_database
        
        # Configure mock
        mock_update_or_create.return_value = (None, True)  # (obj, created)
        
        # Generate and process mock data
        mock_reports = generate_mock_data(3)
        processed_reports = process_reports(mock_reports)
        
        # Update database
        created, updated, total = update_database(processed_reports)
        
        # Validate
        assert created == 3, f"Expected 3 created reports, got {created}"
        assert updated == 0, f"Expected 0 updated reports, got {updated}"
        assert total == 3, f"Expected 3 total reports, got {total}"
        assert mock_update_or_create.call_count == 3, f"Expected 3 calls to update_or_create, got {mock_update_or_create.call_count}"
        
        # Test updating instead of creating
        mock_update_or_create.reset_mock()
        mock_update_or_create.return_value = (None, False)  # (obj, updated)
        
        created, updated, total = update_database(processed_reports)
        
        # Validate
        assert created == 0, f"Expected 0 created reports, got {created}"
        assert updated == 3, f"Expected 3 updated reports, got {updated}"
        assert total == 3, f"Expected 3 total reports, got {total}"
        
        logger.info("test_update_database passed")
        return True
    except Exception as e:
        logger.error(f"test_update_database failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests for the tailored intelligence module"""
    logger.info("Running all tests for tailored intelligence module")
    
    tests = [
        test_generate_mock_data,
        test_process_reports,
        test_update_database
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
        if not result:
            logger.error(f"Test {test_func.__name__} failed")
    
    success_count = sum(results)
    total_count = len(results)
    
    logger.info(f"Tests completed: {success_count}/{total_count} passed")
    
    return all(results)

if __name__ == '__main__':
    run_all_tests() 