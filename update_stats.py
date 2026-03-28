import os
import requests
from supabase import create_client

# 1. Setup Connections using Environment Variables
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
IPL_2026_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

# Players List
TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def get_ipl_series_id():
    """Dynamically finds the official IPL 2026 Series ID."""
    #url = f"https://api.cricapi.com/v1/series?apikey={API_KEY}&offset=0&search=IPL 2026"
    url = f"https://api.cricapi.com/v1/series_matches?apikey={API_KEY}&id={series_id}"
    response = requests.get(url).json()
    
    if response.get("status") == "success":
        for series in response.get("data", []):
            # We look for the exact tournament name to get the correct ID
            if "Indian Premier League 2026" in series['name']:
                return series['id']
    return None

def fetch_and_sync():
    # Step A: Get the specific Series ID for IPL 2026
    series_id = get_ipl_series_id()
    if not series_id:
        print("IPL 2026 Series not found. Skipping sync.")
        return

    # Step B: Get matches only for this specific series
    # This is more precise than searching by name strings
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    response = requests.get(url).json()
    
    if response.get("status") != "success":
        print("API Error:", response.get("reason"))
        return

    for match in response.get("data", []):
        # STRICTOR FILTER: Only process if the match belongs to the IPL 2026 Series ID
        if match.get("series_id") == series_id:
            match_id = match["id"]
            
            # Get the detailed scorecard for this specific match
            score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                # API returns scorecard as a list of innings
                for inning in score_data["data"]["scorecard"]:
                    for batsman in inning["batting"]:
                        p_name = batsman["content"]
                        
                        # Match against our 10 tracked players (Case-Insensitive)
                        if any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                            runs = int(batsman["r"])
                            
                            # Upsert to Supabase: Updates existing record or inserts new one
                            # This prevents duplicate entries for the same match
                            supabase.table("player_runs").upsert({
                                "player_name": p_name,
                                "match_id": match_id,
                                "runs": runs
                            }, on_conflict="player_name,match_id").execute()
                            
                            print(f"✅ Synced {p_name}: {runs} runs (Match ID: {match_id})")

if __name__ == "__main__":
    fetch_and_sync()
