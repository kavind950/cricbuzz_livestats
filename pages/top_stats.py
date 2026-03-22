import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, get_connection
import plotly.graph_objects as go
import plotly.express as px
import os
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def show_top_stats():
    """Display top player statistics from database with refresh options."""
    
    st.header("📊 Top Player Stats")
    
    st.write("Explore the best cricket performers across different formats and categories.")
    
    # Database Sync Controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Sync Live Data from API"):
            with st.spinner("Syncing database with live data..."):
                try:
                    script_dir = Path(__file__).parent.parent
                    fetch_script = script_dir / "utils" / "fetch_live_data.py"
                    
                    result = subprocess.run(
                        ["python", str(fetch_script)],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Database synced with latest data!")
                        st.rerun()
                    else:
                        st.error(f"❌ Sync failed: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with col2:
        # Show last sync time (if available)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(created_at) FROM matches")
            result = cursor.fetchone()
            if result and result[0]:
                last_match_date = result[0]
                time_diff = (datetime.now() - last_match_date).total_seconds()
                if time_diff < 60:
                    sync_time = f"{int(time_diff)}s ago"
                elif time_diff < 3600:
                    sync_time = f"{int(time_diff/60)}m ago"
                else:
                    sync_time = f"{int(time_diff/3600)}h ago"
                st.metric("Last Data Update", sync_time)
            cursor.close()
            conn.close()
        except:
            st.metric("Last Data Update", "N/A")
    
    with col3:
        # Show record count
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM players")
            player_count = cursor.fetchone()[0]
            st.metric("Players in DB", player_count)
            cursor.close()
            conn.close()
        except:
            st.metric("Players in DB", "N/A")
    
    st.markdown("---")
    
    st.write("Explore the best cricket performers across different formats and categories.")
    
    # Create tabs for different stat categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏏 Batting Leaders", 
        "🎯 Bowling Leaders",
        "📈 All-rounders",
        "🏪 Format Comparison",
        "📉 Trends"
    ])
    
    with tab1:
        show_batting_leaders()
    
    with tab2:
        show_bowling_leaders()
    
    with tab3:
        show_allrounders()
    
    with tab4:
        show_format_comparison()
    
    with tab5:
        show_trends()


def show_batting_leaders():
    """Display top batting statistics."""
    
    st.subheader("🏏 Batting Leaders")
    
    stat_type = st.radio("Select Stat Type:", 
                        ["Most Runs", "Highest Average", "Most Centuries", "Highest Strike Rate"],
                        horizontal=True)
    
    format_filter = st.selectbox("Select Format:", ["All", "Test", "ODI", "T20I"], key="bat_format")
    
    # Sample queries - adjust based on your actual database schema
    queries = {
        "Most Runs": """
            SELECT 
                p.full_name,
                SUM(i.runs_scored) AS total_runs,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.runs_scored), 2) AS average,
                ROUND(AVG(i.strike_rate), 2) AS strike_rate
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.batting_position > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            ORDER BY total_runs DESC
            LIMIT 20
        """,
        "Highest Average": """
            SELECT 
                p.full_name,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.runs_scored), 2) AS average,
                SUM(i.runs_scored) AS total_runs,
                ROUND(AVG(i.strike_rate), 2) AS strike_rate
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.batting_position > 0 AND i.runs_scored > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            HAVING COUNT(i.innings_id) >= 5
            ORDER BY average DESC
            LIMIT 20
        """,
        "Most Centuries": """
            SELECT 
                p.full_name,
                SUM(CASE WHEN i.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries,
                SUM(CASE WHEN i.runs_scored >= 50 AND i.runs_scored < 100 THEN 1 ELSE 0 END) AS fifties,
                ROUND(AVG(i.runs_scored), 2) AS average,
                SUM(i.runs_scored) AS total_runs
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.batting_position > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            ORDER BY centuries DESC
            LIMIT 20
        """,
        "Highest Strike Rate": """
            SELECT 
                p.full_name,
                ROUND(AVG(i.strike_rate), 2) AS strike_rate,
                SUM(i.runs_scored) AS total_runs,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.runs_scored), 2) AS average
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.batting_position > 0 AND i.strike_rate > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            HAVING COUNT(i.innings_id) >= 5
            ORDER BY strike_rate DESC
            LIMIT 20
        """
    }
    
    # Build format clause with parameterized query
    format_clause = "" if format_filter == "All" else "AND m.match_format = %s"
    
    query = queries[stat_type].format(format_clause=format_clause)
    query_params = None if format_filter == "All" else (format_filter,)
    
    try:
        data = execute_query(query, query_params, fetch=True)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            if stat_type == "Most Runs":
                fig = px.bar(df.head(10), x="full_name", y="total_runs", 
                           title="Top 10 Run Scorers", color="total_runs",
                           color_continuous_scale="Viridis")
                st.plotly_chart(fig, use_container_width=True)
            elif stat_type == "Highest Average":
                fig = px.bar(df.head(10), x="full_name", y="average",
                           title="Top 10 Batting Averages", color="average",
                           color_continuous_scale="Blues")
                st.plotly_chart(fig, use_container_width=True)
            elif stat_type == "Most Centuries":
                fig = px.bar(df.head(10), x="full_name", y="centuries",
                           title="Top 10 Century Makers", color="centuries",
                           color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            elif stat_type == "Highest Strike Rate":
                fig = px.bar(df.head(10), x="full_name", y="strike_rate",
                           title="Top 10 Highest Strike Rates", color="strike_rate",
                           color_continuous_scale="Greens")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for selected filters")
    
    except Exception as e:
        st.error(f"Error fetching batting stats: {e}")


def show_bowling_leaders():
    """Display top bowling statistics."""
    
    st.subheader("🎯 Bowling Leaders")
    
    stat_type = st.radio("Select Stat Type:",
                        ["Most Wickets", "Best Average", "Best Economy Rate", "Best Strike Rate"],
                        horizontal=True, key="bowl_type")
    
    format_filter = st.selectbox("Select Format:", ["All", "Test", "ODI", "T20I"], key="bowl_format")
    
    queries = {
        "Most Wickets": """
            SELECT 
                p.full_name,
                SUM(i.wickets_taken) AS total_wickets,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.bowling_average), 2) AS average,
                ROUND(AVG(i.economy_rate), 2) AS economy
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.bowling_position > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            ORDER BY total_wickets DESC
            LIMIT 20
        """,
        "Best Average": """
            SELECT 
                p.full_name,
                ROUND(AVG(i.bowling_average), 2) AS average,
                SUM(i.wickets_taken) AS total_wickets,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.economy_rate), 2) AS economy
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.bowling_position > 0 AND i.bowling_average > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            HAVING SUM(i.wickets_taken) >= 10
            ORDER BY average ASC
            LIMIT 20
        """,
        "Best Economy Rate": """
            SELECT 
                p.full_name,
                ROUND(AVG(i.economy_rate), 2) AS economy_rate,
                SUM(i.wickets_taken) AS total_wickets,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.bowling_average), 2) AS average
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.bowling_position > 0 AND i.economy_rate > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            HAVING COUNT(i.innings_id) >= 5
            ORDER BY economy_rate ASC
            LIMIT 20
        """,
        "Best Strike Rate": """
            SELECT 
                p.full_name,
                ROUND(AVG(i.bowling_strike_rate), 2) AS strike_rate,
                SUM(i.wickets_taken) AS total_wickets,
                COUNT(i.innings_id) AS matches,
                ROUND(AVG(i.bowling_average), 2) AS average
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            JOIN matches m ON i.match_id = m.match_id
            WHERE i.bowling_position > 0 AND i.bowling_strike_rate > 0 {format_clause}
            GROUP BY p.player_id, p.full_name
            HAVING COUNT(i.innings_id) >= 5
            ORDER BY strike_rate ASC
            LIMIT 20
        """
    }
    
    format_clause = "" if format_filter == "All" else "AND m.match_format = %s"
    query = queries[stat_type].format(format_clause=format_clause)
    query_params = None if format_filter == "All" else (format_filter,)
    
    try:
        data = execute_query(query, query_params, fetch=True)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            if stat_type == "Most Wickets":
                fig = px.bar(df.head(10), x="full_name", y="total_wickets",
                           title="Top 10 Wicket Takers", color="total_wickets",
                           color_continuous_scale="Oranges")
                st.plotly_chart(fig, use_container_width=True)
            elif stat_type == "Best Average":
                fig = px.bar(df.head(10), x="full_name", y="average",
                           title="Top 10 Best Bowling Averages", color="average",
                           color_continuous_scale="RdYlGn_r")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for selected filters")
    
    except Exception as e:
        st.error(f"Error fetching bowling stats: {e}")


def show_allrounders():
    """Display all-rounder statistics."""
    
    st.subheader("⭐ All-Round Performers")
    
    query = """
        SELECT 
            p.full_name,
            SUM(CASE WHEN i.batting_position > 0 THEN i.runs_scored ELSE 0 END) AS batting_runs,
            SUM(CASE WHEN i.bowling_position > 0 THEN i.wickets_taken ELSE 0 END) AS bowling_wickets,
            ROUND(AVG(CASE WHEN i.batting_position > 0 THEN i.runs_scored END), 2) AS batting_avg,
            ROUND(AVG(CASE WHEN i.bowling_position > 0 THEN i.bowling_average END), 2) AS bowling_avg
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        WHERE p.playing_role = 'All-rounder'
        GROUP BY p.player_id, p.full_name
        HAVING SUM(CASE WHEN i.batting_position > 0 THEN i.runs_scored ELSE 0 END) > 500
            AND SUM(CASE WHEN i.bowling_position > 0 THEN i.wickets_taken ELSE 0 END) > 20
        ORDER BY batting_runs DESC
        LIMIT 15
    """
    
    try:
        data = execute_query(query, fetch=True)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Bubble chart
            fig = px.scatter(df, x="batting_runs", y="bowling_wickets",
                           size="batting_runs", color="bowling_wickets",
                           hover_data=["full_name", "batting_avg", "bowling_avg"],
                           title="All-rounder Performance: Runs vs Wickets",
                           labels={"batting_runs": "Total Runs", "bowling_wickets": "Total Wickets"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No all-rounder data available")
    
    except Exception as e:
        st.error(f"Error fetching all-rounder stats: {e}")


def show_format_comparison():
    """Show player performance across different formats."""
    
    st.subheader("📈 Format Comparison")
    
    st.info("Compare player performance across Test, ODI, and T20 formats")
    
    query = """
        SELECT 
            p.full_name,
            SUM(CASE WHEN m.match_format = 'Test' AND i.batting_position > 0 
                     THEN i.runs_scored ELSE 0 END) AS test_runs,
            SUM(CASE WHEN m.match_format = 'ODI' AND i.batting_position > 0 
                     THEN i.runs_scored ELSE 0 END) AS odi_runs,
            SUM(CASE WHEN m.match_format = 'T20I' AND i.batting_position > 0 
                     THEN i.runs_scored ELSE 0 END) AS t20i_runs
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        JOIN matches m ON i.match_id = m.match_id
        WHERE i.batting_position > 0
        GROUP BY p.player_id, p.full_name
        HAVING SUM(i.runs_scored) > 100
        ORDER BY test_runs DESC
        LIMIT 10
    """
    
    try:
        data = execute_query(query, fetch=True)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Stacked bar chart
            fig = px.bar(df, x="full_name",
                       y=["test_runs", "odi_runs", "t20i_runs"],
                       title="Player Runs Across Different Formats",
                       barmode="stack", color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No format comparison data available")
    
    except Exception as e:
        st.error(f"Error fetching format comparison: {e}")


def show_trends():
    """Display performance trends."""
    
    st.subheader("📉 Performance Trends")
    
    st.write("Track how player performance evolves over time")
    
    # Sample trend query
    query = """
        SELECT 
            p.full_name,
            EXTRACT(YEAR FROM m.match_date) AS year,
            COUNT(i.innings_id) AS matches,
            ROUND(AVG(i.runs_scored), 2) AS avg_runs
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        JOIN matches m ON i.match_id = m.match_id
        WHERE i.batting_position > 0
        GROUP BY p.player_id, p.full_name, EXTRACT(YEAR FROM m.match_date)
        ORDER BY p.full_name, year DESC
        LIMIT 50
    """
    
    try:
        data = execute_query(query, fetch=True)
        
        if data:
            df = pd.DataFrame(data)
            
            # Get unique players
            players = df['full_name'].unique()[:5]  # Top 5 players
            
            fig = px.line(df[df['full_name'].isin(players)], 
                        x="year", y="avg_runs", color="full_name",
                        title="Player Performance Trends Over Years",
                        markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available")
    
    except Exception as e:
        st.error(f"Error fetching trends: {e}")
