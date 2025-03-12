#!/usr/bin/env python3
"""
Script to run the test for non-Microsoft threat intelligence sources and generate a report.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import unittest
from unittest.runner import TextTestResult
from unittest.suite import TestSuite

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the test
from test_non_microsoft_sources import NonMicrosoftSourcesTest

class DetailedTestResult(TextTestResult):
    """Enhanced test result class to capture detailed information about test runs."""
    
    def __init__(self, *args, **kwargs):
        super(DetailedTestResult, self).__init__(*args, **kwargs)
        self.test_results = []
        self.start_time = datetime.now()
        
    def addSuccess(self, test):
        super(DetailedTestResult, self).addSuccess(test)
        self.test_results.append({
            'name': test.id(),
            'status': 'PASS',
            'details': str(test),
            'time': str(datetime.now() - self.start_time)
        })
        self.start_time = datetime.now()
        
    def addFailure(self, test, err):
        super(DetailedTestResult, self).addFailure(test, err)
        self.test_results.append({
            'name': test.id(),
            'status': 'FAIL',
            'details': str(test),
            'error': str(err[1]),
            'time': str(datetime.now() - self.start_time)
        })
        self.start_time = datetime.now()
        
    def addError(self, test, err):
        super(DetailedTestResult, self).addError(test, err)
        self.test_results.append({
            'name': test.id(),
            'status': 'ERROR',
            'details': str(test),
            'error': str(err[1]),
            'time': str(datetime.now() - self.start_time)
        })
        self.start_time = datetime.now()
        
def run_tests(output_file=None, verbose=False):
    """Run the tests and generate a report."""
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(NonMicrosoftSourcesTest)
    
    # Create a test runner with the detailed result class
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        resultclass=DetailedTestResult
    )
    
    # Run the tests
    print("\n==========================================")
    print("Running Non-Microsoft Threat Intel Tests")
    print("==========================================\n")
    
    result = runner.run(suite)
    
    # Create a report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'passed': len(result.test_results) - len(result.failures) - len(result.errors),
        'failures': len(result.failures),
        'errors': len(result.errors),
        'details': result.test_results
    }
    
    # Calculate success percentage
    if result.testsRun > 0:
        success_percentage = (report['passed'] / result.testsRun) * 100
        report['success_percentage'] = round(success_percentage, 2)
    else:
        report['success_percentage'] = 0

    # Print summary
    print("\n==========================================")
    print(f"Test Summary")
    print(f"==========================================")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']} ({report['success_percentage']}%)")
    print(f"Failed: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print("==========================================\n")
    
    # Write report to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
    
    return result.wasSuccessful()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run non-Microsoft threat intelligence source tests')
    parser.add_argument('--output', '-o', type=str, help='Output file to save detailed results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    args = parser.parse_args()
    
    # Use a timestamp-based filename if not specified
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'non_ms_intel_test_report_{timestamp}.json'
    
    # Run the tests
    success = run_tests(output_file=args.output, verbose=args.verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 