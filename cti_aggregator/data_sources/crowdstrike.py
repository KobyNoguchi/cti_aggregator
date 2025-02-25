from falconpy import APIHarness

CLIENT_ID = "fe308421c90f49bdbd35af9a707b223b"
CLIENT_SECRET = "StWbg65m8NL0woZf32D1XGUeTOCusEvp7V4K9kyq"

falcon = APIHarness(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def fetch_threat_actors():
    """Fetch threat actors from CrowdStrike."""
    response = falcon.command("queryIntelActorEntities", parameters={"limit": 10})

    # ✅ First check for HTTP status code
    if response.get("status_code") != 200:
        print(f"❌ Authentication Failed: {response}")
        return []

    # ✅ Now check if we actually got threat actors
    if "resources" in response and response["resources"]:
        print("✅ Authentication Successful! Falcon API is working.")
        return response["resources"]
    else:
        print("⚠️ No Threat Actor Data Found, but authentication succeeded.")
        return []


# Run test when script is executed directly
if __name__ == "__main__":
    test_authentication()

