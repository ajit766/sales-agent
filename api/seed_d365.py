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
            "name": "ABC Corp - Enterprise Licenses",
            "budgetamount": 1800000.0,
            "estimatedvalue": 1800000.0,
            "estimatedclosedate": (today + timedelta(days=4)).strftime("%Y-%m-%d"), # Q1 Urgent
            "closeprobability": 80,
            "description": "Enterprise wide rollout. Waiting on our final contract.",
        },
        {
            "name": "Wholesome Cafe - POS System",
            "budgetamount": 42000.0,
            "estimatedvalue": 42000.0,
            "estimatedclosedate": (today + timedelta(days=10)).strftime("%Y-%m-%d"), # Q3 Quick Win
            "closeprobability": 90,
            "description": "Small POS deal. Very likely to close if we just send the quote.",
        },
        {
            "name": "XYZ Ltd - Cloud Migration",
            "budgetamount": 3200000.0,
            "estimatedvalue": 3200000.0,
            "estimatedclosedate": (today - timedelta(days=2)).strftime("%Y-%m-%d"), # Slipping
            "closeprobability": 60,
            "description": "Stuck in legal review. Need VP approval to bypass standard terms.",
        },
        {
            "name": "Zombie Tech - Legacy Support",
            "budgetamount": 150000.0,
            "estimatedvalue": 150000.0,
            "estimatedclosedate": (today + timedelta(days=60)).strftime("%Y-%m-%d"), # Q4 Zombie
            "closeprobability": 20,
            "description": "They haven't returned our calls in 3 weeks.",
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
            response = requests.post(endpoint, headers=get_headers(), json=opp)
            response.raise_for_status()
            print(f"✅ Created Opportunity: {opp['name']}")
            
            # Extract the new Opportunity ID to link a task
            opp_id = response.headers.get('OData-EntityId', '').split('(')[-1].split(')')[0]
            
            if opp_id and opp['name'] == "ABC Corp - Enterprise Licenses":
                 # Create a mock recent task to test Module 5 (Meeting prep)
                 task_data = {
                     "subject": "Prep for Final Demo with ABC Corp",
                     "description": "They are concerned about implementation timeline. We need to assure them we can deploy by next month.",
                     "scheduledend": (today + timedelta(days=1)).isoformat() + "Z",
                     "statecode": 0,
                     "regardingobjectid_opportunity@odata.bind": f"/opportunities({opp_id})"
                 }
                 task_res = requests.post(task_endpoint, headers=get_headers(), json=task_data)
                 task_res.raise_for_status()
                 print("   ↳ Added Prep Task to ABC Corp")
                 
        except Exception as e:
            print(f"❌ Failed to create {opp['name']}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 print(e.response.text)

if __name__ == "__main__":
    seed_opportunities()
