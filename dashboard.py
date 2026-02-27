import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Real Madrid Analytics", page_icon="⚽", layout="wide")
st.title("⚽ Real Madrid 2023 Season Explorer")
st.write("Explore match results, goals, and trends from the 2023 season.")

@st.cache_data
def get_match_data():
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"team": "541", "season": "2023"}
    # KEEP YOUR KEY HERE FOR NOW to test locally
    headers = {"x-apisports-key": st.secrets["API_KEY"]}
    
    response = requests.get(url, headers=headers, params=querystring)
    matches = response.json()['response']
    
    clean_data = []
    for match in matches:
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']
        
        # Feature Engineering: Figure out exactly which goals belong to Real Madrid
        if home_team == 'Real Madrid':
            rm_goals = home_goals
            opp_goals = away_goals
        else:
            rm_goals = away_goals
            opp_goals = home_goals
            
        # Only add finished games (where goals aren't 'None')
        if rm_goals is not None:
            clean_data.append({
                "Date": match['fixture']['date'][:10],
                "Venue": "Home" if home_team == 'Real Madrid' else "Away",
                "Opponent": away_team if home_team == 'Real Madrid' else home_team,
                "Real Madrid Goals": rm_goals,
                "Opponent Goals": opp_goals
            })
            
    return pd.DataFrame(clean_data)

df = get_match_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")
match_type = st.sidebar.radio("View Games:", ["All Games", "Home", "Away"])

if match_type == "Home":
    display_df = df[df['Venue'] == 'Home']
elif match_type == "Away":
    display_df = df[df['Venue'] == 'Away']
else:
    display_df = df

# --- KPI METRIC CARDS (The Recruiter Eye-Catcher) ---
st.subheader("Season Overview")
col1, col2, col3, col4 = st.columns(4)

total_games = len(display_df)
total_rm_goals = display_df['Real Madrid Goals'].sum()
total_opp_goals = display_df['Opponent Goals'].sum()
goal_difference = total_rm_goals - total_opp_goals

col1.metric("Matches Played", total_games)
col2.metric("Goals Scored", int(total_rm_goals))
col3.metric("Goals Conceded", int(total_opp_goals))
col4.metric("Goal Difference", int(goal_difference))

st.divider() # Adds a nice visual line

# --- INTERACTIVE CHART ---
st.subheader("Goals Scored per Match")
fig = px.bar(
    display_df, 
    x='Date', 
    y='Real Madrid Goals', 
    hover_data=['Opponent', 'Venue', 'Opponent Goals'], 
    color_discrete_sequence=['#00529F'],
    labels={'Real Madrid Goals': 'Goals Scored'}
)
st.plotly_chart(fig, use_container_width=True)

# --- RAW DATA ---
st.subheader("Match Database")

st.dataframe(display_df, use_container_width=True)
