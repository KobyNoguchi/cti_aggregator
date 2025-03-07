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
  title: string;
  summary: string | null;
  report_type: string;
  target_sectors: string[];
  target_countries: string[];
  threat_groups: string[];
  malware_families: string[];
  tags: string[];
  published_date: string;
  last_updated: string;
  confidence_level: string;
  severity_level: string;
  report_url: string | null;
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
    // Return mock data for now
    return generateMockIndicators(15);
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
    // Return mock data for now
    return generateMockRules(15);
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
    // Return mock data for now
    return generateMockVulnerabilities(15);
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

// Helper functions to generate mock data for endpoints that might not be implemented yet
function generateMockIndicators(count: number): CrowdStrikeIndicator[] {
  const types = ['IP', 'Domain', 'URL', 'File Hash', 'Email'];
  const malwareFamilies = ['SUNBURST', 'TEARDROP', 'BEACON', 'MIMIKATZ', 'COBALTSTRIKE'];
  const threatGroups = ['APT29', 'APT28', 'CARBON SPIDER', 'WIZARD SPIDER', 'FANCY BEAR'];
  const confidenceLevels = ['High', 'Medium', 'Low'];
  const severityLevels = ['Critical', 'High', 'Medium', 'Low'];
  
  return Array.from({ length: count }, (_, i) => ({
    id: `indicator-${i + 1}`,
    indicator_value: types[i % types.length] === 'IP' 
      ? `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
      : types[i % types.length] === 'Domain'
        ? `malicious-domain-${i}.com`
        : types[i % types.length] === 'URL'
          ? `https://malicious-site-${i}.com/path/to/resource`
          : types[i % types.length] === 'File Hash'
            ? `a1b2c3d4e5f6${i}7890abcdef1234567890abcdef`
            : `malicious-email-${i}@evil.com`,
    indicator_type: types[i % types.length],
    description: `This is a malicious ${types[i % types.length].toLowerCase()} associated with recent threat activity.`,
    malware_families: [malwareFamilies[i % malwareFamilies.length]],
    threat_groups: [threatGroups[i % threatGroups.length]],
    confidence_level: confidenceLevels[i % confidenceLevels.length],
    severity_level: severityLevels[i % severityLevels.length],
    published_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    last_updated: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
    expiration_date: Math.random() > 0.3 
      ? new Date(Date.now() + Math.floor(Math.random() * 90) * 24 * 60 * 60 * 1000).toISOString()
      : null,
    tags: [`tag-${i % 5}`, `category-${Math.floor(i / 3)}`]
  }));
}

function generateMockRules(count: number): CrowdStrikeRule[] {
  const ruleTypes = ['YARA', 'Sigma', 'Snort', 'STIX', 'Custom'];
  const mitreTechniques = ['T1566', 'T1190', 'T1059', 'T1027', 'T1486'];
  const malwareFamilies = ['SUNBURST', 'TEARDROP', 'BEACON', 'MIMIKATZ', 'COBALTSTRIKE'];
  const threatGroups = ['APT29', 'APT28', 'CARBON SPIDER', 'WIZARD SPIDER', 'FANCY BEAR'];
  const confidenceLevels = ['High', 'Medium', 'Low'];
  const severityLevels = ['Critical', 'High', 'Medium', 'Low'];
  
  return Array.from({ length: count }, (_, i) => ({
    id: `rule-${i + 1}`,
    name: `Detection Rule ${i + 1}`,
    description: `This rule detects ${malwareFamilies[i % malwareFamilies.length]} activity associated with ${threatGroups[i % threatGroups.length]}.`,
    rule_type: ruleTypes[i % ruleTypes.length],
    rule_content: `rule Malicious_Activity_${i} {\n    meta:\n        description = "Detects malicious activity"\n    strings:\n        $a = "malicious string"\n    condition:\n        $a\n}`,
    mitre_techniques: [mitreTechniques[i % mitreTechniques.length]],
    malware_families: [malwareFamilies[i % malwareFamilies.length]],
    threat_groups: [threatGroups[i % threatGroups.length]],
    confidence_level: confidenceLevels[i % confidenceLevels.length],
    severity_level: severityLevels[i % severityLevels.length],
    published_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    last_updated: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
    tags: [`tag-${i % 5}`, `category-${Math.floor(i / 3)}`]
  }));
}

function generateMockVulnerabilities(count: number): CrowdStrikeVulnerability[] {
  const products = ['Windows', 'Office', 'Exchange', 'Chrome', 'Firefox', 'Adobe Reader', 'Java'];
  const exploitationStatuses = ['Exploited in the Wild', 'Proof of Concept Available', 'No Known Exploitation', 'Under Analysis'];
  const severityLevels = ['Critical', 'High', 'Medium', 'Low'];
  
  return Array.from({ length: count }, (_, i) => ({
    id: `vuln-${i + 1}`,
    cve_id: `CVE-${2023 - Math.floor(i / 5)}-${10000 + i}`,
    title: `Vulnerability in ${products[i % products.length]} allows remote code execution`,
    description: `A vulnerability in ${products[i % products.length]} could allow an attacker to execute arbitrary code on the affected system.`,
    severity_level: severityLevels[i % severityLevels.length],
    cvss_score: Math.floor(Math.random() * 10) + (severityLevels[i % severityLevels.length] === 'Critical' ? 9 : 
                                                 severityLevels[i % severityLevels.length] === 'High' ? 7 : 
                                                 severityLevels[i % severityLevels.length] === 'Medium' ? 4 : 1),
    affected_products: [products[i % products.length]],
    exploitation_status: exploitationStatuses[i % exploitationStatuses.length],
    published_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    last_updated: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
    patch_available: Math.random() > 0.3,
    mitigation_steps: Math.random() > 0.3 ? `Apply the latest security updates for ${products[i % products.length]}.` : null,
    tags: [`tag-${i % 5}`, `category-${Math.floor(i / 3)}`]
  }));
} 