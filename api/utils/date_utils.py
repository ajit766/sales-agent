from datetime import datetime

def parse_date(date_str):
    if not date_str: return None
    try:
        if len(date_str) == 10: return datetime.strptime(date_str, "%Y-%m-%d")
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
    except:
        return None
