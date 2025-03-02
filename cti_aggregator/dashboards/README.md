# Malware Family Dashboard

A dashboard for visualizing malware family data from the CrowdStrike Falcon Intelligence API.

## Features

The dashboard displays comprehensive information about malware families including:

- **Malware name** and aliases
- **Publish date** (first seen) and last update date
- **Threat group affiliation** - associated threat actors/groups
- **Nation affiliation** - countries associated with development/deployment
- **TTPs** - Tactics, Techniques, and Procedures using MITRE ATT&CK framework
- **Sectors/Nations targeted** - industries and countries targeted by the malware

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

There are two ways to launch the dashboard:

#### 1. Using the launcher script (recommended)

From the project root directory, run:

```bash
python run_malware_dashboard.py
```

This will:
- Check if all dependencies are installed
- Install any missing requirements
- Launch the Streamlit server
- Open the dashboard in your default browser

#### 2. Directly using Streamlit

From the project root directory, run:

```bash
streamlit run dashboards/malware_dashboard.py
```

### Dashboard Interface

The dashboard interface consists of:

1. **Sidebar** - Contains search options and filters:
   - Recent Malware
   - Search by Name
   - Search by Malware ID

2. **Main Panel** - Displays the data in three tabs:
   - **Overview** - Tabular view with key information for all malware families
   - **Detailed View** - Expandable sections with comprehensive information for each malware family
   - **Raw Data** - JSON view of the raw data

### Search Options

- **Recent Malware**: Retrieve malware families discovered within a specified time period
- **Search by Name**: Search for malware families by name, type, or other keywords
- **Specific Malware ID**: Look up a specific malware family by its unique ID

## Data Sources

The dashboard retrieves data from the CrowdStrike Falcon Intelligence API using the custom `malware_family` module. This module handles authentication, querying, and processing of the data.

## Customizing the Dashboard

The dashboard appearance is controlled by the `style.css` file. You can modify this file to change the colors, fonts, and layout of the dashboard.

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that the CrowdStrike API credentials are correctly configured in the `crowdstrike.py` file
3. Verify that you have proper network connectivity to the CrowdStrike API
4. Look for error messages in the console output

## Screenshot

![Malware Dashboard Screenshot](screenshot.png) 