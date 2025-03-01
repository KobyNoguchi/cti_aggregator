import requests
from .models import Vulnerability, IntelligenceArticle
from celery import shared_task
from datetime import datetime 
from bs4 import BeautifulSoup
import logging

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
