import streamlit as st
import pandas as pd
from supabase import create_client

# --- SECRETS & SETUP ---
# In Streamlit Cloud, add these to "Advanced Settings > Secrets"
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

TRACKED_PLAYERS = ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", 
                   "KL Rahul", "Ishan Kishan", "Sanju Samson", "Shreyas Iyer", 
                   "Mitchell Marsh", "Sai Sudharsan"]

st.set_page_config(page_title="IPL 2026 Tracker", page_icon="🏏")
st.title("🏏 IPL 2026 Player Run Tracker")

# --- DATA FETCHING ---
def get_data():
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

df = get_data()

if not df.empty:
    # 1. Total Runs Leaderboard
    st.subheader("Leaderboard (Total Runs)")
    leaderboard = df.groupby("player_name")["runs"].sum().sort_values(ascending=False)
    st.bar_chart(leaderboard)

    # 2. Detailed Match-wise Table
    st.subheader("Match-by-Match Breakdown")
    pivot_df = df.pivot(index="player_name", columns="match_id", values="runs").fillna(0)
    st.dataframe(pivot_df, use_container_width=True)
else:
    st.info("No data recorded yet. Waiting for first match update!")
  
