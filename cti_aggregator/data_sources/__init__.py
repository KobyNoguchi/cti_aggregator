"""
CTI Aggregator Data Sources Package

This package contains modules for fetching and processing data from various threat intelligence sources.
"""

import os
import sys
import logging

# Add the parent directory to the Python path to allow imports to work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Also add the backend directory for direct Django model imports
backend_dir = os.path.join(parent_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configure a logger for this package
logger = logging.getLogger(__name__) 