# Data Sources Module

This directory contains modules for interacting with various Cyber Threat Intelligence (CTI) data sources.

## Modules

### CrowdStrike Intelligence API

The following modules provide access to CrowdStrike's Falcon Intelligence API:

- `crowdstrike.py` - Base module with authentication and threat actor retrieval
- `malware_family.py` - Module for retrieving malware family information

## Malware Family Module

The `malware_family.py` module provides functionality to retrieve detailed information about malware families from the CrowdStrike Intel API.

### Features

- Search for malware families by name, alias, or other attributes
- Retrieve recent malware families discovered within a specified time period
- Get detailed information for specific malware family IDs
- Access comprehensive malware information including:
  - Malware name and aliases
  - Publish date (first seen) and last update date
  - Associated threat groups and nation affiliations
  - Tactics, Techniques, and Procedures (TTPs) using MITRE ATT&CK framework
  - Targeted sectors and countries

### Usage

#### Basic Usage

```python
from data_sources.malware_family import search_malware_families

# Search for ransomware families
ransomware = search_malware_families(search_term="ransomware", limit=5)

# Display results
for malware in ransomware:
    print(f"Name: {malware.get('name')}")
    print(f"Description: {malware.get('description')}")
    print(f"First Seen: {malware.get('publish_date')}")
    print(f"Threat Groups: {', '.join(malware.get('threat_groups', []))}")
    print("---")
```

#### Getting Recent Malware

```python
from data_sources.malware_family import get_recent_malware_families

# Get malware families discovered in the last 30 days
recent_malware = get_recent_malware_families(days=30, limit=10)

# Process results
for malware in recent_malware:
    # Process each malware family
    pass
```

#### Retrieving Specific Malware Family Details

```python
from data_sources.malware_family import get_malware_details

# Get details for a specific malware family ID
malware_details = get_malware_details(["malware-id-1", "malware-id-2"])

# Process results
for malware in malware_details:
    # Process each malware family
    pass
```

### Example Script

An example script demonstrating how to use the malware family module is available at:
`cti_aggregator/examples/malware_example.py`

#### Running the Example

```bash
# Search for malware families by name or keyword
python examples/malware_example.py --search "ransomware" --limit 3

# Get malware families from the last N days
python examples/malware_example.py --recent 90 --limit 5

# Get details for a specific malware family ID
python examples/malware_example.py --id "malware-id"

# Output results in JSON format
python examples/malware_example.py --search "ransomware" --json
```

## Data Structure

The malware family data is returned as a list of dictionaries with the following structure:

```python
{
    "id": "unique-malware-id",
    "name": "Malware Name",
    "description": "Detailed description of the malware",
    "publish_date": "2023-01-01T00:00:00Z",
    "last_updated": "2023-06-15T00:00:00Z",
    "malware_type": "Ransomware",
    "threat_groups": ["Threat Group 1", "Threat Group 2"],
    "nation_affiliations": ["Nation 1", "Nation 2"],
    "ttps": [
        {
            "tactic": "Initial Access",
            "technique_id": "T1566",
            "technique": "Phishing",
            "sub_technique_id": "T1566.001",
            "sub_technique": "Spearphishing Attachment"
        },
        # Additional TTPs...
    ],
    "targeted_sectors": ["Financial Services", "Healthcare"],
    "targeted_countries": ["United States", "United Kingdom"],
    "family_id": "family-id",
    "aliases": ["Alias 1", "Alias 2"]
}
```

## Notes

- The module handles pagination and chunking of requests automatically.
- Not all fields may be available for all malware families.
- API rate limits may apply based on your CrowdStrike subscription. 