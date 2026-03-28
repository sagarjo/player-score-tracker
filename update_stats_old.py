import os
import requests
from supabase import create_client

# Use Environment Variables from GitHub Secrets
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
API_KEY = os.getenv("CRICKET_API_KEY")

PLAYERS = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", 
            "KL Rahul", "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", 
            "Mitchell Marsh", "Sai Sudharsan"]

def update_daily_scores():
    # 1. Get recent match IDs from API
    # 2. Fetch scorecard for those matches
    # 3. Filter for our specific players
    # 4. Upsert to Supabase
    print("Fetching daily IPL scores...")
    # Example logic: supabase.table("player_runs").upsert({...}).execute()

if __name__ == "__main__":
    update_daily_scores()

