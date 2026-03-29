import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client

# --- INITIALIZATION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key) 

# --- TEAM DEFINITIONS (Supports Overlapping Players) ---
TEAMS = {
    "Team Mandar": [
        "Shreyas Iyer", "Abhishek Sharma", "Shubman Gill", "KL Rahul", "Mitchell Marsh", 
        "Suryakumar Yadav", "Yashasvi Jaiswal", "Jos Buttler", "Philip Salt", "Finn Allen", 
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
    # One player's runs can count for multiple teams simultaneously
    team_data = []
    for _, row in df_raw.iterrows():
        p_name = row['player_name'].lower()
        for team_name, players in TEAMS.items():
            if any(p.lower() in p_name for p in players):
                team_data.append({"Team": team_name, "runs": row['runs']})
    
    df_final = pd.DataFrame(team_data)

    if not df_final.empty:
        # Group and calculate cumulative totals for the chart
        chart_data = df_final.groupby("Team")["runs"].sum().reset_index()

        # --- ALTAIR CHART WITH LABELS ---
        bars = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X("Team:N", sort="-y"),
            y=alt.Y("runs:Q", title="Total Runs"),
            color="Team:N"
        )

        text = bars.mark_text(
            align='center',
            baseline='bottom',
            dy=-5 
        ).encode(
            text='runs:Q'
        )

        st.altair_chart(bars + text, use_container_width=True)

                        # --- SEASON LEADERBOARD ---
        st.subheader("🏆 Season Leaderboard: Top 10 Performers")
        
        # 1. Group by player_name to get total runs across all matches
        player_totals = df_raw.groupby("player_name")["runs"].sum().reset_index()
        
        # 2. Function to find all teams a player belongs to
        def get_all_teams(name):
            name_low = name.lower()
            matched_teams = []
            for team_name, players in TEAMS.items():
                if any(p.lower() in name_low for p in players):
                    matched_teams.append(team_name)
            return ", ".join(matched_teams) if matched_teams else "Other"

        player_totals['Teams'] = player_totals['player_name'].apply(get_all_teams)
        
        # 3. Create the Full Leaderboard for Export (All players)
        full_leaderboard = player_totals[player_totals['Teams'] != "Other"].copy()
        full_leaderboard = full_leaderboard.sort_values(by="runs", ascending=False).reset_index(drop=True)
        full_leaderboard.index = full_leaderboard.index + 1
        full_leaderboard.columns = ["Player Name", "Total Season Runs", "Teams"]

        # 4. Create the Top 10 Display with Medals
        top_10_display = full_leaderboard.head(10).copy()
        
        def add_medals(row):
            if row.name == 1:
                return f"🥇 {row['Player Name']}"
            elif row.name == 2:
                return f"🥈 {row['Player Name']}"
            elif row.name == 3:
                return f"🥉 {row['Player Name']}"
            return row['Player Name']

        top_10_display['Player Name'] = top_10_display.apply(add_medals, axis=1)
        
        # Display the Top 10 Table
        st.table(top_10_display)

        # --- EXPORT TO XLSX ---
        st.write("---")
        
        # Convert the full dataframe to an Excel file in memory
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            full_leaderboard.to_excel(writer, index=True, sheet_name='IPL_2026_Leaderboard')
        
        st.download_button(
            label="📥 Download Full Leaderboard (XLSX)",
            data=buffer,
            file_name=f"IPL_2026_Full_Leaderboard_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
             
else:
    st.info("No data found. Ensure your GitHub Action has synced the latest match scores.")
    
