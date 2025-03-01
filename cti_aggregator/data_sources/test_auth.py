from falconpy import OAuth2

# Use the credentials from crowdstrike.py
from crowdstrike import CLIENT_ID, CLIENT_SECRET

def test_authentication():
    """Test if the CrowdStrike API credentials can authenticate."""
    print("Testing CrowdStrike API authentication...")
    
    # Create an auth object
    auth = OAuth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    
    # Try to get a token
    token_response = auth.token()
    
    if token_response["status_code"] == 201:
        print("✅ Authentication successful! API credentials are valid.")
        return True
    else:
        print(f"❌ Authentication failed: {token_response}")
        return False

if __name__ == "__main__":
    test_authentication() 