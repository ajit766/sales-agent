import os
import requests
import msal
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

D365_ORG_URL = os.getenv("D365_ORG_URL")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# D365 requires adding /.default to the resource URL. Ensure no trailing slash and has https://
_base_url = D365_ORG_URL.rstrip('/') if D365_ORG_URL else ""
if _base_url and not _base_url.startswith("http"):
    _base_url = f"https://{_base_url}"
SCOPE = [f"{_base_url}/.default"] if _base_url else []

def get_access_token():
    """Acquires a bearer token using AAD client credentials."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Could not acquire token: {result.get('error')} - {result.get('error_description')}")

def get_headers():
    """Generates the required headers for Dataverse API calls."""
    token = get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0"
    }

def get_opportunities():
    """Fetches all open opportunities with necessary fields and recent activities for Workstream 2 analysis."""
    endpoint = f"{_base_url}/api/data/v9.2/opportunities?$select=opportunityid,name,budgetamount,estimatedvalue,estimatedclosedate,stepname,modifiedon,_parentcontactid_value,statecode,_ownerid_value,closeprobability,salesstagecode,description&$filter=statecode eq 0&$expand=Opportunity_ActivityPointers($select=subject,activitytypecode,statecode,scheduledend,modifiedon;$top=5;$orderby=modifiedon desc)"
    response = requests.get(endpoint, headers=get_headers())
    response.raise_for_status()
    return response.json().get('value', [])

def get_todays_appointments():
    """Module 5 (Meeting Intelligence): Fetches all appointments scheduled for the current day."""
    from datetime import datetime, time, timezone
    
    # Dynamics Dataverse requires UTC ISO dates for filtering
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min).isoformat() + "Z"
    end_of_day = datetime.combine(today, time.max).isoformat() + "Z"
    
    # We filter by appointments scheduled today, expand the regardingobject (usually an Opportunity) 
    # to grab its name and value to provide context to the LLM
    endpoint = (
        f"{_base_url}/api/data/v9.2/appointments?"
        f"$select=subject,scheduledstart,scheduledend,description"
        f"&$filter=scheduledstart ge {start_of_day} and scheduledstart le {end_of_day}"
        f"&$expand=regardingobjectid_opportunity_appointment($select=name,estimatedvalue)"
    )
    
    try:
        response = requests.get(endpoint, headers=get_headers())
        response.raise_for_status()
        return response.json().get('value', [])
    except Exception as e:
        print(f"Error fetching today's appointments: {e}")
        return []

def update_opportunity(opportunity_id, update_data):
    """Updates specific fields on an opportunity based on transcript extraction."""
    endpoint = f"{_base_url}/api/data/v9.2/opportunities({opportunity_id})"
    response = requests.patch(endpoint, headers=get_headers(), json=update_data)
    response.raise_for_status()
    return True

def create_draft_task(opportunity_id, subject, description, owner_id=None):
    """Creates a Task activity linked to the opportunity."""
    endpoint = f"{_base_url}/api/data/v9.2/tasks"
    task_data = {
        "subject": subject,
        "description": description,
        "statecode": 0, # Open (Draft state)
        "regardingobjectid_opportunity@odata.bind": f"/opportunities({opportunity_id})"
    }
    
    # If we have the original human seller's ID, bind the task to them 
    # so it shows up in their "My Work -> Activities" dashboard!
    if owner_id:
        task_data["ownerid@odata.bind"] = f"/systemusers({owner_id})"
        
    response = requests.post(endpoint, headers=get_headers(), json=task_data)
    response.raise_for_status()
    # Return the ID of the created task if needed later
    if 'OData-EntityId' in response.headers:
        return response.headers['OData-EntityId'].split("(")[1].split(")")[0]
    return True

if __name__ == "__main__":
    # Self-test block to verify credentials
    if not all([D365_ORG_URL, TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Missing credentials! Please update your .env file.")
        exit(1)
        
    print("Testing D365 Connection...")
    try:
        opps = get_opportunities()
        print(f"Success! Found {len(opps)} open opportunities.")
        if len(opps) > 0:
            print(f"Sample First Opportunity Name: {opps[0].get('name')}")
    except Exception as e:
        print(f"Error connecting to Dataverse: {e}")
