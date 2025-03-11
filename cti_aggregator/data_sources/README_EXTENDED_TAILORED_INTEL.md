# Extended CrowdStrike Tailored Intelligence

This implementation adds support for querying and displaying additional fields from the CrowdStrike Tailored Intelligence API:

- Source
- Hit Type
- Matched rule names
- Details
- First Seen

## Implementation Details

The implementation consists of the following components:

1. **Test Script** (`test_tailored_intel_extended.py`): Tests the ability to query the CrowdStrike API for the extended fields.

2. **Extended API Module** (`tailored_intel_extended.py`): Implements the functionality to fetch and process the extended fields from the CrowdStrike API.

3. **Update Script** (`run_tailored_intel_extended_update.py`): Provides a command-line interface to run the update process.

4. **API Serializer Update**: Updates the API serializer to include the new fields in the API response.

5. **Frontend Update**: Updates the frontend to display the new fields in the UI.

## Usage

### Running the Test

To test the implementation without saving data to the database:

```bash
python data_sources/test_tailored_intel_extended.py
```

### Running the Update

To fetch and save the extended tailored intelligence data:

```bash
python run_tailored_intel_extended_update.py
```

Options:
- `--limit LIMIT`: Maximum number of indicators to fetch (default: 100)
- `--test`: Run in test mode (display results without saving)

### API Endpoints

The extended fields are available through the existing API endpoint:

```
/api/crowdstrike/tailored-intel/
```

## Implementation Notes

### Database Changes

The implementation adds the following fields to the `CrowdStrikeTailoredIntel` model:

- `source`: The source of the intelligence (e.g., "CrowdStrike")
- `hit_type`: The type of hit (e.g., "high", "medium", "low")
- `matched_rule_names`: JSON array of rule names that matched the indicator
- `details`: Detailed description of the indicator
- `first_seen`: Timestamp when the indicator was first seen

### API Changes

The API serializer has been updated to include the new fields in the response.

### Frontend Changes

The frontend has been updated to display the new fields in the UI:

- The table now shows Source, Hit Type, and First Seen columns
- The expanded row details include Matched Rules and Details sections

## Credentials

The implementation uses the CrowdStrike API credentials stored in the `.env` file:

- `FALCON_CLIENT_ID`: CrowdStrike API client ID
- `FALCON_CLIENT_SECRET`: CrowdStrike API client secret

## Dependencies

- FalconPy: CrowdStrike API client library
- Django: Web framework for the backend
- React: Frontend library

## Troubleshooting

If you encounter issues with the implementation:

1. Check that the CrowdStrike API credentials are correctly set in the `.env` file
2. Verify that the FalconPy library is installed (`pip install falconpy`)
3. Check the logs for error messages
4. Run the test script to verify API connectivity 