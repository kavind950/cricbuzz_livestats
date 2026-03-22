import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
from utils.live_data_manager import LiveMatchesRefresh

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

# Initialize session state for live refresh
if 'live_matches_last_update' not in st.session_state:
    st.session_state.live_matches_last_update = datetime.now()

if 'live_matches_auto_refresh' not in st.session_state:
    st.session_state.live_matches_auto_refresh = True

if 'live_matches_refresh_interval' not in st.session_state:
    st.session_state.live_matches_refresh_interval = 5  # seconds

if 'live_matches_manual_refresh' not in st.session_state:
    st.session_state.live_matches_manual_refresh = False  # Track manual refresh clicks

def show_live_matches():
    """Display live cricket matches from Cricbuzz API with auto-refresh."""
    
    st.header("📺 Live Matches - REAL-TIME UPDATES")
    
    st.write("✨ Live cricket matches with automatic real-time updates every few seconds.")
    
    # API Configuration Warning
    if not API_KEY or API_KEY == "your_api_key_here":
        st.warning("⚠️ API Key not configured. Please set RAPIDAPI_KEY in environment variables.")
        st.info("Get your API key from: https://rapidapi.com/api-sports/api/cricbuzz-cricket")
        return
    
    # CRITICAL: Check auto-refresh FIRST (before display)
    # Only update timestamp if auto-refresh is enabled AND it's not a manual refresh
    if st.session_state.live_matches_auto_refresh and not st.session_state.live_matches_manual_refresh:
        time_since_refresh = (datetime.now() - st.session_state.live_matches_last_update).total_seconds()
        if time_since_refresh >= st.session_state.live_matches_refresh_interval:
            # Update timestamp IMMEDIATELY
            st.session_state.live_matches_last_update = datetime.now()
            st.rerun()
    else:
        # Reset manual refresh flag after this run
        st.session_state.live_matches_manual_refresh = False
    
    # Display refresh controls (NOW shows updated time)
    LiveMatchesRefresh.display_live_refresh_header()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔴 Live Matches", "⏱️ Upcoming Matches", "📊 Match Details"])
    
    with tab1:
        show_live_matches_tab()
    
    with tab2:
        show_upcoming_matches_tab()
    
    with tab3:
        show_match_details_tab()


def fetch_live_matches():
    """Fetch live matches from Cricbuzz API."""
    try:
        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": API_HOST
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None


def parse_live_matches(data):
    """Parse live matches data from API response."""
    matches = []
    
    if not data:
        return matches
    
    try:
        for match_type in data.get("typeMatches", []):
            match_type_name = match_type.get("matchType", "N/A")
            
            for series in match_type.get("seriesMatches", []):
                series_data = series.get("seriesAdWrapper", {})
                series_name = series_data.get("seriesName", "N/A")
                
                for match in series_data.get("matches", []):
                    try:
                        match_info = match.get("matchInfo", {})
                        match_score = match.get("matchScore", {})
                        
                        team1 = match_info.get("team1", {})
                        team2 = match_info.get("team2", {})
                        
                        team1_score = match_score.get("team1Score", {})
                        team2_score = match_score.get("team2Score", {})
                        
                        matches.append({
                            "Match ID": match_info.get("matchId", "N/A"),
                            "Series": series_name,
                            "Format": match_type_name,
                            "Team 1": team1.get("teamName", "N/A"),
                            "Team 2": team2.get("teamName", "N/A"),
                            "Venue": match_info.get("venue", {}).get("name", "N/A"),
                            "Status": match_info.get("status", "N/A"),
                            "Team 1 Score": team1_score.get("scoreFullDetails", {}).get("runs", "N/A"),
                            "Team 2 Score": team2_score.get("scoreFullDetails", {}).get("runs", "N/A")
                        })
                    except Exception as e:
                        continue
                        
    except Exception as e:
        st.error(f"❌ Error parsing matches: {e}")
    
    return matches


def show_live_matches_tab():
    """Display live matches tab."""
    
    st.subheader("Currently Live Matches")
    
    if st.button("🔄 Refresh Live Matches", key="refresh_live"):
        st.rerun()
    
    # Show countdown to next auto-refresh
    if st.session_state.live_matches_auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.live_matches_last_update).total_seconds()
        time_left = st.session_state.live_matches_refresh_interval - time_since_refresh
        if time_left > 0:
            st.info(f"⏱️ Next auto-refresh in {int(time_left)}s...")
        time.sleep(1)  # Small delay between checks
    
    with st.spinner("Fetching live matches..."):
        data = fetch_live_matches()
    
    if not data:
        st.warning("No data received from API")
        return
    
    matches = parse_live_matches(data)
    
    if not matches:
        st.info("📭 No live matches at the moment")
        return
    
    # Display matches in columns
    for idx, match in enumerate(matches[:3]):  # Show top 3 matches
        with st.container():
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.write(f"**{match['Team 1']}**")
                st.write(f"Score: {match['Team 1 Score']}")
            
            with col2:
                st.write(f"**{match['Series']}**")
                st.write(f"Format: {match['Format']}")
                st.write(f"Status: {match['Status']}")
                st.write(f"Venue: {match['Venue']}")
            
            with col3:
                st.write(f"**{match['Team 2']}**")
                st.write(f"Score: {match['Team 2 Score']}")
    
    # Display all matches in table format
    st.subheader("All Live Matches")
    
    if matches:
        df = pd.DataFrame(matches)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No live matches available")


def format_timestamp(timestamp):
    """Convert Unix timestamp (milliseconds) to readable date format."""
    try:
        # Handle None or "N/A"
        if timestamp is None or timestamp == "N/A":
            return "N/A"
        
        # Convert to float (handles both int, float, and string)
        timestamp_val = float(timestamp)
        
        # Convert milliseconds to seconds
        timestamp_sec = timestamp_val / 1000
        
        # Format to readable date
        formatted_date = datetime.fromtimestamp(timestamp_sec).strftime("%d %b %Y, %I:%M %p")
        return formatted_date
    except (ValueError, TypeError, OSError):
        return "N/A"


def show_upcoming_matches_tab():
    """Display upcoming matches tab."""
    
    st.subheader("Upcoming Matches")
    
    try:
        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": API_HOST
        }
        
        with st.spinner("Fetching upcoming matches..."):
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        
        matches = []
        
        for match_type in data.get("typeMatches", []):
            match_type_name = match_type.get("matchType", "N/A")
            
            for series in match_type.get("seriesMatches", []):
                series_data = series.get("seriesAdWrapper", {})
                series_name = series_data.get("seriesName", "N/A")
                
                for match in series_data.get("matches", [])[:5]:  # Limit to 5 matches per series
                    match_info = match.get("matchInfo", {})
                    
                    # Format the timestamp
                    raw_date = match_info.get("startDate", "N/A")
                    formatted_date = format_timestamp(raw_date)
                    
                    matches.append({
                        "Series": series_name,
                        "Format": match_type_name,
                        "Team 1": match_info.get("team1", {}).get("teamName", "N/A"),
                        "Team 2": match_info.get("team2", {}).get("teamName", "N/A"),
                        "Venue": match_info.get("venue", {}).get("name", "N/A"),
                        "Date": formatted_date
                    })
        
        if matches:
            df = pd.DataFrame(matches)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming matches available")
            
    except Exception as e:
        st.error(f"❌ Error fetching upcoming matches: {e}")


def show_match_details_tab():
    """Display detailed match information."""
    
    st.subheader("Match Details & Statistics")
    
    st.info("📌 Select a live match to view detailed scorecard, player statistics, and match summary.")
    
    # Fetch recent matches for selection
    with st.spinner("Fetching match data..."):
        data = fetch_live_matches()
    
    if not data:
        st.warning("Unable to fetch match data")
        return
    
    matches = parse_live_matches(data)
    
    if not matches:
        st.info("No matches available for detailed view")
        return
    
    # Create match selector
    match_labels = [f"{m['Team 1']} vs {m['Team 2']} ({m['Venue']})" for m in matches]
    
    if match_labels:
        selected_idx = st.selectbox("Select a match to view details:", range(len(match_labels)), 
                                   format_func=lambda x: match_labels[x])
        
        selected_match = matches[selected_idx]
        
        # Display detailed match information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Team 1", selected_match['Team 1'], selected_match['Team 1 Score'])
        
        with col2:
            st.metric("Format", selected_match['Format'])
        
        with col3:
            st.metric("Team 2", selected_match['Team 2'], selected_match['Team 2 Score'])
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Series:** {selected_match['Series']}")
            st.write(f"**Venue:** {selected_match['Venue']}")
        
        with col2:
            st.write(f"**Match Status:** {selected_match['Status']}")
            st.write(f"**Match ID:** {selected_match['Match ID']}")
        
        st.divider()
        
        st.write("📋 **Match Summary**")
        st.info(f"{selected_match['Team 1']} scored {selected_match['Team 1 Score']} runs | "
               f"{selected_match['Team 2']} scored {selected_match['Team 2 Score']} runs")
    
    # API Documentation Link
    st.divider()
    st.write("For more match details, visit: [Cricbuzz Cricket API Docs](https://rapidapi.com/api-sports/api/cricbuzz-cricket)")