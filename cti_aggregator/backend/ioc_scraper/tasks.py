import requests
from .models import Vulnerability
# celery addition 
import celery import shared_task
from datetime import datetime 

def fetch_cisa_vulnerabilities():
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    response = requests.get(url)
    data = response.json().get("vulnerabilities", [])

    for vuln in data:
        Vulnerability.objects.update_or_create(
            cve_id=vuln.get("cveID"),
            defaults={
                "vulnerability_name": vuln.get("vulnerabilityName"),
                "description": vuln.get("shortDescription"),
                "severity": vuln.get("severity"),
                "published_date": vuln.get("dateAdded"),
                "source_url": vuln.get("url","Unknown"),
            }
        )

@shared_task
def fetch_cisa_vulnerabilities():
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    response = requests.get(url)
    data = response.json().get("vulnerabilities", [])

    for vuln in data:
        published_date = vuln.get("dateAdded", "1970-01-01")  # Default to avoid errors
        published_date = datetime.strptime(published_date, "%Y-%m-%d").date()

        Vulnerability.objects.update_or_create(
            cve_id=vuln.get("cveID"),
            defaults={
                "vulnerability_name": vuln.get("vulnerabilityName"),
                "description": vuln.get("shortDescription"),
                "severity": vuln.get("severity"),
                "published_date": published_date,
                "source_url": vuln.get("url", "Unknown"),
            }
        )

    return f"Updated {len(data)} vulnerabilities from CISA KEV"
