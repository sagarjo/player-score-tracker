import streamlit as st
import pandas as pd
from supabase import create_client

# ... (Your existing Supabase connection code) ...

# Define the Teams
TEAM_MEET = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul"]
TEAM_PAKSHAL = ["Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"]

def get_data():
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

df = get_data()

if not df.empty:
    # --- TEAM ASSIGNMENT LOGIC ---
    def assign_team(name):
        if any(player in name for player in TEAM_MEET):
            return "Team Meet"
        if any(player in name for player in TEAM_PAKSHAL):
            return "Team Pakshal"
        return "Other"

    df['Team'] = df['player_name'].apply(assign_team)
    
    # Filter out 'Other' if any stray data exists
    df = df[df['Team'] != "Other"]

    # --- BAR CHART: TEAM COMPARISON ---
    st.subheader("Team Meet vs Team Pakshal")
    
    # Group by Team and sum the runs
    team_comparison = df.groupby("Team")["runs"].sum().reset_index()
    
    # Display the simple bar chart
    st.bar_chart(data=team_comparison, x="Team", y="runs", color="Team")

    # --- INDIVIDUAL LEADERBOARD ---
    st.subheader("Top Performers")
    player_stats = df.groupby("player_name")["runs"].sum().sort_values(ascending=False)
    st.dataframe(player_stats, use_container_width=True)

else:
    st.info("The IPL 2026 season opener starts tonight! Check back at 7:30 PM IST for live data.")
  
