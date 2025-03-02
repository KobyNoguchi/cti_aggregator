# CrowdStrike Tailored Intelligence Module

This module provides functionality to fetch, process, and display CrowdStrike Tailored Intelligence reports in the CTI Aggregator dashboard.

## Features

- Fetches Tailored Intelligence reports from the CrowdStrike Falcon API
- Processes and normalizes the data for storage in the database
- Provides a React component for displaying the data in the dashboard
- Includes filtering by threat group, targeted sector, and search functionality
- Supports mock data generation for development and testing

## Components

The module consists of the following components:

1. **Backend**:
   - `tailored_intelligence.py`: Main module for fetching and processing data
   - `test_tailored_intelligence.py`: Test script for the module
   - Django model: `CrowdStrikeTailoredIntel` in `ioc_scraper/models.py`
   - API endpoint: `/api/crowdstrike/tailored-intel/`

2. **Frontend**:
   - React component: `TailoredIntel.tsx` in `frontend/my-heroui-dashboard/components/intel/`
   - Integration with the dashboard in `frontend/my-heroui-dashboard/app/dashboard/page.tsx`

## Installation

1. Ensure the Django backend is set up correctly
2. Run migrations to create the database table:
   ```
   cd cti_aggregator/backend
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Install the required dependencies:
   ```
   pip install falconpy
   ```

## Usage

### Updating the Database

To fetch and update the database with the latest Tailored Intelligence reports:

```bash
cd cti_aggregator
python run_tailored_intel_update.py
```

Options:
- `--test`: Run tests instead of updating the database
- `--verbose` or `-v`: Enable verbose logging

### API Configuration

To use the actual CrowdStrike API (instead of mock data), set the following environment variables:

```bash
export FALCON_CLIENT_ID="your-client-id"
export FALCON_CLIENT_SECRET="your-client-secret"
```

### Viewing the Data

The Tailored Intelligence reports are displayed in the dashboard at:
`http://localhost:3000/dashboard`

## Development

### Mock Data

The module includes a mock data generator for development and testing. When the CrowdStrike API credentials are not available, the module automatically falls back to using mock data.

### Testing

To run the tests:

```bash
cd cti_aggregator
python run_tailored_intel_update.py --test
```

Or directly:

```bash
cd cti_aggregator/data_sources
python test_tailored_intelligence.py
```

## Data Structure

Each Tailored Intelligence report includes the following information:

- **id**: Unique identifier for the report
- **name**: Title of the report
- **publish_date**: Date when the report was published
- **last_updated**: Date when the report was last updated
- **summary**: Summary of the report
- **url**: URL to the full report
- **threat_groups**: List of threat groups mentioned in the report
- **nation_affiliations**: List of nations affiliated with the threat groups
- **targeted_sectors**: List of industry sectors targeted
- **targeted_countries**: List of countries targeted

## Integration with Dashboard

The Tailored Intelligence module is integrated into the main dashboard and displays the reports in a card-based layout with filtering options. 