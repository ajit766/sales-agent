import requests
from d365_client import get_headers, _base_url, get_opportunities

def clean_opportunities():
    print("🧹 Cleaning orphaned dummy opportunities from Dynamics 365...")
    
    # Define our dummy names
    dummy_names = [
        "ABC Corp - Enterprise Licenses",
        "Wholesome Cafe - POS System",
        "XYZ Ltd - Cloud Migration",
        "Zombie Tech - Legacy Support"
    ]

    try:
        opps = get_opportunities()
        if not opps:
            print("❌ No opportunities found.")
            return

        # We will keep track of seen names that HAVE an owner to avoid deleting the good ones.
        # Alternatively, we can just delete opportunities that match the dummy names AND lack an _ownerid_value, 
        # but let's just delete the ones without _ownerid_value or _parentcontactid_value to be safe.
        
        deleted_count = 0
        for opp in opps:
            name = opp.get("name")
            opp_id = opp.get("opportunityid")
            owner_id = opp.get("_ownerid_value")
            contact_id = opp.get("_parentcontactid_value")
            
            if name in dummy_names:
                # If it's missing the contact mapping (like our first run), we delete it.
                if not contact_id:
                    print(f"🗑️ Deleting orphaned '{name}' (ID: {opp_id})...")
                    endpoint = f"{_base_url}/api/data/v9.2/opportunities({opp_id})"
                    try:
                        resp = requests.delete(endpoint, headers=get_headers())
                        resp.raise_for_status()
                        print(f"✅ Deleted successfully.")
                        deleted_count += 1
                    except Exception as e:
                        print(f"❌ Failed to delete: {e}")
                else:
                    print(f"✨ Keeping valid mapped '{name}' (ID: {opp_id}).")

        print(f"🎉 Cleanup complete. Deleted {deleted_count} orphaned records.")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    clean_opportunities()
