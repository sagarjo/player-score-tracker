import streamlit as st
import pandas as pd
from supabase import create_client

# --- INITIALIZATION ---
# These must be set in your Streamlit Cloud Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# [span_3](start_span)Initialize the supabase client object[span_3](end_span)
supabase = create_client(url, key) 

# [span_4](start_span)Define the Teams[span_4](end_span)
TEAM_MEET = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul"]
TEAM_PAKSHAL = ["Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"]

def get_data():
    # [span_5](start_span)[span_6](start_span)This now has access to the 'supabase' object initialized above[span_5](end_span)[span_6](end_span)
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

# [span_7](start_span)Fetch data[span_7](end_span)
try:
    df = get_data()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    df = pd.DataFrame()

if not df.empty:
    # -[span_8](start_span)-- TEAM ASSIGNMENT LOGIC ---[span_8](end_span)
    def assign_team(name):
        if any(player in name for player in TEAM_MEET):
            return "Team Meet"
        if any(player in name for player in TEAM_PAKSHAL):
            return "Team Pakshal"
        return "Other"

    df['Team'] = df['player_name'].apply(assign_team)
    
    # [span_9](start_span)Filter out 'Other' if any stray data exists[span_9](end_span)
    df = df[df['Team'] != "Other"]

    # -[span_10](start_span)-- BAR CHART: TEAM COMPARISON ---[span_10](end_span)
    st.subheader("Team Meet vs Team Pakshal")
    
    # [span_11](start_span)Group by Team and sum the runs[span_11](end_span)
    team_comparison = df.groupby("Team")["runs"].sum().reset_index()
    
    # [span_12](start_span)Display the simple bar chart[span_12](end_span)
    st.bar_chart(data=team_comparison, x="Team", y="runs", color="Team")

    # -[span_13](start_span)-- INDIVIDUAL LEADERBOARD ---[span_13](end_span)
    st.subheader("Top Performers")
    player_stats = df.groupby("player_name")["runs"].sum().sort_values(ascending=False)
    st.dataframe(player_stats, use_container_width=True)

else:
    st.info("The IPL 2026 season opener starts tonight! Check back for live data.")
    
