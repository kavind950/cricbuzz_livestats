# Cricket Analytics Dashboard - Main Application Entry Point
#
# This module initializes the Streamlit application, sets up the database schema,
# loads initial cricket data from the Cricbuzz API, and configures the multi-page
# interface for cricket match tracking and analytics.
#
# Key Functions:
# - init_and_load(): Initializes database and loads sample player data
# - Loads environment configuration from .env file
# - Caches expensive operations for performance optimization

import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from utils.db_connection import get_conn, ensure_schema, seed_demo_data_if_empty
from utils.load_players import load_from_trending, load_by_ids

# Configure Streamlit page layout and branding
st.set_page_config(
    page_title="Cricket Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables from .env file for API authentication
dotenv_path = find_dotenv(usecwd=True) or (Path(__file__).resolve().parent / ".env")
load_dotenv(dotenv_path, override=False)

# Retrieve API credentials from environment or Streamlit secrets
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") or st.secrets.get("RAPIDAPI_KEY")
if RAPIDAPI_KEY:
    os.environ["RAPIDAPI_KEY"] = RAPIDAPI_KEY

@st.cache_resource(show_spinner=True)
def init_and_load():
    """
    Initialize the cricket analytics database and load initial player data.
    
    This function performs the following operations:
    1. Creates database schema (tables for players, matches, venues)
    2. Loads trending player data from project_data/trending.json
    3. Loads sample players if database is empty
    4. Caches all expensive operations for performance
    
    The function is decorated with @st.cache_resource to ensure it only runs once 
    per Streamlit session, improving application startup performance.
    """
    ensure_schema()
    try:
        seed_demo_data_if_empty(force=False)
    except Exception as e:
        print(f"[seed] skipped: {e}")

    trending_path = Path("project_data") / "trending.json"
    if trending_path.exists():
        try:
            with open(trending_path, "r", encoding="utf-8") as f:
                trending = json.load(f)
        except Exception as e:
            print(f"[trending load] file read failed: {e}")
            trending = []
    else:
        trending = []

    try:
        if trending:
            load_from_trending(trending, max_players=6)
    except Exception as e:
        print(f"[trending load] failed: {e}")

    try:
        conn = get_conn()
        n_runs = int(pd.read_sql(
            "SELECT COUNT(*) AS n FROM players WHERE COALESCE(total_runs,0) > 0", conn).iloc[0, 0])
        n_wkts = int(pd.read_sql(
            "SELECT COUNT(*) AS n FROM players WHERE COALESCE(total_wickets,0) > 0", conn).iloc[0, 0])
    except Exception:
        ensure_schema()
        conn = get_conn()
        n_runs = int(pd.read_sql(
            "SELECT COUNT(*) AS n FROM players WHERE COALESCE(total_runs,0) > 0", conn).iloc[0, 0])
        n_wkts = int(pd.read_sql(
            "SELECT COUNT(*) AS n FROM players WHERE COALESCE(total_wickets,0) > 0", conn).iloc[0, 0])

    if n_runs == 0 and n_wkts == 0:
        try:
            load_by_ids([
                ("8733",  "KL Rahul",        "India"),
                ("2258",  "Jos Buttler",     "England"),
                ("10738", "Rashid Khan",     "Afghanistan"),
                ("7825",  "Faf du Plessis",  "South Africa"),
            ])
        except Exception as e:
            print(f"[load_by_ids] failed: {e}")

init_and_load()

if not RAPIDAPI_KEY:
    st.error("RAPIDAPI_KEY is not set in your environment (.env) or st.secrets.")

st.title("🏏 Cricbuzz LiveStats")
st.markdown("""
Welcome! 🎉

Use the **sidebar** to explore:
- 📘 Project Overview-- Home 
- 📡 Live Matches  
- 📊 Top Stats  
- 🗄️ SQL Queries  
- 🛠️ CRUD Operations  

---
""")
st.success("✅ Setup Complete. Select a page from the sidebar to continue.")
