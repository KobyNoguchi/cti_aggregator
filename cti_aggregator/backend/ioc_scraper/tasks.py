import requests
from .models import Vulnerability, IntelligenceArticle
from celery import shared_task, group
from datetime import datetime 
from bs4 import BeautifulSoup
import logging
from django.utils import timezone
from ioc_scraper.models import CrowdStrikeIntel, CrowdStrikeMalware
import sys
import os

# Add the parent directory to sys.path to allow importing from data_sources
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from data_sources.crowdstrike import falcon, fetch_threat_actors, get_actor_details

# Add the data_sources directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_sources'))

# Import crowdstrike module with improved functions
from crowdstrike import fetch_threat_actors, get_actor_details

# Try to import the enhanced scraper (free version)
try:
    from data_sources.free_enhanced_scraper import FreeEnhancedScraper, scrape_intelligence_articles, is_free_proxy_configured
    ENHANCED_SCRAPER_AVAILABLE = True
except ImportError:
    ENHANCED_SCRAPER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Enhanced scraper not available. Some scrapers will use fallback methods.")
else:
    logger = logging.getLogger(__name__)

@shared_task
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
    """Fetch intelligence articles from all sources in parallel"""
    # Create a list of task signatures to execute in parallel
    scraper_tasks = [
        fetch_cisco_talos_intelligence.s(),
        fetch_microsoft_intelligence.s(),
        fetch_mandiant_intelligence.s(),
        fetch_unit42_intelligence.s(),
        fetch_zscaler_intelligence.s(),
        fetch_orange_defense_intelligence.s(),
        fetch_mitre_intelligence.s(),
        fetch_google_tag_intelligence.s(),
    ]
    
    # Add the appropriate dark reading scraper based on availability
    if ENHANCED_SCRAPER_AVAILABLE:
        scraper_tasks.append(fetch_dark_reading_enhanced.s())
    else:
        scraper_tasks.append(fetch_dark_reading_intelligence.s())
    
    # Execute all scraper tasks in parallel using Celery's group functionality
    job = group(scraper_tasks)
    result = job.apply_async()
    
    # Wait for all tasks to complete and get their results
    task_results = result.get()
    
    return f"Completed fetching intelligence from all sources in parallel: {', '.join(task_results)}"

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
def update_tailored_intelligence():
    """
    Celery task to update CrowdStrike Tailored Intelligence data.
    This task runs the tailored_intelligence.py update function.
    """
    logger.info("Starting scheduled update of CrowdStrike Tailored Intelligence data")
    
    try:
        # Add the data_sources directory to the Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        data_sources_dir = os.path.join(project_root, 'data_sources')
        if data_sources_dir not in sys.path:
            sys.path.insert(0, data_sources_dir)
        
        # Import and run the update function
        from data_sources.tailored_intelligence import run_update
        result = run_update()
        
        logger.info(f"Completed scheduled update of Tailored Intelligence data: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in scheduled update of Tailored Intelligence data: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task
def fetch_unit42_intelligence():
    """Fetch intelligence articles from Palo Alto Unit42"""
    url = "https://unit42.paloaltonetworks.com/"
    source_name = "Unit42"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"Unit42 fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.entry')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h2.entry-title a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            
            # Extract date
            date_elem = article.select_one('time.entry-date')
            if date_elem and date_elem.get('datetime'):
                published_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.entry-content, .entry-summary')
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
def fetch_zscaler_intelligence():
    """Fetch intelligence articles from ZScaler Security Research Blog"""
    url = "https://www.zscaler.com/blogs/security-research"
    source_name = "ZScaler Security"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"ZScaler fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.view-content .views-row')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h3 a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.zscaler.com' + article_url
            
            # Extract date
            date_elem = article.select_one('.views-field-created-1')
            if date_elem:
                date_text = date_elem.text.strip()
                try:
                    published_date = datetime.strptime(date_text, '%B %d, %Y')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.views-field-body')
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
def fetch_orange_defense_intelligence():
    """Fetch intelligence articles from Orange Cyber Defense Blog"""
    url = "https://orangecyberdefense.com/global/blog/"
    source_name = "Orange Cyber Defense"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"Orange Cyber Defense fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.et_pb_post')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h2.entry-title a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            
            # Extract date
            date_elem = article.select_one('.published')
            if date_elem:
                date_text = date_elem.text.strip()
                try:
                    published_date = datetime.strptime(date_text, '%B %d, %Y')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.post-content')
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
def fetch_mitre_intelligence():
    """Fetch intelligence articles from MITRE ATT&CK Updates"""
    url = "https://attack.mitre.org/resources/updates/"
    source_name = "MITRE ATT&CK"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"MITRE fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.card')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('.card-title')
            if not title_elem:
                continue
            
            # Extract the link
            link_elem = article.select_one('a')
            if not link_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = link_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://attack.mitre.org' + article_url
            
            # Extract date - MITRE updates often have dates in the title or card body
            date_elem = article.select_one('.card-text')
            published_date = datetime.now()
            if date_elem:
                # Try to find a date pattern in the text
                text = date_elem.text.strip()
                import re
                date_match = re.search(r'(\w+ \d{1,2}, \d{4})', text)
                if date_match:
                    try:
                        published_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
                    except ValueError:
                        pass
            
            # Extract summary
            summary = date_elem.text.strip() if date_elem else ""
            
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
def fetch_dark_reading_intelligence():
    """Fetch intelligence articles from Dark Reading"""
    url = "https://www.darkreading.com/threat-intelligence"
    source_name = "Dark Reading"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"Dark Reading fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.article-info')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h3 a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.darkreading.com' + article_url
            
            # Extract date
            date_elem = article.select_one('.timestamp')
            if date_elem:
                date_text = date_elem.text.strip()
                try:
                    published_date = datetime.strptime(date_text, '%b %d, %Y')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.deck')
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
def fetch_google_tag_intelligence():
    """Fetch intelligence articles from Google Threat Analysis Group"""
    url = "https://blog.google/threat-analysis-group/"
    source_name = "Google TAG"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        logger.info(f"Google TAG fetch status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {source_name} data: {response.status_code}")
            return f"Failed to fetch {source_name} data: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.blog-c-entry')
        
        count = 0
        for article in articles:
            title_elem = article.select_one('h2.blog-c-entry__title a')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            article_url = title_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://blog.google' + article_url
            
            # Extract date
            date_elem = article.select_one('time')
            if date_elem and date_elem.get('datetime'):
                try:
                    published_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Extract summary
            summary_elem = article.select_one('.blog-c-entry__snippet')
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
def fetch_dark_reading_enhanced():
    """Fetch intelligence articles from Dark Reading using the free enhanced scraper"""
    source_name = "Dark Reading"
    url = "https://www.darkreading.com/threat-intelligence"
    
    if not ENHANCED_SCRAPER_AVAILABLE:
        logger.warning(f"Enhanced scraper not available for {source_name}, falling back to standard scraper")
        return fetch_dark_reading_intelligence()
    
    try:
        logger.info(f"Fetching {source_name} intelligence using free enhanced scraper")
        logger.info(f"Free proxy system configured: {is_free_proxy_configured()}")
        
        # Use the free enhanced scraper
        try:
            articles = scrape_intelligence_articles(
                url=url,
                source_name=source_name,
                article_selector=".article-info",
                title_selector="h3 a",
                date_selector=".timestamp",
                date_format="%b %d, %Y",
                summary_selector=".deck",
                url_prefix="https://www.darkreading.com",
                use_proxies=True,
                max_retries=4
            )
            
            if not articles:
                logger.warning(f"No articles found with proxies, trying direct connection")
                # If proxies fail, try direct connection
                articles = scrape_intelligence_articles(
                    url=url,
                    source_name=source_name,
                    article_selector=".article-info",
                    title_selector="h3 a",
                    date_selector=".timestamp",
                    date_format="%b %d, %Y",
                    summary_selector=".deck",
                    url_prefix="https://www.darkreading.com",
                    use_proxies=False,
                    max_retries=3
                )
        except Exception as e:
            logger.error(f"Error during enhanced scraping: {str(e)}")
            logger.info("Falling back to standard scraper")
            return fetch_dark_reading_intelligence()
        
        if not articles:
            logger.warning(f"No articles found with enhanced scraper, falling back to standard scraper")
            return fetch_dark_reading_intelligence()
        
        # Update or create articles in the database
        count = 0
        for article in articles:
            try:
                IntelligenceArticle.objects.update_or_create(
                    url=article['url'],
                    defaults={
                        'title': article['title'],
                        'source': article['source'],
                        'published_date': article['published_date'],
                        'summary': article['summary']
                    }
                )
                count += 1
            except Exception as e:
                logger.error(f"Error saving article {article.get('title', 'Unknown')}: {str(e)}")
        
        logger.info(f"Updated {count} {source_name} intelligence articles using free enhanced scraper")
        return f"Updated {count} {source_name} intelligence articles using free enhanced scraper"
    except Exception as e:
        logger.error(f"Error fetching {source_name} data with free enhanced scraper: {str(e)}")
        logger.info("Falling back to standard scraper as last resort")
        return fetch_dark_reading_intelligence()
