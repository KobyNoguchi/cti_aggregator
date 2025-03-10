// API service for fetching data from the backend

export interface IntelligenceArticle {
  id: number;
  title: string;
  source: string;
  url: string;
  published_date: string;
  summary: string | null;
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
  mitre_techniques: string[];
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

// Base API URL - update this to match your deployment environment
const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Fetch intelligence articles from the backend
 */
export async function fetchIntelligenceArticles(): Promise<IntelligenceArticle[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/intelligence/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching intelligence articles:', error);
    throw error;
  }
}

/**
 * Fetch CrowdStrike malware families from the backend
 */
export async function fetchCrowdStrikeMalware(): Promise<CrowdStrikeMalware[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike/malware/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike malware data:', error);
    throw error;
  }
}

/**
 * Fetch CISA KEV (Known Exploited Vulnerabilities) from the backend
 */
export async function fetchCISAKev(): Promise<CISAKevVulnerability[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/cisa/kev/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CISA KEV data:', error);
    throw error;
  }
}

/**
 * Fetch CrowdStrike threat actors from the backend
 */
export async function fetchCrowdStrikeActors(): Promise<CrowdStrikeActor[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike-intel/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike actor data:', error);
    throw error;
  }
}

/**
 * Fetch CrowdStrike tailored intelligence from the backend
 */
export async function fetchCrowdStrikeTailoredIntel(): Promise<CrowdStrikeTailoredIntel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike/tailored-intel/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike tailored intelligence:', error);
    throw error;
  }
}

/**
 * Fetch CrowdStrike indicators from the backend
 */
export async function fetchCrowdStrikeIndicators(): Promise<CrowdStrikeIndicator[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike/indicators/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike indicators:', error);
    // Return error object instead of mock data
    return [{ 
      id: 'error',
      indicator_value: '404 Not Found',
      indicator_type: 'Error',
      description: 'Could not retrieve indicators from the server',
      malware_families: [],
      threat_groups: [],
      confidence_level: 'N/A',
      severity_level: 'N/A',
      published_date: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      expiration_date: null,
      tags: []
    }];
  }
}

/**
 * Fetch CrowdStrike rules from the backend
 */
export async function fetchCrowdStrikeRules(): Promise<CrowdStrikeRule[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike/rules/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike rules:', error);
    // Return error object instead of mock data
    return [{
      id: 'error',
      name: '404 Not Found',
      description: 'Could not retrieve rules from the server',
      rule_type: 'Error',
      rule_content: 'No content available',
      mitre_techniques: [],
      malware_families: [],
      threat_groups: [],
      confidence_level: 'N/A',
      severity_level: 'N/A',
      published_date: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      tags: []
    }];
  }
}

/**
 * Fetch CrowdStrike vulnerabilities from the backend
 */
export async function fetchCrowdStrikeVulnerabilities(): Promise<CrowdStrikeVulnerability[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/crowdstrike/vulnerabilities/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching CrowdStrike vulnerabilities:', error);
    // Return error object instead of mock data
    return [{
      id: 'error',
      cve_id: '404 Not Found',
      title: 'Could not retrieve vulnerabilities from the server',
      description: 'Service unavailable or error in connection',
      severity_level: 'N/A',
      cvss_score: null,
      affected_products: [],
      exploitation_status: 'Unknown',
      published_date: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      patch_available: false,
      mitigation_steps: null,
      tags: []
    }];
  }
}

/**
 * Refresh intelligence articles by triggering scraping tasks
 */
export async function refreshIntelligence(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/refresh-intelligence/`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Refresh failed with status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error refreshing intelligence:', error);
    throw error;
  }
} 