import os
import requests
from supabase import create_client

# Setup Connections using Environment Variables (GitHub Secrets)
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Official IPL 2026 Series ID for CricketData API
IPL_2026_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def fetch_and_sync():
    # Use the hardcoded Series ID for reliability
    series_id = IPL_2026_SERIES_ID

    # Get matches for IPL 2026
    url = f"https://api.cricapi.com/v1/series_matches?apikey={API_KEY}&id={series_id}"
    response = requests.get(url).json()
    
    if response.get("status") != "success":
        print(f"API Error: {response.get('reason')}")
        return

    for match in response.get("data", []):
        match_id = match["id"]
        
        # Only check scorecard if the match is recently completed or live
        score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
        score_data = requests.get(score_url).json()
        
        if score_data.get("status") == "success":
            for inning in score_data["data"]["scorecard"]:
                for batsman in inning["batting"]:
                    p_name = batsman["content"]
                    
                    # Case-insensitive matching for your players
                    if any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                        runs = int(batsman["r"])
                        
                        # Sync to Supabase
                        supabase.table("player_runs").upsert({
                            "player_name": p_name,
                            "match_id": match_id,
                            "runs": runs
                        }, on_conflict="player_name,match_id").execute()
                        
                        print(f"✅ Synced {p_name}: {runs} runs")

if __name__ == "__main__":
    fetch_and_sync()
    
