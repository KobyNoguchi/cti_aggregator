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