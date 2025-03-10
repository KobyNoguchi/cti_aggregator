import os
from dotenv import load_dotenv

# Load the .env file
print("Attempting to load .env file...")
load_dotenv()

# Check if the variables are loaded
crowdstrike_client_id = os.environ.get('CROWDSTRIKE_CLIENT_ID')
crowdstrike_client_secret = os.environ.get('CROWDSTRIKE_CLIENT_SECRET')

# Print the results (without revealing the actual values)
print(f"CROWDSTRIKE_CLIENT_ID: {'✓ (Found)' if crowdstrike_client_id else '✗ (Not found)'}")
print(f"CROWDSTRIKE_CLIENT_SECRET: {'✓ (Found)' if crowdstrike_client_secret else '✗ (Not found)'}")

# If not found, let's check if they're using different variable names
print("\nChecking for other possible variable names:")
for key in os.environ.keys():
    if 'CROWD' in key.upper() or 'FALCON' in key.upper() or 'API' in key.upper() or 'KEY' in key.upper() or 'SECRET' in key.upper() or 'CLIENT' in key.upper() or 'ID' in key.upper():
        print(f"Found potential match: {key} ✓") 