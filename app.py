import streamlit as st
import pandas as pd
from supabase import create_client

# --- INITIALIZATION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key) 

# --- TEAM DEFINITIONS ---
# Original 5-player teams (Checked FIRST to prevent overlap)
TEAM_MEET = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul"]
TEAM_PAKSHAL = ["Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"]

# New 20-player teams
TEAM_MANDAR = [
    "Shreyas Iyer", "Abhishek Sharma", "Shubman Gill", "KL Rahul", "Mitchell Marsh", 
    "Suryakumar Yadav", "Yashasvi Jaiswal", "Jos Buttler", "Philip Salt", "Finn Allen", 
    "Dewald Brevis", "Prabhsimran Singh", "Vaibhav Sooryavanshi", "Rishabh Pant", 
    "Ayush Mhatre", "Heinrich Klaasen", "Nitish Rana", "Riyan Parag", "Shivam Dube", "Nehal Wadhera"
]

TEAM_MEET_2 = [
    "Virat Kohli", "Ishan Kishan", "Travis Head", "Sanju Samson", "Rajat Patidar", 
    "Sai Sudharsan", "Ruturaj Gaikwad", "Aiden Markram", "Nicholas Pooran", "Rohit Sharma", 
    "Quinton de Kock", "Priyansh Arya", "Tilak Varma", "Shimron Hetmyer", "Ajinkya Rahane", 
    "Pathum Nissanka", "Tristan Stubbs", "Glenn Phillips", "Dhruv Jurel", "Cameron Green"
]

st.set_page_config(page_title="IPL 2026 Tracker", page_icon="🏏", layout="wide")
st.title("🏏 IPL 2026: 4-Team Standings")

def get_data():
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

try:
    df = get_data()
except Exception as e:
    st.error(f"Error: {e}")
    df = pd.DataFrame()

if not df.empty:
    def assign_team(name):
        n = name.lower()
        # PRIORITY ORDER: Check small original teams first
        if any(p.lower() in n for p in TEAM_MEET): return "Team Meet"
        if any(p.lower() in n for p in TEAM_PAKSHAL): return "Team Pakshal"
        # Then assign remaining players to the new squads
        if any(p.lower() in n for p in TEAM_MANDAR): return "Team Mandar"
        if any(p.lower() in n for p in TEAM_MEET_2): return "Team Meet 2"
        return "Other"

    df['Team'] = df['player_name'].apply(assign_team)
    df = df[df['Team'] != "Other"]

    # --- 4-TEAM BAR CHART ---
    st.subheader("Cumulative Runs by Team")
    team_comparison = df.groupby("Team")["runs"].sum().reset_index()
    st.bar_chart(data=team_comparison, x="Team", y="runs", color="Team")

    # --- DETAILED STATS ---
    st.subheader("Player Leaderboard")
    st.dataframe(df.groupby(["player_name", "Team"])["runs"].sum().sort_values(ascending=False).reset_index(), use_container_width=True)
else:
    st.info("Waiting for data sync... Run your GitHub Action manually to see results.")
    
