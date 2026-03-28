import os
import requests
from supabase import create_client

# 1. Setup Connections
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Players List from your image
TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def get_ipl_series_id():
    """Finds the official IPL 2026 Series ID using the search endpoint."""
    # FIX: Corrected the endpoint URL for searching
    url = f"https://api.cricapi.com/v1/series?apikey={API_KEY}&offset=0&search=Indian Premier League 2026"
    response = requests.get(url).json()
    
    if response.get("status") == "success":
        for series in response.get("data", []):
            if "Indian Premier League 2026" in series['name']:
                return series['id']
    return None

def fetch_and_sync():
    series_id = get_ipl_series_id()
    if not series_id:
        print("IPL 2026 Series not found. Skipping sync.")
        return

    # Fetching match IDs for this series
    url = f"https://api.cricapi.com/v1/series_matches?apikey={API_KEY}&id={series_id}"
    response = requests.get(url).json()
    
    if response.get("status") != "success":
        print(f"API Error: {response.get('reason')}")
        return

    for match in response.get("data", []):
        match_id = match["id"]
        
        # Get detailed scorecard
        score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
        score_data = requests.get(score_url).json()
        
        if score_data.get("status") == "success":
            for inning in score_data["data"]["scorecard"]:
                for batsman in inning["batting"]:
                    p_name = batsman["content"]
                    
                    if any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                        runs = int(batsman["r"])
                        
                        # Upsert to Supabase
                        supabase.table("player_runs").upsert({
                            "player_name": p_name,
                            "match_id": match_id,
                            "runs": runs
                        }, on_conflict="player_name,match_id").execute()
                        
                        print(f"✅ Synced {p_name}: {runs} runs")

if __name__ == "__main__":
    fetch_and_sync()
    
