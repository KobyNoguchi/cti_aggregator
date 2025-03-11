import requests
from .models import Vulnerability, IntelligenceArticle
from celery import shared_task, group, chain, chord
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging
from django.utils import timezone
from django.db.models import Count
from ioc_scraper.models import CrowdStrikeIntel, CrowdStrikeMalware
import sys
import os
import json
from django.db import connection
from django.db.models import Max, Q
from django.core.cache import cache
from celery.result import AsyncResult
from backend.celery import app as celery_app

# Configure logging
logger = logging.getLogger(__name__)

# Import Celery inspect functionality
try:
    # For Celery 5.x
    from celery.app.control import inspect
    logger.debug("Successfully imported inspect from celery.app.control")
except ImportError:
    try:
        # For Celery 4.x
        from celery.control import inspect
        logger.debug("Successfully imported inspect from celery.control")
    except ImportError:
        try:
            # Fallback method
            from celery import inspect
            logger.debug("Successfully imported inspect from celery")
        except ImportError:
            logger.warning("Could not import celery inspect functionality. Some monitoring features may be unavailable.")
            inspect = None

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
    """
    Orchestrate the fetching of intelligence articles from all sources in parallel,
    followed by post-processing tasks.
    """
    # Create a list of task signatures to execute in parallel
    scraper_tasks = [
        fetch_cisco_talos_intelligence.s(),
        fetch_microsoft_intelligence.s(),
        fetch_mandiant_intelligence.s(),
        fetch_unit42_intelligence.s(),
        fetch_zscaler_intelligence.s(),
        fetch_orange_defense_intelligence.s(),
        fetch_google_tag_intelligence.s(),
    ]
    
    # Add the appropriate dark reading scraper based on availability
    if ENHANCED_SCRAPER_AVAILABLE:
        scraper_tasks.append(fetch_dark_reading_enhanced.s())
    else:
        scraper_tasks.append(fetch_dark_reading_intelligence.s())
    
    # Use a chord to run all scrapers in parallel, then process the results
    # A chord is a group with a callback that's executed after all tasks in the group complete
    task_flow = chord(
        header=scraper_tasks,
        body=process_intelligence_data.s()
    )
    
    # Execute the task workflow
    result = task_flow.apply_async()
    
    return f"Intelligence data collection process initiated"

@shared_task
def process_intelligence_data(results):
    """
    Process the intelligence data after all sources have been fetched.
    This is run as a callback after all scraper tasks complete.
    
    Args:
        results: List of results from all scraper tasks
    """
    try:
        # Count total articles
        total_articles = IntelligenceArticle.objects.count()
        
        # Get stats on sources
        source_counts = IntelligenceArticle.objects.values('source').annotate(count=Count('source'))
        sources_summary = ", ".join([f"{item['source']}: {item['count']}" for item in source_counts])
        
        # Get the date range of intelligence articles
        latest_date = IntelligenceArticle.objects.order_by('-published_date').first()
        earliest_date = IntelligenceArticle.objects.order_by('published_date').first()
        
        date_range = ""
        if latest_date and earliest_date:
            date_range = f"ranging from {earliest_date.published_date.strftime('%Y-%m-%d')} to {latest_date.published_date.strftime('%Y-%m-%d')}"
        
        # Calculate how many new articles were fetched in this run
        one_day_ago = timezone.now() - timedelta(days=1)
        recent_articles = IntelligenceArticle.objects.filter(published_date__gte=one_day_ago).count()
        
        # Identify potential overlap or duplicate articles (articles with similar titles)
        # This is a simplified check - a more sophisticated approach could use text similarity
        message = f"Intelligence data processed: {total_articles} total articles from {len(source_counts)} sources ({sources_summary}) {date_range}. {recent_articles} new articles in the last 24 hours."
        
        logger.info(message)
        return message
    except Exception as e:
        logger.error(f"Error processing intelligence data: {str(e)}")
        return f"Error processing intelligence data: {str(e)}"

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
    Orchestrate fetching intelligence from CrowdStrike Intel Feed using task chains.
    """
    logger.info("Starting CrowdStrike intelligence collection workflow")
    
    # Create a chain of tasks with dependencies
    # 1. Fetch threat actors
    # 2. Fetch malware data
    # 3. Fetch tailored intelligence (via update_tailored_intelligence task)
    # 4. Process and summarize all collected data
    workflow = chain(
        fetch_crowdstrike_actors.s(),
        fetch_crowdstrike_malware.s(),
        update_tailored_intelligence.s(),
        summarize_crowdstrike_intel.s()
    )
    
    # Execute the workflow
    result = workflow.apply_async()
    
    return "CrowdStrike intelligence collection workflow initiated"

@shared_task
def fetch_crowdstrike_actors():
    """
    Fetch threat actors from CrowdStrike API.
    This is step 1 in the CrowdStrike intelligence collection workflow.
    """
    logger.info("Fetching CrowdStrike threat actors...")
    
    try:
        # Get threat actors from CrowdStrike API
        actors_data = fetch_threat_actors()
        
        if not actors_data:
            logger.warning("No threat actors data received from CrowdStrike API.")
            return "No threat actors data received"
            
        # Process actor data directly from the response
        processed_actors = get_actor_details(actors_data)
        
        created_count = 0
        updated_count = 0
        
        for actor in processed_actors:
            # Update or create actor
            obj, created = CrowdStrikeIntel.objects.update_or_create(
                actor_id=actor['id'],
                defaults={
                    'name': actor['name'],
                    'description': actor.get('description'),
                    'capabilities': actor.get('capabilities', []),
                    'motivations': actor.get('motivations', []),
                    'objectives': actor.get('objectives', []),
                    'adversary_type': actor.get('type'),
                    'origins': actor.get('origins', []),
                    'last_update_date': timezone.now()
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        result_message = f"CrowdStrike Actors: Created {created_count}, Updated {updated_count}"
        logger.info(result_message)
        return result_message
    
    except Exception as e:
        error_message = f"Error fetching CrowdStrike threat actors: {str(e)}"
        logger.error(error_message)
        return error_message

@shared_task
def fetch_crowdstrike_malware(previous_result=None):
    """
    Fetch malware data from CrowdStrike API.
    This is step 2 in the CrowdStrike intelligence collection workflow.
    
    Args:
        previous_result: Result from the previous task in the chain (fetch_crowdstrike_actors)
    """
    logger.info(f"Fetching CrowdStrike malware data... (Previous task result: {previous_result})")
    
    try:
        # TODO: Implement actual malware data fetching from CrowdStrike API
        # This is a placeholder - in a real implementation, you'd call the API to get malware data
        
        # For now, we'll just log that this was called
        result_message = "CrowdStrike Malware: Collection not yet implemented"
        logger.info(result_message)
        return result_message
    
    except Exception as e:
        error_message = f"Error fetching CrowdStrike malware data: {str(e)}"
        logger.error(error_message)
        return error_message

@shared_task
def summarize_crowdstrike_intel(previous_result=None):
    """
    Summarize all collected CrowdStrike intelligence.
    This is the final step in the CrowdStrike intelligence collection workflow.
    
    Args:
        previous_result: Result from the previous task in the chain
    """
    logger.info(f"Summarizing CrowdStrike intelligence... (Previous task result: {previous_result})")
    
    try:
        # Count total entities
        actor_count = CrowdStrikeIntel.objects.count()
        malware_count = CrowdStrikeMalware.objects.count()
        tailored_intel_count = CrowdStrikeTailoredIntel.objects.count()
        
        # Get timestamp of most recent data
        most_recent_actor = CrowdStrikeIntel.objects.order_by('-last_update_date').first()
        most_recent_actor_date = most_recent_actor.last_update_date if most_recent_actor else "N/A"
        
        most_recent_intel = CrowdStrikeTailoredIntel.objects.order_by('-last_updated').first()
        most_recent_intel_date = most_recent_intel.last_updated if most_recent_intel else "N/A"
        
        # Create summary
        summary = (
            f"CrowdStrike Intelligence Summary:\n"
            f"- Threat Actors: {actor_count} (last updated: {most_recent_actor_date})\n"
            f"- Malware Families: {malware_count}\n"
            f"- Tailored Intelligence Reports: {tailored_intel_count} (last updated: {most_recent_intel_date})\n"
        )
        
        logger.info(summary)
        return summary
    
    except Exception as e:
        error_message = f"Error summarizing CrowdStrike intelligence: {str(e)}"
        logger.error(error_message)
        return error_message

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

@shared_task
def system_health_check():
    """
    Perform system health checks, cleanup, and generate status report.
    This task runs daily to ensure the system is functioning properly.
    """
    logger.info("Running system health check...")
    
    # Collect health check results with error handling
    results = {
        "database": check_database_health(),
    }
    
    # Check Celery health with additional error handling
    try:
        results["celery"] = check_celery_health()
    except Exception as e:
        logger.error(f"Celery health check completely failed: {str(e)}")
        results["celery"] = {
            "status": "unhealthy", 
            "details": f"Health check error: {str(e)}"
        }
    
    # Continue with other checks
    try:
        results["data_sources"] = check_data_sources_health()
    except Exception as e:
        logger.error(f"Data sources health check failed: {str(e)}")
        results["data_sources"] = {
            "status": "unhealthy", 
            "details": f"Health check error: {str(e)}"
        }
    
    try:
        results["cleanup"] = perform_cleanup_tasks()
    except Exception as e:
        logger.error(f"Cleanup tasks failed: {str(e)}")
        results["cleanup"] = {
            "status": "degraded", 
            "details": f"Cleanup error: {str(e)}"
        }
    
    # Generate overall status
    unhealthy_count = sum(1 for v in results.values() if v.get("status") == "unhealthy")
    degraded_count = sum(1 for v in results.values() if v.get("status") == "degraded")
    
    if unhealthy_count > 0:
        overall_status = "unhealthy"
    elif degraded_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    # Create summary
    summary = f"System Health: {overall_status.upper()}\n"
    for component, info in results.items():
        summary += f"- {component}: {info['status']}"
        if info.get("details"):
            summary += f" ({info['details']})"
        summary += "\n"
    
    logger.info(summary)
    
    # Store the health check result in cache for dashboard display
    cache.set("system_health_check_result", {
        "timestamp": timezone.now().isoformat(),
        "overall_status": overall_status,
        "results": results,
        "summary": summary,
    }, timeout=86400)  # Cache for 24 hours
    
    return summary

def check_database_health():
    """Check database connection and integrity."""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Get database stats
        article_count = IntelligenceArticle.objects.count()
        intel_count = CrowdStrikeTailoredIntel.objects.count()
        actor_count = CrowdStrikeIntel.objects.count()
        
        # Check for any tables with 0 records (potential issues)
        empty_tables = []
        if article_count == 0:
            empty_tables.append("intelligence_articles")
        if intel_count == 0:
            empty_tables.append("tailored_intel")
        if actor_count == 0:
            empty_tables.append("threat_actors")
        
        if empty_tables:
            return {
                "status": "degraded", 
                "details": f"Empty tables: {', '.join(empty_tables)}"
            }
        
        return {"status": "healthy", "details": f"{article_count} articles, {intel_count} intel reports, {actor_count} actors"}
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "details": str(e)}

def check_celery_health():
    """Check Celery worker and tasks health."""
    try:
        # Check if inspect is available
        if inspect is None:
            logger.warning("Celery health check degraded: inspect functionality not available")
            return {
                "status": "degraded", 
                "details": "Celery inspect functionality not available. Install the appropriate Celery version."
            }
            
        # Initialize inspector
        try:
            inspector = inspect()
            if inspector is None:
                logger.warning("Celery health check degraded: inspector could not be initialized")
                return {
                    "status": "degraded", 
                    "details": "Celery inspector could not be initialized."
                }
                
            # Check if Celery workers are running
            active_workers = inspector.active()
            
            if not active_workers:
                logger.warning("Celery health check failed: No active workers found")
                return {"status": "unhealthy", "details": "No active workers found. Make sure Celery workers are running."}
            
            # Check for tasks stuck in reserved state
            reserved = inspector.reserved()
            reserved_count = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
            
            # Check scheduled tasks
            scheduled = inspector.scheduled()
            scheduled_count = sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0
            
            # Get stats about workers
            stats = inspector.stats()
            worker_count = len(stats) if stats else 0
            
            return {
                "status": "healthy",
                "details": f"Active workers: {worker_count}, Reserved tasks: {reserved_count}, Scheduled tasks: {scheduled_count}"
            }
        except Exception as e:
            logger.error(f"Error while using Celery inspector: {str(e)}")
            return {
                "status": "degraded",
                "details": f"Error inspecting Celery workers: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Celery health check failed: {str(e)}")
        return {"status": "unhealthy", "details": str(e)}

def check_data_sources_health():
    """Check data sources health based on last update time."""
    try:
        # Check when data was last updated
        current_time = timezone.now()
        
        # Intelligence articles - should be updated at least every 12 hours
        latest_article = IntelligenceArticle.objects.order_by('-published_date').first()
        latest_article_age = None
        if latest_article:
            latest_article_age = (current_time - latest_article.published_date).total_seconds() / 3600  # in hours
        
        # CrowdStrike data - should be updated at least daily
        latest_intel = CrowdStrikeTailoredIntel.objects.order_by('-last_updated').first()
        latest_intel_age = None
        if latest_intel and latest_intel.last_updated:
            latest_intel_age = (current_time - latest_intel.last_updated).total_seconds() / 3600  # in hours
        
        # Check if data is stale
        stale_sources = []
        if latest_article_age and latest_article_age > 24:  # More than 24 hours old
            stale_sources.append(f"intelligence articles ({int(latest_article_age)} hours old)")
        
        if latest_intel_age and latest_intel_age > 48:  # More than 48 hours old
            stale_sources.append(f"tailored intelligence ({int(latest_intel_age)} hours old)")
        
        if stale_sources:
            return {"status": "degraded", "details": f"Stale data: {', '.join(stale_sources)}"}
        
        return {"status": "healthy", "details": "All data sources updated recently"}
    
    except Exception as e:
        logger.error(f"Data sources health check failed: {str(e)}")
        return {"status": "degraded", "details": str(e)}

def perform_cleanup_tasks():
    """Perform cleanup tasks to maintain system health."""
    try:
        cleanup_actions = []
        
        # Remove duplicate intelligence articles (based on URL)
        with connection.cursor() as cursor:
            # Find duplicate URLs
            cursor.execute("""
                SELECT url, COUNT(*) as count 
                FROM ioc_scraper_intelligencearticle 
                GROUP BY url 
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            
            # Remove duplicates (keep the most recent)
            for url, count in duplicates:
                # Get IDs of all articles with this URL, ordered by published_date (latest first)
                articles = IntelligenceArticle.objects.filter(url=url).order_by('-published_date')
                
                # Keep the first one (most recent), delete the rest
                if articles.count() > 1:
                    for article in articles[1:]:
                        article.delete()
                        
                    cleanup_actions.append(f"Removed {count-1} duplicate articles for URL: {url}")
        
        # Clean up any temporary cached data older than 30 days
        # (Implementation would depend on your caching strategy)
        
        if cleanup_actions:
            return {"status": "healthy", "details": f"Performed {len(cleanup_actions)} cleanup actions"}
        else:
            return {"status": "healthy", "details": "No cleanup needed"}
    
    except Exception as e:
        logger.error(f"Cleanup tasks failed: {str(e)}")
        return {"status": "degraded", "details": str(e)}
