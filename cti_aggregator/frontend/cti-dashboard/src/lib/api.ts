// API service for fetching data from the backend

export interface IntelligenceArticle {
  id: number;
  title: string;
  source: string;
  url: string;
  published_date: string;
  summary: string | null;
  threat_actor_type: string | null;
  target_industries: string | null;
}

export interface CrowdStrikeMalware {
  malware_id: string;
  name: string;
  description: string | null;
  ttps: string[] | null;
  targeted_industries: string[] | null;
  publish_date: string | null;
  activity_start_date: string | null;
  activity_end_date: string | null;
  threat_groups: string[] | null;
  last_update_date: string | null;
}

export interface CISAKevVulnerability {
  id: string;
  cveID: string;
  vulnerabilityName: string;
  dateAdded: string;
  shortDescription: string;
  vendorProject: string;
  product: string;
  severityLevel: string;
  requiredAction: string;
  dueDate: string | null;
}

export interface CrowdStrikeActor {
  actor_id: string;
  name: string;
  description: string | null;
  capabilities: string[] | null;
  motivations: string[] | null;
  objectives: string[] | null;
  adversary_type: string | null;
  origins: string[] | null;
  last_update_date: string | null;
}

export interface CrowdStrikeTailoredIntel {
  id: string;
  name: string;
  summary: string | null;
  publish_date: string;
  last_updated: string;
  url: string | null;
  threat_groups: string[];
  targeted_sectors: string[];
  // New fields
  source?: string;
  hit_type?: string;
  matched_rule_names?: string[];
  details?: string;
  first_seen?: string;
  // Frontend-only fields
  title?: string;
  report_type?: string;
  target_sectors?: string[];
  target_countries?: string[];
  malware_families?: string[];
  tags?: string[];
  published_date?: string;
  confidence_level?: string;
  severity_level?: string;
  report_url?: string | null;
}

export interface CrowdStrikeIndicator {
  id: string;
  indicator_value: string;
  indicator_type: string;
  description: string | null;
  malware_families: string[];
  threat_groups: string[];
  confidence_level: string;
  severity_level: string;
  published_date: string;
  last_updated: string;
  expiration_date: string | null;
  tags: string[];
}

export interface CrowdStrikeRule {
  id: string;
  name: string;
  description: string | null;
  rule_type: string;
  rule_content: string;
  malware_families: string[];
  threat_groups: string[];
  confidence_level: string;
  severity_level: string;
  published_date: string;
  last_updated: string;
  tags: string[];
}

export interface CrowdStrikeVulnerability {
  id: string;
  cve_id: string;
  title: string;
  description: string | null;
  severity_level: string;
  cvss_score: number | null;
  affected_products: string[];
  exploitation_status: string;
  published_date: string;
  last_updated: string;
  patch_available: boolean;
  mitigation_steps: string | null;
  tags: string[];
}

// Base API URL - was hardcoded, now use environment variable with fallback
const API_BASE_URL = 
  typeof window !== 'undefined' && process.env.NEXT_PUBLIC_API_URL 
    ? process.env.NEXT_PUBLIC_API_URL 
    : 'http://localhost:8000/api';

// Cache configuration
interface CacheConfig {
  enabled: boolean;
  defaultTTL: number; // Time to live in milliseconds
}

interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

// Cache configuration - can be customized based on environment
const cacheConfig: CacheConfig = {
  enabled: typeof window !== 'undefined', // Only enable cache in browser environment
  defaultTTL: 5 * 60 * 1000, // 5 minutes default cache TTL
};

// Cache namespace to prevent collisions with other localStorage items
const CACHE_NAMESPACE = 'cti_aggr_cache:';

/**
 * Check if browser storage is available
 */
function isStorageAvailable(): boolean {
  if (typeof window === 'undefined') {
    return false; // Not in browser environment
  }
  
  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, testKey);
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Get data from cache, optionally ignoring expiration
 */
function getFromCache<T>(key: string, ignoreExpiry: boolean = false): T | null {
  if (!cacheConfig.enabled || !isStorageAvailable()) {
    return null;
  }
  
  try {
    const cachedItem = localStorage.getItem(CACHE_NAMESPACE + key);
    if (!cachedItem) return null;
    
    const item: CacheItem<T> = JSON.parse(cachedItem);
    
    if (!ignoreExpiry) {
      const now = Date.now();
      
      // Check if cache has expired
      if (now > item.expiry) {
        return null;
      }
    }
    
    return item.data;
  } catch (error) {
    console.error('Error reading from cache:', error);
    return null;
  }
}

/**
 * Save data to cache
 */
function saveToCache<T>(key: string, data: T, ttl: number = cacheConfig.defaultTTL): void {
  if (!cacheConfig.enabled || !isStorageAvailable()) {
    return;
  }
  
  try {
    const now = Date.now();
    const item: CacheItem<T> = {
      data,
      timestamp: now,
      expiry: now + ttl
    };
    
    localStorage.setItem(CACHE_NAMESPACE + key, JSON.stringify(item));
  } catch (error) {
    console.error('Error saving to cache:', error);
  }
}

/**
 * Clear all cached data
 */
export function clearCache(): void {
  if (!isStorageAvailable()) return;
  
  try {
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(CACHE_NAMESPACE)) {
        localStorage.removeItem(key);
      }
    });
  } catch (error) {
    console.error('Error clearing cache:', error);
  }
}

// Generic error response type
export interface ApiErrorResponse {
  isError: true;
  status: number;
  message: string;
  timestamp: string;
}

// Generic function to create error responses
function createErrorResponse(status: number, message: string): ApiErrorResponse {
  return {
    isError: true,
    status,
    message,
    timestamp: new Date().toISOString()
  };
}

// Type guard to check if a response is an error
export function isErrorResponse<T>(response: T[] | ApiErrorResponse): response is ApiErrorResponse {
  return (response as ApiErrorResponse).isError === true;
}

// Add a function to check if the API is reachable
async function isApiReachable(): Promise<boolean> {
  if (typeof window === 'undefined') {
    return false;
  }
  
  try {
    // Use a simple HEAD request to check if the API is reachable
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
    
    const response = await fetch(`${API_BASE_URL}/health-check/`, {
      method: 'HEAD',
      signal: controller.signal,
    }).catch(() => null);
    
    clearTimeout(timeoutId);
    return !!response && response.ok;
  } catch (error) {
    console.error('API reachability check failed:', error);
    return false;
  }
}

// Cache for API reachability status to avoid multiple checks
let apiReachableCache: { status: boolean; timestamp: number } | null = null;

// Generic fetch function with consistent error handling and caching
async function fetchFromApi<T>(
  endpoint: string, 
  errorMessage: string = "Could not retrieve data from the server",
  cacheTTL: number | null = cacheConfig.defaultTTL
): Promise<T[] | ApiErrorResponse> {
  // Generate a cache key based on the endpoint
  const cacheKey = endpoint.replace(/[^a-zA-Z0-9]/g, '_');
  
  // Skip cache if we're in a server environment
  const shouldUseCache = typeof window !== 'undefined' && cacheTTL !== null;
  
  // Try to get from cache first if caching is enabled and we're in browser
  if (shouldUseCache) {
    const cachedData = getFromCache<T[]>(cacheKey);
    if (cachedData) {
      console.log(`Using cached data for ${endpoint}`);
      return cachedData;
    }
  }
  
  // Handle SSR - return empty array during server rendering to avoid hydration mismatch
  if (typeof window === 'undefined') {
    console.log(`Skipping API fetch during SSR for ${endpoint}`);
    return [] as T[];
  }
  
  // Check if API is reachable (only check once every 30 seconds)
  const now = Date.now();
  if (!apiReachableCache || now - apiReachableCache.timestamp > 30000) {
    apiReachableCache = {
      status: await isApiReachable(),
      timestamp: now
    };
  }
  
  // If API is known to be unreachable, return cached data if available or an error
  if (!apiReachableCache.status) {
    // Try to get stale data from cache as fallback
    const staleData = getFromCache<T[]>(cacheKey, true);
    if (staleData) {
      console.log(`API unreachable, using stale cached data for ${endpoint}`);
      return staleData;
    }
    
    return createErrorResponse(
      503,
      "API server is currently unreachable. Please check your network connection and try again later."
    );
  }
  
  // If not in cache or caching disabled, fetch from API
  try {
    // Set timeout for fetch requests
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      // If we got a 404, check if we have stale data in cache
      if (response.status === 404 && shouldUseCache) {
        const staleData = getFromCache<T[]>(cacheKey, true);
        if (staleData) {
          console.log(`Endpoint not found, using stale cached data for ${endpoint}`);
          return staleData;
        }
      }
      
      return createErrorResponse(
        response.status,
        `${errorMessage} (${response.status}: ${response.statusText})`
      );
    }
    
    const data = await response.json();
    
    // Validate data is an array before proceeding
    if (!Array.isArray(data)) {
      console.error(`Expected array but got:`, data);
      
      // Try to get stale data from cache as fallback
      if (shouldUseCache) {
        const staleData = getFromCache<T[]>(cacheKey, true);
        if (staleData) {
          console.log(`Invalid data format, using stale cached data for ${endpoint}`);
          return staleData;
        }
      }
      
      return createErrorResponse(
        500,
        `${errorMessage}: Invalid data format received from server`
      );
    }
    
    // Save successful response to cache if caching is enabled
    if (shouldUseCache && Array.isArray(data)) {
      saveToCache(cacheKey, data, cacheTTL);
    }
    
    return data;
  } catch (error) {
    console.error(`Error fetching from ${endpoint}:`, error);
    
    // Handle AbortError specifically for timeouts
    if (error instanceof DOMException && error.name === 'AbortError') {
      return createErrorResponse(
        408,
        `Request timed out: The server took too long to respond. Please try again later.`
      );
    }
    
    // Try to get stale data from cache as fallback
    if (shouldUseCache) {
      const staleData = getFromCache<T[]>(cacheKey, true);
      if (staleData) {
        console.log(`Error in fetch, using stale cached data for ${endpoint}`);
        return staleData;
      }
    }
    
    // Provide more specific error messages based on error type
    let errorMsg = `${errorMessage}: `;
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      errorMsg += 'Network error - Please check your internet connection or if the server is running.';
    } else {
      errorMsg += error instanceof Error ? error.message : 'Unknown error';
    }
    
    return createErrorResponse(
      500,
      errorMsg
    );
  }
}

/**
 * Fetch intelligence articles from the backend
 */
export async function fetchIntelligenceArticles(skipCache: boolean = false): Promise<IntelligenceArticle[] | ApiErrorResponse> {
  return fetchFromApi<IntelligenceArticle>(
    '/intelligence/', 
    'Could not retrieve intelligence articles',
    skipCache ? null : undefined
  );
}

/**
 * Fetch CrowdStrike malware families from the backend
 */
export async function fetchCrowdStrikeMalware(skipCache: boolean = false): Promise<CrowdStrikeMalware[] | ApiErrorResponse> {
  return fetchFromApi<CrowdStrikeMalware>(
    '/crowdstrike/malware/', 
    'Could not retrieve malware families',
    skipCache ? null : undefined
  );
}

/**
 * Fetch CISA KEV (Known Exploited Vulnerabilities) from the backend
 */
export async function fetchCISAKev(skipCache: boolean = false): Promise<CISAKevVulnerability[] | ApiErrorResponse> {
  return fetchFromApi<CISAKevVulnerability>(
    '/cisa/kev/', 
    'Could not retrieve CISA KEV data',
    skipCache ? null : undefined
  );
}

/**
 * Fetch CrowdStrike threat actors from the backend
 */
export async function fetchCrowdStrikeActors(skipCache: boolean = false): Promise<CrowdStrikeActor[] | ApiErrorResponse> {
  return fetchFromApi<CrowdStrikeActor>(
    '/crowdstrike-intel/', 
    'Could not retrieve threat actors',
    skipCache ? null : undefined
  );
}

/**
 * Fetch CrowdStrike tailored intelligence from the backend
 */
export async function fetchCrowdStrikeTailoredIntel(skipCache: boolean = false): Promise<CrowdStrikeTailoredIntel[] | ApiErrorResponse> {
  return fetchFromApi<CrowdStrikeTailoredIntel>(
    '/crowdstrike/tailored-intel/', 
    'Could not retrieve tailored intelligence',
    skipCache ? null : undefined
  );
}

/**
 * Refresh intelligence articles by triggering scraping tasks
 */
export async function refreshIntelligence(): Promise<{success: boolean, message: string}> {
  try {
    const response = await fetch(`${API_BASE_URL}/refresh-intelligence/`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      return {
        success: false,
        message: `Refresh failed with status: ${response.status}`
      };
    }
    
    return {
      success: true,
      message: 'Intelligence refreshed successfully'
    };
  } catch (error) {
    console.error('Error refreshing intelligence:', error);
    return {
      success: false,
      message: `Error refreshing intelligence: ${error instanceof Error ? error.message : 'Unknown error'}`
    };
  }
}