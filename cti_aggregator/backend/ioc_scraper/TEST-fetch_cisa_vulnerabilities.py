import requests

# CISA KEV API Endpoint
URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

def fetch_cisa_data():
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("vulnerabilities", [])  # Extract vulnerabilities list
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

if __name__ == "__main__":
    vulnerabilities = fetch_cisa_data()
    print(vulnerabilities[:2])  # Print first 2 entries for verification

