import requests
from .models import Vulnerability

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
