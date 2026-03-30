# Player Performance Leaderboards - Cricket Analytics Dashboard
#
# This module displays comprehensive player statistics and rankings across
# multiple performance categories including batting averages, strike rates,
# total runs, and bowling figures. 
#
# Features:
# - Dynamic leaderboards sorted by various metrics
# - Country and role-based filtering
# - Interactive charts and visualizations
# - Comparison capabilities between players
# - Historical performance trends
#
# The page queries the local SQLite database for all statistics calculations.

import os
import sys
import glob
import sqlite3
from datetime import datetime

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

# ---------- Database Connection Import with Fallback ----------
# Handles various project structure configurations for import reliability
_DB_IMPORTED = False
try:
    ROOT_CANDIDATES = [
        os.getcwd(),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # project/
        os.path.dirname(os.path.abspath(__file__)),                   # project/pages
    ]
    for path in ROOT_CANDIDATES:
        if path and path not in sys.path:
            sys.path.append(path)

    from utils.db_connection import DatabaseConnection as _UserDatabaseConnection  # type: ignore
    _DB_IMPORTED = True
except Exception:
    _DB_IMPORTED = False


def _find_db_file() -> str | None:
    candidates = [
        os.path.join(os.getcwd(), "cricket.db"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cricket.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cricket.db"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "cricket.db"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        matches = glob.glob(os.path.join(project_root, "**", "cricket.db"), recursive=True)
        if matches:
            return matches[0]
    except Exception:
        pass
    return None


class _FallbackDatabaseConnection:
    """SQLite fallback with the same interface expected by the page."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or _find_db_file()
        if not self.db_path:
            raise FileNotFoundError(
                "Could not locate 'cricket.db'. Place it in the project root or 'utils/'."
            )

    def execute_query(self, sql: str, params: tuple | list | None = None) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(sql, conn, params=params or ())


if _DB_IMPORTED:
    DatabaseConnection = _UserDatabaseConnection  # type: ignore
else:
    DatabaseConnection = _FallbackDatabaseConnection  # type: ignore


# =============================================================================
# Page entry
# =============================================================================
def show_top_stats(api_key: str | None):
    st.markdown("# 🏆 Top Player Statistics")
    st.markdown("Comprehensive player statistics and leaderboards")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏏 Batting Stats", "⚾ Bowling Stats", "🔄 All-rounders", "📊 Database Stats"]
    )

    with tab1:
        show_batting_stats(api_key)
    with tab2:
        show_bowling_stats(api_key)
    with tab3:
        show_allrounder_stats(api_key)
    with tab4:
        show_database_stats()


# ------------------------ Batting ------------------------
def show_batting_stats(api_key: str | None):
    st.markdown("## 🏏 Top Batting Performances")
    format_options = ["Test", "ODI", "T20I", "All Formats"]
    selected_format = st.selectbox("Select Format", format_options, key="batting_format")

    if api_key:
        try:
            with st.spinner("Fetching batting statistics..."):
                batting_data = fetch_batting_stats_api(api_key, selected_format)
                if batting_data:
                    display_batting_leaderboards(batting_data, selected_format)
                else:
                    display_sample_batting_stats(selected_format)
        except Exception as e:
            st.error(f"Error fetching API data: {e}")
            display_sample_batting_stats(selected_format)
    else:
        st.info("🔑 Enter API key to view live statistics")
        display_sample_batting_stats(selected_format)


# ------------------------ Bowling ------------------------
def show_bowling_stats(api_key: str | None):
    st.markdown("## ⚾ Top Bowling Performances")
    format_options = ["Test", "ODI", "T20I", "All Formats"]
    selected_format = st.selectbox("Select Format", format_options, key="bowling_format")

    if api_key:
        try:
            with st.spinner("Fetching bowling statistics..."):
                bowling_data = fetch_bowling_stats_api(api_key, selected_format)
                if bowling_data:
                    display_bowling_leaderboards(bowling_data, selected_format)
                else:
                    display_sample_bowling_stats(selected_format)
        except Exception as e:
            st.error(f"Error fetching API data: {e}")
            display_sample_bowling_stats(selected_format)
    else:
        st.info("🔑 Enter API key to view live statistics")
        display_sample_bowling_stats(selected_format)


# ---------------------- All-rounders ---------------------
def show_allrounder_stats(api_key: str | None):
    st.markdown("## 🔄 Top All-rounders")
    st.markdown(
        """
        **All-rounder Criteria:**
        - Minimum 1000 runs scored
        - Minimum 50 wickets taken
        - Active in international cricket
        """
    )

    if api_key:
        try:
            with st.spinner("Fetching all-rounder statistics..."):
                allrounder_data = fetch_allrounder_stats_api(api_key)
                if allrounder_data:
                    display_allrounder_analysis(allrounder_data)
                else:
                    display_sample_allrounder_stats()
        except Exception as e:
            st.error(f"Error fetching API data: {e}")
            display_sample_allrounder_stats()
    else:
        st.info("🔑 Enter API key to view live statistics")
        display_sample_allrounder_stats()


# ------------------------ Database -----------------------
def show_database_stats():
    st.markdown("## 📊 Database Statistics")
    try:
        db = DatabaseConnection()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏏 Top Run Scorers (Database)")
            batting_query = """
                SELECT name, country, total_runs, batting_average, strike_rate
                FROM players 
                WHERE total_runs > 0
                ORDER BY total_runs DESC 
                LIMIT 10
            """
            batting_data = db.execute_query(batting_query)
            if not batting_data.empty:
                st.dataframe(batting_data, use_container_width=True)
                fig_runs = px.bar(
                    batting_data.head(8),
                    x="name",
                    y="total_runs",
                    color="batting_average",
                    title="Top 8 Run Scorers",
                    labels={"name": "Player", "total_runs": "Total Runs"},
                    color_continuous_scale="viridis",
                )
                fig_runs.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_runs, use_container_width=True)
            else:
                st.info("No batting rows in 'players' table.")

        with col2:
            st.markdown("### ⚾ Top Wicket Takers (Database)")
            bowling_query = """
                SELECT name, country, total_wickets, bowling_average, economy_rate
                FROM players 
                WHERE total_wickets > 0
                ORDER BY total_wickets DESC 
                LIMIT 10
            """
            bowling_data = db.execute_query(bowling_query)
            if not bowling_data.empty:
                st.dataframe(bowling_data, use_container_width=True)
                fig_wickets = px.bar(
                    bowling_data.head(8),
                    x="name",
                    y="total_wickets",
                    color="bowling_average",
                    title="Top 8 Wicket Takers",
                    labels={"name": "Player", "total_wickets": "Total Wickets"},
                    color_continuous_scale="plasma",
                )
                fig_wickets.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_wickets, use_container_width=True)
            else:
                st.info("No bowling rows in 'players' table.")

        # Country-wise analysis
        st.markdown("### 🌍 Country-wise Performance Analysis")
        country_stats_query = """
            SELECT 
                country,
                COUNT(*) as total_players,
                AVG(batting_average) as avg_batting_avg,
                AVG(bowling_average) as avg_bowling_avg,
                SUM(total_runs) as total_country_runs,
                SUM(total_wickets) as total_country_wickets
            FROM players 
            WHERE country IS NOT NULL
            GROUP BY country
            HAVING total_players >= 2
            ORDER BY total_country_runs DESC
        """
        country_data = db.execute_query(country_stats_query)
        if not country_data.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig_country_runs = px.pie(
                    country_data.head(10),
                    values="total_country_runs",
                    names="country",
                    title="Total Runs by Country",
                )
                st.plotly_chart(fig_country_runs, use_container_width=True)
            with c2:
                fig_country_avg = px.bar(
                    country_data.head(10),
                    x="country",
                    y="avg_batting_avg",
                    title="Average Batting Average by Country",
                    color="avg_batting_avg",
                    color_continuous_scale="blues",
                )
                fig_country_avg.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_country_avg, use_container_width=True)

            st.markdown("### 📋 Country Statistics Summary")
            st.dataframe(country_data.round(2), use_container_width=True)
        else:
            st.info("No country-level rows in 'players' table.")

        # Role distribution
        st.markdown("### 🎯 Playing Role Distribution")
        role_query = """
            SELECT 
                playing_role,
                COUNT(*) as player_count,
                AVG(batting_average) as avg_batting,
                AVG(bowling_average) as avg_bowling,
                AVG(strike_rate) as avg_strike_rate
            FROM players 
            WHERE playing_role IS NOT NULL
            GROUP BY playing_role
            ORDER BY player_count DESC
        """
        role_data = db.execute_query(role_query)
        if not role_data.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig_roles = px.pie(
                    role_data,
                    values="player_count",
                    names="playing_role",
                    title="Player Distribution by Role",
                )
                st.plotly_chart(fig_roles, use_container_width=True)
            with c2:
                st.dataframe(role_data.round(2), use_container_width=True)
        else:
            st.info("No role-level rows in 'players' table.")

    except FileNotFoundError as e:
        st.error(str(e))
        st.info("Tip: put 'cricket.db' in your project root or in 'utils/'.")
    except Exception as e:
        st.error(f"Error loading database statistics: {e}")


# =============================================================================
# API calls (sample endpoints; schema may vary by plan)
# =============================================================================
def fetch_batting_stats_api(api_key: str, format_type: str):
    base_url = "https://cricbuzz-cricket.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"}
    try:
        r = requests.get(f"{base_url}/stats/v1/rankings/batsmen", headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def fetch_bowling_stats_api(api_key: str, format_type: str):
    base_url = "https://cricbuzz-cricket.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"}
    try:
        r = requests.get(f"{base_url}/stats/v1/rankings/bowlers", headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def fetch_allrounder_stats_api(api_key: str):
    base_url = "https://cricbuzz-cricket.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"}
    try:
        r = requests.get(f"{base_url}/stats/v1/rankings/allrounders", headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


# =============================================================================
# Render helpers for live API (stub until you wire exact schema)
# =============================================================================
def display_batting_leaderboards(data, format_type: str):
    st.success(f"📊 Live {format_type} Batting Statistics")
    st.info("API data processing is schema-dependent. Wire it up once you confirm the JSON shape.")


def display_bowling_leaderboards(data, format_type: str):
    st.success(f"📊 Live {format_type} Bowling Statistics")
    st.info("API data processing is schema-dependent. Wire it up once you confirm the JSON shape.")


def display_allrounder_analysis(data):
    st.success("📊 Live All-rounder Statistics")
    st.info("API data processing is schema-dependent. Wire it up once you confirm the JSON shape.")


# =============================================================================
# Sample fallbacks
# =============================================================================
def display_sample_batting_stats(format_type: str):
    st.info(f"📝 Sample {format_type} Batting Statistics (Live data requires API key)")
    sample_batting = {
        "Test": [
            {"Player": "Steve Smith", "Country": "Australia", "Runs": 8647, "Average": 61.8, "Strike Rate": 86.4, "Centuries": 27},
            {"Player": "Kane Williamson", "Country": "New Zealand", "Runs": 7368, "Average": 54.0, "Strike Rate": 81.2, "Centuries": 24},
            {"Player": "Virat Kohli", "Country": "India", "Runs": 8043, "Average": 50.4, "Strike Rate": 92.5, "Centuries": 27},
            {"Player": "Joe Root", "Country": "England", "Runs": 9460, "Average": 49.8, "Strike Rate": 89.1, "Centuries": 26},
            {"Player": "Babar Azam", "Country": "Pakistan", "Runs": 3596, "Average": 45.7, "Strike Rate": 89.7, "Centuries": 9},
        ],
        "ODI": [
            {"Player": "Virat Kohli", "Country": "India", "Runs": 12898, "Average": 58.1, "Strike Rate": 93.2, "Centuries": 46},
            {"Player": "Rohit Sharma", "Country": "India", "Runs": 9825, "Average": 48.9, "Strike Rate": 88.9, "Centuries": 30},
            {"Player": "David Warner", "Country": "Australia", "Runs": 5455, "Average": 44.7, "Strike Rate": 95.4, "Centuries": 18},
            {"Player": "Babar Azam", "Country": "Pakistan", "Runs": 4442, "Average": 59.2, "Strike Rate": 89.7, "Centuries": 17},
            {"Player": "Quinton de Kock", "Country": "South Africa", "Runs": 5431, "Average": 44.7, "Strike Rate": 95.1, "Centuries": 17},
        ],
        "T20I": [
            {"Player": "Babar Azam", "Country": "Pakistan", "Runs": 3485, "Average": 41.6, "Strike Rate": 129.2, "Centuries": 3},
            {"Player": "Mohammad Rizwan", "Country": "Pakistan", "Runs": 2607, "Average": 47.4, "Strike Rate": 127.2, "Centuries": 1},
            {"Player": "Suryakumar Yadav", "Country": "India", "Runs": 1675, "Average": 46.5, "Strike Rate": 175.2, "Centuries": 4},
            {"Player": "Jos Buttler", "Country": "England", "Runs": 2140, "Average": 35.0, "Strike Rate": 144.9, "Centuries": 1},
            {"Player": "Aaron Finch", "Country": "Australia", "Runs": 3120, "Average": 34.3, "Strike Rate": 142.5, "Centuries": 2},
        ],
    }
    df = (
        pd.DataFrame([dict(p, **{"Format": fmt}) for fmt, players in sample_batting.items() for p in players])
        if format_type == "All Formats"
        else pd.DataFrame(sample_batting.get(format_type, sample_batting["ODI"]))
    )
    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_scatter = px.scatter(
            df.head(10),
            x="Average",
            y="Runs",
            size="Centuries",
            color="Strike Rate",
            hover_name="Player",
            title=f"{format_type} - Runs vs Average",
            color_continuous_scale="viridis",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        fig_bar = px.bar(
            df.head(8),
            x="Player",
            y="Runs",
            color="Average",
            title=f"Top 8 Run Scorers - {format_type}",
            color_continuous_scale="blues",
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)


def display_sample_bowling_stats(format_type: str):
    st.info(f"📝 Sample {format_type} Bowling Statistics (Live data requires API key)")
    sample_bowling = {
        "Test": [
            {"Player": "Pat Cummins", "Country": "Australia", "Wickets": 269, "Average": 23.4, "Economy": 3.2, "Strike Rate": 43.8},
            {"Player": "Jasprit Bumrah", "Country": "India", "Wickets": 159, "Average": 20.2, "Economy": 2.7, "Strike Rate": 44.8},
            {"Player": "Kagiso Rabada", "Country": "South Africa", "Wickets": 270, "Average": 22.9, "Economy": 3.6, "Strike Rate": 38.1},
            {"Player": "Josh Hazlewood", "Country": "Australia", "Wickets": 236, "Average": 25.3, "Economy": 2.9, "Strike Rate": 52.3},
            {"Player": "Tim Southee", "Country": "New Zealand", "Wickets": 385, "Average": 28.9, "Economy": 3.2, "Strike Rate": 54.1},
        ],
        "ODI": [
            {"Player": "Trent Boult", "Country": "New Zealand", "Wickets": 169, "Average": 25.9, "Economy": 4.8, "Strike Rate": 32.4},
            {"Player": "Josh Hazlewood", "Country": "Australia", "Wickets": 100, "Average": 24.6, "Economy": 4.1, "Strike Rate": 36.0},
            {"Player": "Jasprit Bumrah", "Country": "India", "Wickets": 132, "Average": 24.4, "Economy": 4.6, "Strike Rate": 31.8},
            {"Player": "Mujeeb Ur Rahman", "Country": "Afghanistan", "Wickets": 120, "Average": 21.4, "Economy": 4.2, "Strike Rate": 30.5},
            {"Player": "Shaheen Afridi", "Country": "Pakistan", "Wickets": 89, "Average": 23.1, "Economy": 5.2, "Strike Rate": 26.6},
        ],
        "T20I": [
            {"Player": "Rashid Khan", "Country": "Afghanistan", "Wickets": 140, "Average": 13.2, "Economy": 6.2, "Strike Rate": 12.8},
            {"Player": "Shaheen Afridi", "Country": "Pakistan", "Wickets": 97, "Average": 18.7, "Economy": 7.3, "Strike Rate": 15.4},
            {"Player": "Adil Rashid", "Country": "England", "Wickets": 108, "Average": 23.4, "Economy": 7.6, "Strike Rate": 18.5},
            {"Player": "Wanindu Hasaranga", "Country": "Sri Lanka", "Wickets": 91, "Average": 15.4, "Economy": 6.4, "Strike Rate": 14.4},
            {"Player": "Josh Hazlewood", "Country": "Australia", "Wickets": 63, "Average": 20.9, "Economy": 7.3, "Strike Rate": 17.2},
        ],
    }
    df = (
        pd.DataFrame([dict(p, **{"Format": fmt}) for fmt, players in sample_bowling.items() for p in players])
        if format_type == "All Formats"
        else pd.DataFrame(sample_bowling.get(format_type, sample_bowling["ODI"]))
    )
    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_scatter = px.scatter(
            df.head(10),
            x="Average",
            y="Wickets",
            size="Strike Rate",
            color="Economy",
            hover_name="Player",
            title=f"{format_type} - Wickets vs Average",
            color_continuous_scale="plasma",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        fig_bar = px.bar(
            df.head(8),
            x="Player",
            y="Wickets",
            color="Average",
            title=f"Top 8 Wicket Takers - {format_type}",
            color_continuous_scale="reds",
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)


def display_sample_allrounder_stats():
    st.info("📝 Sample All-rounder Statistics (Live data requires API key)")
    sample_allrounders = [
        {"Player": "Ben Stokes", "Country": "England", "Runs": 5061, "Bat Avg": 35.8, "Wickets": 197, "Bowl Avg": 31.2, "Points": 428},
        {"Player": "Ravindra Jadeja", "Country": "India", "Runs": 3897, "Bat Avg": 35.2, "Wickets": 294, "Bowl Avg": 24.8, "Points": 425},
        {"Player": "Jason Holder", "Country": "West Indies", "Runs": 2650, "Bat Avg": 33.1, "Wickets": 145, "Bowl Avg": 27.9, "Points": 378},
        {"Player": "Shakib Al Hasan", "Country": "Bangladesh", "Runs": 4201, "Bat Avg": 38.9, "Wickets": 230, "Bowl Avg": 31.1, "Points": 405},
        {"Player": "Pat Cummins", "Country": "Australia", "Runs": 1045, "Bat Avg": 22.1, "Wickets": 269, "Bowl Avg": 23.4, "Points": 352},
    ]
    df = pd.DataFrame(sample_allrounders)
    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_scatter = px.scatter(
            df,
            x="Bat Avg",
            y="Bowl Avg",
            size="Points",
            color="Points",
            hover_name="Player",
            title="All-rounder Performance Matrix",
            labels={"Bat Avg": "Batting Average", "Bowl Avg": "Bowling Average"},
            color_continuous_scale="viridis",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        fig_bar = px.bar(
            df.sort_values("Points", ascending=True),
            x="Points",
            y="Player",
            orientation="h",
            title="All-rounder Rankings",
            color="Points",
            color_continuous_scale="blues",
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# =============================================================================
# Call the page entry so Streamlit renders content
# =============================================================================
def _read_api_key() -> str | None:
    # 1) Prefer environment (.env already loaded via load_dotenv)
    key = os.getenv("RAPIDAPI_KEY")
    if key and key.strip():
        return key.strip()

    # 2) Fall back to Streamlit Cloud / local secrets if present
    try:
        # Using [] avoids creating a .get() call that still parses; the try guards the parse error.
        key = st.secrets["RAPIDAPI_KEY"]
        return key.strip() if isinstance(key, str) and key.strip() else None
    except Exception:
        return None


# Streamlit executes this file top-to-bottom; call the renderer:
api_key__ = _read_api_key()
show_top_stats(api_key__)
