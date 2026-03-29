import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client

# --- INITIALIZATION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key) 

# --- TEAM DEFINITIONS ---
TEAMS = {
    "Team Mandar": [
        "Shreyas Iyer", "Abhishek Sharma", "Shubman Gill", "KL Rahul", "Mitchell Marsh", 
        "Suryakumar Yadav", "Yashasvi Jaiswal", "Jos Buttler", "Phil Salt", "Finn Allen", 
        "Dewald Brevis", "Prabhsimran Singh", "Vaibhav Sooryavanshi", "Rishabh Pant", 
        "Ayush Mhatre", "Heinrich Klaasen", "Nitish Rana", "Riyan Parag", "Shivam Dube", "Nehal Wadhera"
    ],
    "Team Meet 2": [
        "Virat Kohli", "Ishan Kishan", "Travis Head", "Sanju Samson", "Rajat Patidar", 
        "Sai Sudharsan", "Ruturaj Gaikwad", "Aiden Markram", "Nicholas Pooran", "Rohit Sharma", 
        "Quinton de Kock", "Priyansh Arya", "Tilak Varma", "Shimron Hetmyer", "Ajinkya Rahane", 
        "Pathum Nissanka", "Tristan Stubbs", "Glenn Phillips", "Dhruv Jurel", "Cameron Green"
    ],
    "Team Meet": ["Virat Kohli", "Shubman Gill", "Yashasvi Jaiswal", "Abhishek Sharma", "KL Rahul"],
    "Team Pakshal": ["Ishan Kishan", "Sanju Samson", "Shreyas Iyer", "Mitchell Marsh", "Sai Sudharsan"]
}

def get_data():
    response = supabase.table("player_runs").select("*").execute()
    return pd.DataFrame(response.data)

st.set_page_config(page_title="IPL 2026 Tracker", layout="wide")
st.title("🏏 IPL 2026: 4-Team Cumulative Standings")

try:
    df_raw = get_data()
except Exception as e:
    st.error(f"Error: {e}")
    df_raw = pd.DataFrame()

if not df_raw.empty:
    # --- OVERLAPPING SCORE LOGIC ---
    # Create a new list of records where one player run can count for multiple teams
    team_data = []
    for _, row in df_raw.iterrows():
        p_name = row['player_name'].lower()
        for team_name, players in TEAMS.items():
            if any(p.lower() in p_name for p in players):
                team_data.append({"Team": team_name, "runs": row['runs']})
    
    df_final = pd.DataFrame(team_data)

    if not df_final.empty:
        # Group and calculate cumulative totals
        chart_data = df_final.groupby("Team")["runs"].sum().reset_index()

        # --- ALTAIR CHART WITH LABELS ---
        # Base bar chart
        bars = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X("Team:N", sort="-y"),
            y=alt.Y("runs:Q", title="Total Runs"),
            color="Team:N"
        )

        # Text labels on top of bars
        text = bars.mark_text(
            align='center',
            baseline='bottom',
            dy=-5  # Nudge text up slightly
        ).encode(
            text='runs:Q'
        )

        st.altair_chart(bars + text, use_container_width=True)

        # Leaderboard
        st.subheader("Player Contributions")
        st.dataframe(df_raw.sort_values(by="runs", ascending=False), use_container_width=True)
else:
    st.info("No data found in Supabase. Run the sync script to populate scores.")
    
