#!/usr/bin/env python3
"""
Utility functions for managing Redis cache in the CTI Aggregator.
This module provides functions to cache and retrieve data from Redis.
"""

import os
import sys
import json
import logging
import redis
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

# Redis connection settings
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_CACHE_DB', 0))

# Redis key prefixes for different data types
TAILORED_INTEL_PREFIX = 'crowdstrike:tailored_intel:'
MALWARE_PREFIX = 'crowdstrike:malware:'
THREAT_ACTOR_PREFIX = 'crowdstrike:threat_actor:'
CISA_KEV_PREFIX = 'cisa:kev:'

# Default cache expiration times (in seconds)
DEFAULT_EXPIRY = 86400  # 24 hours
LONG_EXPIRY = 604800    # 7 days
SHORT_EXPIRY = 3600     # 1 hour

# Initialize Redis connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test connection
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {str(e)}")
    REDIS_AVAILABLE = False

def cache_data(key_prefix, key_suffix, data, expiry=DEFAULT_EXPIRY):
    """
    Cache data in Redis with the specified key and expiration time.
    
    Args:
        key_prefix (str): The prefix for the Redis key.
        key_suffix (str): The suffix for the Redis key.
        data (object): The data to cache (will be JSON serialized).
        expiry (int, optional): The cache expiration time in seconds. Defaults to DEFAULT_EXPIRY.
    
    Returns:
        bool: True if the data was successfully cached, False otherwise.
    """
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, skipping cache operation")
        return False
    
    full_key = f"{key_prefix}{key_suffix}"
    
    try:
        redis_client.setex(full_key, expiry, json.dumps(data))
        logger.info(f"Successfully cached data at key: {full_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to cache data at key {full_key}: {str(e)}")
        return False

def get_cached_data(key_prefix, key_suffix):
    """
    Retrieve data from Redis cache with the specified key.
    
    Args:
        key_prefix (str): The prefix for the Redis key.
        key_suffix (str): The suffix for the Redis key.
    
    Returns:
        object: The cached data (JSON deserialized) or None if not found.
    """
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, skipping cache retrieval")
        return None
    
    full_key = f"{key_prefix}{key_suffix}"
    
    try:
        cached_data = redis_client.get(full_key)
        if cached_data:
            logger.info(f"Retrieved cached data from key: {full_key}")
            return json.loads(cached_data)
        else:
            logger.info(f"No cached data found for key: {full_key}")
            return None
    except Exception as e:
        logger.error(f"Failed to retrieve cached data from key {full_key}: {str(e)}")
        return None

def cache_tailored_intel(data, cache_key='reports', expiry=DEFAULT_EXPIRY):
    """
    Cache CrowdStrike Tailored Intelligence data in Redis.
    
    Args:
        data (list): List of tailored intelligence reports.
        cache_key (str, optional): The cache key suffix. Defaults to 'reports'.
        expiry (int, optional): The cache expiration time in seconds. Defaults to DEFAULT_EXPIRY.
    
    Returns:
        bool: True if the data was successfully cached, False otherwise.
    """
    return cache_data(TAILORED_INTEL_PREFIX, cache_key, data, expiry)

def get_cached_tailored_intel(cache_key='reports'):
    """
    Retrieve CrowdStrike Tailored Intelligence data from Redis cache.
    
    Args:
        cache_key (str, optional): The cache key suffix. Defaults to 'reports'.
    
    Returns:
        list: List of tailored intelligence reports or None if not found.
    """
    return get_cached_data(TAILORED_INTEL_PREFIX, cache_key)

def clear_cache(key_prefix='*'):
    """
    Clear all cache entries matching the specified prefix.
    
    Args:
        key_prefix (str, optional): The prefix for keys to clear. Defaults to '*' (all keys).
    
    Returns:
        int: The number of keys cleared.
    """
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, skipping cache clear operation")
        return 0
    
    try:
        pattern = f"{key_prefix}*" if key_prefix != '*' else '*'
        keys = redis_client.keys(pattern)
        if keys:
            count = redis_client.delete(*keys)
            logger.info(f"Cleared {count} cache entries with prefix: {key_prefix}")
            return count
        else:
            logger.info(f"No cache entries found with prefix: {key_prefix}")
            return 0
    except Exception as e:
        logger.error(f"Failed to clear cache with prefix {key_prefix}: {str(e)}")
        return 0

def cache_query_results(query_hash, results, expiry=SHORT_EXPIRY):
    """
    Cache the results of a database query.
    
    Args:
        query_hash (str): A hash that uniquely identifies the query.
        results (list): The query results to cache.
        expiry (int, optional): The cache expiration time in seconds. Defaults to SHORT_EXPIRY.
    
    Returns:
        bool: True if the results were successfully cached, False otherwise.
    """
    return cache_data('query:', query_hash, results, expiry)

def get_cached_query_results(query_hash):
    """
    Retrieve the cached results of a database query.
    
    Args:
        query_hash (str): A hash that uniquely identifies the query.
    
    Returns:
        list: The cached query results or None if not found.
    """
    return get_cached_data('query:', query_hash)

def get_cache_stats():
    """
    Get statistics about the Redis cache.
    
    Returns:
        dict: A dictionary containing cache statistics.
    """
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, cannot get cache statistics")
        return {
            "available": False,
            "error": "Redis connection not available"
        }
    
    try:
        info = redis_client.info()
        db_info = info.get(f"db{REDIS_DB}", {})
        
        # Get key counts by prefix
        tailored_intel_count = len(redis_client.keys(f"{TAILORED_INTEL_PREFIX}*"))
        malware_count = len(redis_client.keys(f"{MALWARE_PREFIX}*"))
        threat_actor_count = len(redis_client.keys(f"{THREAT_ACTOR_PREFIX}*"))
        cisa_kev_count = len(redis_client.keys(f"{CISA_KEV_PREFIX}*"))
        query_count = len(redis_client.keys("query:*"))
        
        return {
            "available": True,
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_days": info.get("uptime_in_days", 0),
            "total_keys": info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0),
            "hit_rate": info.get("keyspace_hits", 0) / (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1) or 1),
            "key_counts": {
                "tailored_intel": tailored_intel_count,
                "malware": malware_count,
                "threat_actor": threat_actor_count,
                "cisa_kev": cisa_kev_count,
                "query": query_count,
                "total": db_info.get("keys", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {str(e)}")
        return {
            "available": True,
            "error": str(e)
        } 