from falconpy import Intel
from crowdstrike import CLIENT_ID, CLIENT_SECRET

def test_intel_api():
    """Test retrieving intelligence data from CrowdStrike."""
    print("Testing CrowdStrike Intelligence API...")
    
    # Initialize the Intel API client
    intel_client = Intel(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    
    # Test 1: List available actor entities
    print("\nTest 1: Querying actor entities...")
    query_response = intel_client.query_actor_entities(limit=10)
    
    if query_response["status_code"] == 200:
        actor_ids = query_response["body"].get("resources", [])
        print(f"✅ Successfully queried actor entities: {len(actor_ids)} actors found")
        
        if actor_ids:
            print("Sample actor IDs:", actor_ids[:3])
        else:
            print("No actor IDs returned in the response")
    else:
        print(f"❌ Failed to query actor entities: {query_response}")
    
    # Test 2: Get actor entity details (if we have IDs)
    if query_response["status_code"] == 200 and query_response["body"].get("resources"):
        print("\nTest 2: Getting actor entity details...")
        actor_ids = query_response["body"]["resources"][:5]  # Get first 5 IDs
        
        details_response = intel_client.get_actor_entities(ids=actor_ids)
        
        if details_response["status_code"] == 200:
            actors = details_response["body"].get("resources", [])
            print(f"✅ Successfully retrieved details for {len(actors)} actors")
            
            if actors:
                for actor in actors:
                    print(f"  - {actor.get('name', 'Unnamed')} ({actor.get('id', 'No ID')})")
        else:
            print(f"❌ Failed to get actor details: {details_response}")
    
    # Test 3: Try an alternative intelligence endpoint (reports)
    print("\nTest 3: Querying intelligence reports...")
    reports_response = intel_client.query_report_entities(limit=5)
    
    if reports_response["status_code"] == 200:
        report_ids = reports_response["body"].get("resources", [])
        print(f"✅ Successfully queried reports: {len(report_ids)} reports found")
        
        if report_ids:
            print("Sample report IDs:", report_ids[:3])
        else:
            print("No report IDs returned in the response")
    else:
        print(f"❌ Failed to query reports: {reports_response}")

if __name__ == "__main__":
    test_intel_api() 