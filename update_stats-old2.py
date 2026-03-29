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

# Official IPL 2026 Series ID for CricketData API
IPL_2026_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

# --- TARGET PLAYERS (Meet vs Pakshal) ---
TARGET_PLAYERS = [
    "Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul",
    "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"
]

def fetch_and_sync():
    logger.info("Starting IPL sync process...")
    
    # 1. Calculate yesterday's date (Format: YYYY-MM-DD)
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    logger.info(f"Targeting matches from yesterday: {yesterday}")

    # 2. Use the 'series_info' endpoint to get ONLY IPL 2026 matches
    url = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={IPL_2026_SERIES_ID}"
    try:
        response = requests.get(url).json()
    except Exception as e:
        logger.error(f"Failed to connect to Cricket API: {e}")
        return

    if response.get("status") != "success":
        logger.error(f"API Error: {response.get('reason')}")
        return

    match_list = response.get("data", {}).get("matchList", [])
    found_match = False

    for match in match_list:
        # Check if the match date matches yesterday AND has started
        if match.get("date") == yesterday and match.get("matchStarted"):
            found_match = True
            match_id = match["id"]
            logger.info(f"Found yesterday's match: {match['name']} (ID: {match_id})")
            
            # 3. Fetch the scorecard for this specific match
            score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                for inning in score_data["data"]["scorecard"]:
                    for batsman in inning["batting"]:
                        p_name = batsman["content"]
                        
                        # Case-insensitive matching
                        if any(target.lower() in p_name.lower() for target in TARGET_PLAYERS):
                            runs = int(batsman["r"])
                            
                            # 4. Upsert to Supabase
                            try:
                                supabase.table("player_runs").upsert({
                                    "player_name": p_name,
                                    "match_id": match_id,
                                    "runs": runs,
                                    "last_updated": datetime.now().isoformat()
                                }, on_conflict="player_name,match_id").execute()
                                logger.info(f"✅ Synced {p_name}: {runs} runs")
                            except Exception as db_err:
                                logger.error(f"Database error for {p_name}: {db_err}")
            else:
                logger.warning(f"Scorecard not available for Match ID: {match_id}")

    if not found_match:
        logger.info(f"No IPL 2026 matches found for {yesterday}.")

if __name__ == "__main__":
    fetch_and_sync()
