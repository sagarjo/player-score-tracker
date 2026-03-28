import os
import requests
from supabase import create_client

# 1. Setup Connections
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Players from your image
TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def fetch_and_sync():
    # Get current/recent matches
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    response = requests.get(url).json()
    
    if response.get("status") != "success":
        print("API Error:", response.get("reason"))
        return

    for match in response.get("data", []):
        # We only care about IPL 2026 matches
        if "IPL" in match.get("name", "") or "Indian Premier League" in match.get("name", ""):
            match_id = match["id"]
            
            # Get the detailed scorecard for this specific match
            score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                # The API returns a list of innings; we loop through each to find batting stats
                for inning in score_data["data"]["scorecard"]:
                    for batsman in inning["batting"]:
                        p_name = batsman["content"] # Name of the player
                        
                        # Only sync if the player is in our specific list
                        if any(target in p_name for target in TARGET_PLAYERS):
                            runs = int(batsman["r"])
                            
                            # Push to Supabase (Upsert: Update if exists, Insert if new)
                            supabase.table("player_runs").upsert({
                                "player_name": p_name,
                                "match_id": match_id,
                                "runs": runs
                            }, on_conflict="player_name,match_id").execute()
                            print(f"Synced {p_name}: {runs} runs")

if __name__ == "__main__":
    fetch_and_sync()
