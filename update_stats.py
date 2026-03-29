import os
import requests
from supabase import create_client
from datetime import datetime, timedelta

# Setup Connections
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TARGET_PLAYERS = [...] # Your existing list

def get_ipl_series_id():
    url = f"https://api.cricapi.com/v1/series?apikey={API_KEY}&offset=0&search=Indian Premier League 2026"
    response = requests.get(url).json()
    if response.get("status") == "success":
        for series in response.get("data", []):
            if "Indian Premier League 2026" in series['name']:
                return series['id']
    return None

def fetch_and_sync():
    #series_id = get_ipl_series_id()
    series_id="87c62aac-bc3c-4738-ab93-19da0690488f"
    #if not series_id: return

    # Calculate yesterday's date (Format: YYYY-MM-DD)
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    url = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={series_id}"
    response = requests.get(url).json()
    
    if response.get("status") == "success":
        match_list = response.get("data", {}).get("matchList", [])
        for match in match_list:
            # FIX: Only fetch scorecard if match was yesterday and has started
            if match.get("date") == yesterday and match.get("matchStarted"):
                match_id = match["id"]
                score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                for inning in score_data["data"]["scorecard"]:
                    for batsman in inning["batting"]:
                        p_name = batsman["content"]
                        
                        # Match against Team Meet & Team Pakshal lists
                        if any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                            runs = int(batsman["r"])
                            
                            supabase.table("player_runs").upsert({
                                "player_name": p_name,
                                "match_id": match_id,
                                "runs": runs
                            }, on_conflict="player_name,match_id").execute()
                            
                            print(f"✅ Synced {p_name}: {runs} runs")
    
