from falconpy import Intel

CLIENT_ID = "fe308421c90f49bdbd35af9a707b223b"
CLIENT_SECRET = "StWbg65m8NL0woZf32D1XGUeTOCusEvp7V4K9kyq"

# Use the Intel service specifically instead of the generic APIHarness
falcon = Intel(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def fetch_threat_actors():
    """Fetch threat actors from CrowdStrike."""
    # Using the correct method for the Intel service
    response = falcon.query_actor_entities(limit=50)  # Increased limit to get more actors

    # Check for HTTP status code
    if response["status_code"] != 200:
        print(f"❌ Authentication Failed: {response}")
        return []

    # Check if we actually got threat actors
    if "resources" in response["body"] and response["body"]["resources"]:
        print("✅ Authentication Successful! Falcon API is working.")
        return response["body"]["resources"]
    else:
        print("⚠️ No Threat Actor Data Found, but authentication succeeded.")
        return []

def get_actor_details(actor_data_list):
    """
    Process actor data directly from the query results.
    This replaces the previous get_actor_details function that used the get_actor_entities endpoint.
    
    Args:
        actor_data_list: List of actor data from query_actor_entities
        
    Returns:
        List of processed actors with standardized structure
    """
    if not actor_data_list:
        return []
    
    processed_actors = []
    
    for actor in actor_data_list:
        # Map fields from the query response to our expected structure
        actor_obj = {
            "id": actor.get("id"),
            "name": actor.get("name", "Unknown"),
            "description": actor.get("short_description", ""),
            "adversary_type": _extract_adversary_type(actor),
            "last_modified_date": _format_timestamp(actor.get("last_modified_date")),
            "origins": _extract_values(actor.get("origins", [])),
            "capabilities": _extract_values(actor.get("capabilities", [])),
            "motivations": _extract_values(actor.get("motivations", [])),
            "objectives": _extract_values(actor.get("objectives", []))
        }
        processed_actors.append(actor_obj)
    
    return processed_actors

# Helper functions to extract data from the API response
def _extract_values(items_list):
    """Extract values from a list of objects that have a 'value' key."""
    if not items_list:
        return []
    return [item.get("value") for item in items_list if item.get("value")]

def _extract_adversary_type(actor):
    """Determine the adversary type based on motivations."""
    motivations = _extract_values(actor.get("motivations", []))
    
    if "State-Sponsored" in motivations:
        return "nation-state"
    elif "Criminal" in motivations:
        return "criminal"
    elif any(m in motivations for m in ["Hacktivist", "Ideological"]):
        return "hacktivist"
    else:
        return "unknown"

def _format_timestamp(timestamp):
    """Convert UNIX timestamp to ISO format."""
    if not timestamp:
        return None
    
    from datetime import datetime
    
    try:
        # If it's already a string date, return as is
        if isinstance(timestamp, str):
            return timestamp
            
        # Convert UNIX timestamp to ISO format
        dt = datetime.fromtimestamp(timestamp)
        return dt.isoformat() + "Z"
    except:
        return None

# Test function
def test_connection():
    actors_data = fetch_threat_actors()
    if actors_data:
        processed_actors = get_actor_details(actors_data)
        print(f"Retrieved and processed details for {len(processed_actors)} actors")
        
        # Print sample data
        if processed_actors:
            print("\nSample actor data:")
            import json
            print(json.dumps(processed_actors[0], indent=2))
            
    return actors_data

# Run test when script is executed directly
if __name__ == "__main__":
    test_connection()

