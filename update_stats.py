import os
import requests
import logging
from datetime import datetime, timedelta
from supabase import create_client

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONNECTIONS ---
API_KEY = os.getenv("CRICKET_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

IPL_2026_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

# Combined unique players from all four teams
TARGET_PLAYERS = list(set([
    "Shreyas Iyer", "Abhishek Sharma", "Shubman Gill", "KL Rahul", "Mitchell Marsh", 
    "Suryakumar Yadav", "Yashasvi Jaiswal", "Jos Buttler", "Phil Salt", "Finn Allen", 
    "Dewald Brevis", "Prabhsimran Singh", "Vaibhav Sooryavanshi", "Rishabh Pant", 
    "Ayush Mhatre", "Heinrich Klaasen", "Nitish Rana", "Riyan Parag", "Shivam Dube", 
    "Nehal Wadhera", "Virat Kohli", "Ishan Kishan", "Travis Head", "Sanju Samson", 
    "Rajat Patidar", "Sai Sudharsan", "Ruturaj Gaikwad", "Aiden Markram", "Nicholas Pooran", 
    "Rohit Sharma", "Quinton de Kock", "Priyansh Arya", "Tilak Varma", "Shimron Hetmyer", 
    "Ajinkya Rahane", "Pathum Nissanka", "Tristan Stubbs", "Glenn Phillips", "Dhruv Jurel", "Cameron Green"
]))

def fetch_and_sync():
    logger.info("Starting expanded IPL sync...")
    
    # Get matches for IPL 2026 Series specifically (1 API Hit)
    url = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={IPL_2026_SERIES_ID}"
    response = requests.get(url).json()
    
    if response.get("status") != "success":
        logger.error(f"API Error: {response.get('reason')}")
        return

    match_list = response.get("data", {}).get("matchList", [])
    for match in match_list:
        # Only process matches that have actually started or finished
        if match.get("matchStarted"):
            match_id = match["id"]
            
            # Fetch Scorecard (1 API Hit per IPL match)
            score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
            score_data = requests.get(score_url).json()
            
            if score_data.get("status") == "success":
                for inning in score_data["data"].get("scorecard", []):
                    for batsman_data in inning.get("batting", []):
                        # Access name as per API structure
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

