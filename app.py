import streamlit as st
import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-fetch live data on app startup
@st.cache_resource
def fetch_live_data_on_startup():
    """
    Automatically fetch live data from Cricbuzz API when app starts.
    This ensures the database is always up-to-date with latest cricket matches.
    Uses caching to avoid fetching multiple times per Streamlit session.
    """
    try:
        # Get the directory of this script
        script_dir = Path(__file__).parent
        fetch_script = script_dir / "utils" / "fetch_live_data.py"
        
        # Check if API key is configured
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            print("⚠️ RAPIDAPI_KEY not configured. Skipping live data fetch.")
            return False
        
        # Only fetch if fetch script exists
        if fetch_script.exists():
            try:
                # Run fetch_live_data.py silently
                result = subprocess.run(
                    ["python", str(fetch_script)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅ Live data fetched successfully")
                    return True
                else:
                    # Silently log errors, don't block app startup
                    print(f"⚠️ Data fetch returned: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("⚠️ Data fetch timeout (>30s) - continuing with existing data")
                return False
            except Exception as e:
                print(f"⚠️ Data fetch error: {e}")
                return False
        else:
            print("⚠️ fetch_live_data.py script not found")
            return False
    except Exception as e:
        print(f"⚠️ Startup initialization error: {e}")
        return False

# Trigger data fetch
fetch_live_data_on_startup()

# Initialize session state for live updates
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now()

if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = True

if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 5  # seconds

st.title("🏏 Cricbuzz LiveStats")

st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", [
    "Home",
    "Live Matches",
    "Top Stats",
    "SQL Queries",
    "CRUD Operations"
])

if page == "Home":
    from pages.home import show_home
    show_home()

elif page == "Live Matches":
    from pages.live_matches import show_live_matches
    show_live_matches()

elif page == "Top Stats":
    from pages.top_stats import show_top_stats
    show_top_stats()

elif page == "SQL Queries":
    from pages.sql_queries import show_sql_queries
    show_sql_queries()

elif page == "CRUD Operations":
    from pages.crud_operations import show_crud
    show_crud()