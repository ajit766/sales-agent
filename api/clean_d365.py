import requests
from d365_client import get_headers, _base_url, get_opportunities

def clean_opportunities():
    print("🧹 Cleaning orphaned dummy opportunities from Dynamics 365...")
    
    # Define our dummy names
    dummy_names = [
        "ABC Corp - Enterprise Licenses",
        "Wholesome Cafe - POS System",
        "XYZ Ltd - Cloud Migration",
        "Zombie Tech - Legacy Support",
        "Acme Corp - Blocked Deal",
        "Global Tech - High Risk Enterprise",
        "Venture Inc - Zombie Deal"
    ]

    try:
        opps = get_opportunities()
        if not opps:
            print("❌ No opportunities found.")
            return

        deleted_count = 0
        seen_names = set()
        
        for opp in opps:
            name = opp.get("name")
            opp_id = opp.get("opportunityid")
            
            if name in dummy_names:
                if name in seen_names:
                    print(f"🗑️ Deleting duplicate '{name}' (ID: {opp_id})...")
                    endpoint = f"{_base_url}/api/data/v9.2/opportunities({opp_id})"
                    try:
                        resp = requests.delete(endpoint, headers=get_headers())
                        resp.raise_for_status()
                        print(f"✅ Deleted successfully.")
                        deleted_count += 1
                    except Exception as e:
                        print(f"❌ Failed to delete: {e}")
                else:
                    print(f"✨ Keeping primary '{name}' (ID: {opp_id}).")
                    seen_names.add(name)

        print(f"🎉 Cleanup complete. Deleted {deleted_count} duplicate records.")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    clean_opportunities()
