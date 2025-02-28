import requests
from .models import Vulnerability
from celery import shared_task
from datetime import datetime 

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
