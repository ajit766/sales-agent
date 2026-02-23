import requests
import json
from datetime import datetime, timedelta
from d365_client import get_headers, _base_url, get_opportunities

def seed_opportunities():
    print("🚀 Seeding Dummy Opportunities & Activities for Daily Briefing...")
    
    # Fetch an existing opportunity to steal its Contact, Currency, and Owner IDs
    try:
        existing_opps = get_opportunities()
        if not existing_opps:
            print("❌ No existing opportunities found to map fields from.")
            return
        base_opp = existing_opps[0]
        contact_id = base_opp.get("_parentcontactid_value")
        currency_id = base_opp.get("_transactioncurrencyid_value")
        owner_id = base_opp.get("_ownerid_value")
    except Exception as e:
        print(f"❌ Failed to fetch base opportunity: {e}")
        return
    
    today = datetime.now()
    
    # Define our test scenarios based on the PRD
    dummy_opportunities = [
        {
            "name": "Acme Corp - Blocked Deal",
            "budgetamount": 80000.0,
            "estimatedvalue": 80000.0,
            "estimatedclosedate": (today + timedelta(days=20)).strftime("%Y-%m-%d"),
            "closeprobability": 75,
            "description": "High probability, late stage, but no activity in > 3 days (Module A).",
            "overriddencreatedon": (today - timedelta(days=5)).isoformat() + "Z",
            "_spoofed_age_days": 5
        },
        {
            "name": "Global Tech - High Risk Enterprise",
            "budgetamount": 4500000.0,
            "estimatedvalue": 4500000.0,
            "estimatedclosedate": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "closeprobability": 40,
            "description": "Massive deal, top 25% pipeline size, with NO activity in > 7 days (Module B).",
            "overriddencreatedon": (today - timedelta(days=9)).isoformat() + "Z",
            "_spoofed_age_days": 9
        },
        {
            "name": "Venture Inc - Zombie Deal",
            "budgetamount": 120000.0,
            "estimatedvalue": 120000.0,
            "estimatedclosedate": (today - timedelta(days=5)).strftime("%Y-%m-%d"), 
            "closeprobability": 10,
            "description": "Late stage deal completely rotting on the vine > 14 days inactive (Module C).",
            "overriddencreatedon": (today - timedelta(days=19)).isoformat() + "Z",
            "_spoofed_age_days": 19
        }
    ]

    # Map the bindings
    for opp in dummy_opportunities:
        if contact_id:
            opp["parentcontactid@odata.bind"] = f"/contacts({contact_id})"
        if currency_id:
            opp["transactioncurrencyid@odata.bind"] = f"/transactioncurrencies({currency_id})"
        if owner_id:
            opp["ownerid@odata.bind"] = f"/systemusers({owner_id})"

    endpoint = f"{_base_url}/api/data/v9.2/opportunities"
    task_endpoint = f"{_base_url}/api/data/v9.2/tasks"
    
    for opp in dummy_opportunities:
        try:
            spoofed_days = opp.pop("_spoofed_age_days", 0)
            
            response = requests.post(endpoint, headers=get_headers(), json=opp)
            response.raise_for_status()
            print(f"✅ Created Opportunity: {opp['name']}")
            
            # Extract the new Opportunity ID to link a task
            opp_id = response.headers.get('OData-EntityId', '').split('(')[-1].split(')')[0]
            
            # Artificially age the modifiedon via a secondary PATCH if needed
            # (Note: In strict Dataverse, modifiedon is read-only unless overridden during data migration)
            # We will rely on overriddencreatedon for the initial seed, but if the API evaluates `modifiedon`,
            # we must ensure the Python script `/api/silent-risks` falls back to `createdon` if `modifiedon` is recent
            # OR we can just edit the Python script to use `overriddencreatedon` if available.
            # For this test, we'll patch the sales stage which is valid.
            
            patch_url = f"{endpoint}({opp_id})"
            # Set stage to 'Propose/2' depending on the scenario
            if opp['name'] == "Acme Corp - Blocked Deal" or opp['name'] == "Venture Inc - Zombie Deal":
                # Sales stage code varies by CRM instance, skipping to avoid validation errors,
                # our dummy python script evaluates stage > 1, but default dynamics might only have '1' mapped out of the box in this Dev instance.
                pass
                
        except Exception as e:
            print(f"❌ Failed to create {opp['name']}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 print(e.response.text)

if __name__ == "__main__":
    seed_opportunities()
