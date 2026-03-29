import os
import requests
import logging
from datetime import datetime, timedelta
from supabase import create_client

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONNECTIONS ---
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Official IPL 2026 Series ID
IPL_2026_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

# --- TARGET PLAYERS ---
TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def fetch_and_sync():
    logger.info("Starting IPL sync process...")
    
    # Targeting yesterday's match to ensure data is finalized
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    logger.info(f"Targeting matches from: {yesterday}")

    # Step 1: Get IPL 2026 matches (Cost: 1 hit)
    url = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={IPL_2026_SERIES_ID}"
    try:
        response = requests.get(url).json()
        if response.get("status") != "success":
            logger.error(f"API Error: {response.get('reason')}")
            return
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return

    match_list = response.get("data", {}).get("matchList", [])
    for match in match_list:
        # Match filtering logic
        if match.get("date") == yesterday and match.get("matchStarted"):
            match_id = match["id"]
            logger.info(f"Processing Match: {match['name']} ({match_id})")
            
            # Step 2: Fetch scorecard (Cost: 1 hit)
            score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                # Navigate scorecard data based on Sample.txt structure
                for inning in score_data["data"].get("scorecard", []):
                    for batsman_data in inning.get("batting", []):
                        # FIX: Access name via ['batsman']['name'] per Sample.txt
                        p_name = batsman_data.get("batsman", {}).get("name")
                        
                        if p_name and any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                            runs = int(batsman_data.get("r", 0))
                            
                            # Upsert to Supabase
                            supabase.table("player_runs").upsert({
                                "player_name": p_name,
                                "match_id": match_id,
                                "runs": runs,
                            }, on_conflict="player_name,match_id").execute()
                            logger.info(f"✅ Synced {p_name}: {runs} runs")

if __name__ == "__main__":
    fetch_and_sync()
