import streamlit as st
import pandas as pd
from supabase import create_client

# --- INITIALIZATION ---
# These must be set in your Streamlit Cloud Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# Initialize the supabase client object BEFORE calling any data functions
supabase = create_client(url, key) 

# --- TEAM DEFINITIONS ---
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

TEAM_MEET = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul"]
TEAM_PAKSHAL = ["Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"]

st.set_page_config(page_title="IPL 2026 Tracker", page_icon="🏏")
st.title("🏏 IPL 2026 Team Standings")

def get_data():
    # Successfully uses the 'supabase' object initialized above
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

# Fetch data with error handling
try:
    df = get_data()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    df = pd.DataFrame()

if not df.empty:
    # --- UPDATED TEAM ASSIGNMENT LOGIC ---
    def assign_team(name):
        name_low = name.lower()
        # Checks all four team lists for a match
        if any(p.lower() in name_low for p in TEAM_MANDAR): return "Team Mandar"
        if any(p.lower() in name_low for p in TEAM_MEET_2): return "Team Meet 2"
        if any(p.lower() in name_low for p in TEAM_MEET): return "Team Meet"
        if any(p.lower() in name_low for p in TEAM_PAKSHAL): return "Team Pakshal"
        return "Other"

    df['Team'] = df['player_name'].apply(assign_team)
    
    # Filter out 'Other' to ensure only the four main teams appear in the graph
    df = df[df['Team'] != "Other"]

    # --- TEAM VISUALIZATION ---
    st.subheader("Team Run Comparison")
    # Group by Team and sum the runs for the cumulative total
    team_comparison = df.groupby("Team")["runs"].sum().reset_index()
    
    # Display the bar chart showing all four teams
    st.bar_chart(data=team_comparison, x="Team", y="runs", color="Team")

    # --- INDIVIDUAL LEADERBOARD ---
    st.subheader("Top Performers")
    leaderboard = df.groupby(["player_name", "Team"])["runs"].sum().sort_values(ascending=False).reset_index()
    st.dataframe(leaderboard, use_container_width=True)

else:
    st.info("No match data found. Ensure your GitHub Action has synced the latest scores.")
    
