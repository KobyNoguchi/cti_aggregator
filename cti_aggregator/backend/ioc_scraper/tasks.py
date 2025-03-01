import requests
from .models import Vulnerability, IntelligenceArticle
from celery import shared_task
from datetime import datetime 
from bs4 import BeautifulSoup
import logging
from django.utils import timezone
from ioc_scraper.models import CrowdStrikeIntel
import sys
import os

# Add the parent directory to sys.path to allow importing from data_sources
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from data_sources.crowdstrike import falcon, fetch_threat_actors, get_actor_details

# Add the data_sources directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_sources'))

# Import crowdstrike module with improved functions
from crowdstrike import fetch_threat_actors, get_actor_details

logger = logging.getLogger(__name__)

def fetch_cisa_vulnerabilities():
    """Fetches CISA KEV vulnerabilities and updates the database."""
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    response = requests.get(url)

    if response.status_code !=200:
        print(f" Error: Unable to fetch data (Status Code {response.status_code})")
        return "failed to fetch CISA KEV data"

    data = response.json().get("vulnerabilities", [])


    for vuln in data:
        cve_id = vuln.get("cveID")
        published_date = vuln.get("dateAdded", "1970-01-01") #Ensure no missing dates
        published_date = datetime.strptime(published_date, "%Y-%m-%d").date() 

        print(f" Process {cve_id} - Published: {published_date}")

        Vulnerability.objects.update_or_create(
            cve_id=cve_id,
            defaults={
                "vulnerability_name": vuln.get("vulnerabilityName", "Unknown"),
                "description": vuln.get("shortDescription", "No description provided"),
                "severity": vuln.get("serverity", "Unknown"),
                "published_date": published_date,
                "source_url": vuln.get("url", "Unknown"),
            }
        )

    print(f" Updated {len(data)} vulnerabilities from CISA KEV")
    return (f"Updated {len(data)} vulnerabilities from CISA KEV")

@shared_task
def fetch_all_intelligence():
    """Fetch intelligence articles from all sources"""
    results = []
    results.append(fetch_cisco_talos_intelligence())
    results.append(fetch_microsoft_intelligence())
    results.append(fetch_mandiant_intelligence())
    return f"Completed fetching intelligence from all sources: {', '.join(results)}"

@shared_task
def fetch_cisco_talos_intelligence():
    """Fetch intelligence articles from Cisco Talos"""
    url = "https://blog.talosintelligence.com/"
    source_name = "Cisco Talos"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.post')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h2.post-title a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            
            # Extract date
            date_elem = article.select_one('time.published')
            if date_elem and date_elem.get('datetime'):
                published_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.entry-content')
            summary = summary_elem.text.strip() if summary_elem else ""
            
            # Update or create article
            IntelligenceArticle.objects.update_or_create(
                url=article_url,
                defaults={
                    'title': title,
                    'source': source_name,
                    'published_date': published_date,
                    'summary': summary[:500] + ('...' if len(summary) > 500 else '')
                }
            )
            count += 1
        
        logger.info(f"Updated {count} {source_name} intelligence articles")
        return f"Updated {count} {source_name} intelligence articles"
    except Exception as e:
        logger.error(f"Error fetching {source_name} data: {str(e)}")
        return f"Error fetching {source_name} data: {str(e)}"

@shared_task
def fetch_microsoft_intelligence():
    """Fetch intelligence articles from Microsoft Security Blog"""
    url = "https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/"
    source_name = "Microsoft Security"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.post')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h2 a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.microsoft.com' + article_url
            
            # Extract date
            date_elem = article.select_one('time.c-timestamp')
            if date_elem:
                date_text = date_elem.text.strip()
                try:
                    published_date = datetime.strptime(date_text, '%B %d, %Y')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.entry-summary')
            summary = summary_elem.text.strip() if summary_elem else ""
            
            # Update or create article
            IntelligenceArticle.objects.update_or_create(
                url=article_url,
                defaults={
                    'title': title,
                    'source': source_name,
                    'published_date': published_date,
                    'summary': summary[:500] + ('...' if len(summary) > 500 else '')
                }
            )
            count += 1
        
        logger.info(f"Updated {count} {source_name} intelligence articles")
        return f"Updated {count} {source_name} intelligence articles"
    except Exception as e:
        logger.error(f"Error fetching {source_name} data: {str(e)}")
        return f"Error fetching {source_name} data: {str(e)}"

@shared_task
def fetch_mandiant_intelligence():
    """Fetch intelligence articles from Mandiant"""
    url = "https://www.mandiant.com/resources/blog"
    source_name = "Mandiant"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.blog-card')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('.blog-card__title a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.mandiant.com' + article_url
            
            # Extract date
            date_elem = article.select_one('.blog-card__date')
            if date_elem:
                date_text = date_elem.text.strip()
                try:
                    published_date = datetime.strptime(date_text, '%B %d, %Y')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.blog-card__description')
            summary = summary_elem.text.strip() if summary_elem else ""
            
            # Update or create article
            IntelligenceArticle.objects.update_or_create(
                url=article_url,
                defaults={
                    'title': title,
                    'source': source_name,
                    'published_date': published_date,
                    'summary': summary[:500] + ('...' if len(summary) > 500 else '')
                }
            )
            count += 1
        
        logger.info(f"Updated {count} {source_name} intelligence articles")
        return f"Updated {count} {source_name} intelligence articles"
    except Exception as e:
        logger.error(f"Error fetching {source_name} data: {str(e)}")
        return f"Error fetching {source_name} data: {str(e)}"

@shared_task
def fetch_crowdstrike_intel():
    """
    Fetch intelligence from CrowdStrike Intel Feed.
    """
    logger.info("Fetching CrowdStrike Intel...")
    
    try:
        # Get threat actors from CrowdStrike API
        actors_data = fetch_threat_actors()
        
        if not actors_data:
            logger.warning("No threat actors data received from CrowdStrike API.")
            return "No threat actors data received"
            
        # Process actor data directly from the response
        processed_actors = get_actor_details(actors_data)
        
        if not processed_actors:
            logger.warning("Failed to process actor details from CrowdStrike API.")
            return "Failed to process actor details"
            
        actor_count = 0
        
        # Process each actor
        for actor in processed_actors:
            try:
                # Create or update actor in the database
                actor_obj, created = CrowdStrikeIntel.objects.update_or_create(
                    actor_id=actor.get('id'),
                    defaults={
                        'name': actor.get('name', 'Unknown'),
                        'description': actor.get('description', ''),
                        'adversary_type': actor.get('adversary_type', 'unknown'),
                        'origins': actor.get('origins', []),
                        'capabilities': actor.get('capabilities', []),
                        'motivations': actor.get('motivations', []),
                        'objectives': actor.get('objectives', []),
                        'last_update_date': actor.get('last_modified_date')
                    }
                )
                
                if created:
                    logger.info(f"Created new threat actor: {actor.get('name')}")
                else:
                    logger.info(f"Updated existing threat actor: {actor.get('name')}")
                    
                actor_count += 1
                
            except Exception as e:
                logger.error(f"Error saving actor {actor.get('name', 'Unknown')}: {str(e)}")
                
        return f"Successfully processed {actor_count} threat actors from CrowdStrike"
        
    except Exception as e:
        logger.error(f"Error fetching CrowdStrike intel: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def create_sample_crowdstrike_data():
    """Create sample CrowdStrike data for testing."""
    logger.info("Creating sample CrowdStrike data...")
    
    # Sample threat actors
    sample_actors = [
        {
            "actor_id": "1001",
            "name": "FANCY BEAR",
            "description": "FANCY BEAR is a Russian cyber espionage group that has been active since at least 2004. The group primarily targets government, military, and security organizations.",
            "adversary_type": "nation-state",
            "origins": ["Russia", "Eastern Europe"],
            "capabilities": ["Spear Phishing", "Zero-day Exploits", "Malware Development", "Social Engineering"],
            "motivations": ["State-Sponsored", "Political"],
            "objectives": ["Intelligence Gathering", "Data Theft", "Disruption"],
            "last_update_date": "2024-04-15T00:00:00Z"
        },
        {
            "actor_id": "1002",
            "name": "COZY BEAR",
            "description": "COZY BEAR is a Russian threat group that targets various organizations for intelligence collection purposes. They use sophisticated techniques to maintain stealth and persistence.",
            "adversary_type": "nation-state",
            "origins": ["Russia", "Eastern Europe"],
            "capabilities": ["Supply Chain Attacks", "Living-off-the-land", "Custom Malware", "Advanced Persistence"],
            "motivations": ["State-Sponsored", "Political"],
            "objectives": ["Intelligence Gathering", "Strategic Compromise"],
            "last_update_date": "2024-04-10T00:00:00Z"
        },
        {
            "actor_id": "1003",
            "name": "LAZARUS GROUP",
            "description": "LAZARUS GROUP is a North Korean state-sponsored cyber threat group with a history of disruptive and destructive cyber attacks. They are known for operations targeting financial institutions and cryptocurrency exchanges.",
            "adversary_type": "nation-state",
            "origins": ["North Korea", "East Asia"],
            "capabilities": ["Watering Hole Attacks", "Bitcoin Theft", "Destructive Malware", "APT Tactics"],
            "motivations": ["State-Sponsored", "Financial Gain"],
            "objectives": ["Currency Generation", "Sanctions Evasion", "Intelligence Collection"],
            "last_update_date": "2024-03-22T00:00:00Z"
        },
        {
            "actor_id": "1004",
            "name": "MUSTANG PANDA",
            "description": "MUSTANG PANDA is a China-based threat actor targeting governmental and non-governmental organizations across Asia, with a focus on Mongolia, Vietnam, Myanmar, and the Philippines.",
            "adversary_type": "nation-state",
            "origins": ["China", "East Asia"],
            "capabilities": ["Custom Loaders", "Targeted Phishing", "PlugX Malware"],
            "motivations": ["State-Sponsored", "Political"],
            "objectives": ["Intelligence Gathering", "Surveillance"],
            "last_update_date": "2024-02-18T00:00:00Z"
        },
        {
            "actor_id": "1005",
            "name": "WIZARD SPIDER",
            "description": "WIZARD SPIDER is a Russia-based criminal group focused on deploying ransomware for monetary gain. The group is known for developing and deploying the TrickBot banking malware and Ryuk ransomware.",
            "adversary_type": "criminal",
            "origins": ["Russia", "Eastern Europe"],
            "capabilities": ["Ransomware Deployment", "Banking Trojans", "Data Exfiltration"],
            "motivations": ["Financial Gain", "Criminal"],
            "objectives": ["Ransom Payments", "Data Theft"],
            "last_update_date": "2024-04-01T00:00:00Z"
        },
        {
            "actor_id": "1006",
            "name": "CARBON SPIDER",
            "description": "CARBON SPIDER is a financially motivated criminal group targeting the hospitality, entertainment, and retail sectors. They specialize in point-of-sale (POS) intrusions for credit card theft.",
            "adversary_type": "criminal",
            "origins": ["Eastern Europe"],
            "capabilities": ["Point-of-Sale Malware", "Supply Chain Attacks", "Social Engineering"],
            "motivations": ["Financial Gain", "Criminal"],
            "objectives": ["Credit Card Theft", "Fraud"],
            "last_update_date": "2024-03-15T00:00:00Z"
        },
        {
            "actor_id": "1007",
            "name": "MUDDY WATER",
            "description": "MUDDY WATER is a threat group that conducts targeted cyber espionage operations against Middle Eastern nations and various industry verticals, including telecommunications, government, and defense.",
            "adversary_type": "nation-state",
            "origins": ["Iran", "Middle East"],
            "capabilities": ["Custom PowerShell Scripts", "Obfuscation", "Spear Phishing"],
            "motivations": ["State-Sponsored", "Political"],
            "objectives": ["Intelligence Gathering", "Data Theft"],
            "last_update_date": "2024-03-05T00:00:00Z"
        },
        {
            "actor_id": "1008",
            "name": "HOSTILE CHOLLIMA",
            "description": "HOSTILE CHOLLIMA is a North Korean financially-motivated threat group focusing on cryptocurrency theft and financial fraud to generate revenue for the regime.",
            "adversary_type": "nation-state",
            "origins": ["North Korea", "East Asia"],
            "capabilities": ["Cryptocurrency Theft", "Banking Malware", "Social Engineering"],
            "motivations": ["State-Sponsored", "Financial Gain"],
            "objectives": ["Currency Generation", "Sanctions Evasion"],
            "last_update_date": "2024-02-28T00:00:00Z"
        }
    ]
    
    # Create/update actors in the database
    created_count = 0
    for actor_data in sample_actors:
        actor, created = CrowdStrikeIntel.objects.update_or_create(
            actor_id=actor_data['actor_id'],
            defaults={
                'name': actor_data['name'],
                'description': actor_data['description'],
                'adversary_type': actor_data['adversary_type'],
                'origins': actor_data['origins'],
                'capabilities': actor_data['capabilities'],
                'motivations': actor_data['motivations'],
                'objectives': actor_data['objectives'],
                'last_update_date': actor_data['last_update_date']
            }
        )
        if created:
            created_count += 1
            
    logger.info(f"Created {created_count} sample threat actors")
    return f"Created {created_count} sample threat actors"
