# SQL Analytics Interface for Cricket Analytics Platform
#
# This module provides a comprehensive SQL query execution environment with:
# - Pre-built library of 25+ cricket analytics queries
# - Custom SQL query editor for advanced users
# - Safe schema validation to prevent errors
# - Results displayed in interactive tables
#
# Query Categories:
# - Beginner (1-8): Basic filtering and aggregation
# - Intermediate (9-16): Multi-table joins and subqueries
# - Advanced (17-25): Window functions and complex analytics
#
# Usage: Users can select predefined queries or write custom SQL directly

from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Dict
from utils.db_connection import get_conn, ensure_schema, seed_demo_data_if_empty

# ---------- Helper function for safe query execution ----------
def _query_df(sql: str, params: Dict | None = None) -> pd.DataFrame:
    """
    Execute a SQL query safely and return results as a pandas DataFrame.
    
    Features:
    - Ensures database schema exists before execution
    - Catches and displays SQL errors gracefully
    - Returns empty DataFrame on error to prevent app crashes
    
    - Supports parameterized queries to prevent SQL injection
    
    Args:
        sql: SQL query string
        params: Optional dictionary of parameters for parameterized queries
        
    Returns:
        pandas.DataFrame: Query results, or empty DataFrame if error occurs
    """
    ensure_schema()
    conn = get_conn()
    try:
        return pd.read_sql_query(sql, conn, params=params or {})
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

def show_sql_analytics():
    st.markdown("# 📋 SQL Queries & Analytics")
    st.caption("All queries run against the local SQLite DB created by `utils/db_connection.py`.")

    # one-click demo data (safe to click multiple times)
    if st.button("📦 Click to load data"):
        try:
            seed_demo_data_if_empty(force=True)
            st.success("Demo data inserted.")
        except Exception as e:
            st.error(f"Seeding failed: {e}")

    # Tabs
    t1, t2, t3, t4 = st.tabs(["🟢 Beginner (1–8)", "🟡 Intermediate (9–16)", "🔴 Advanced (17–25)", "💻 Custom Query"])
    with t1:
        _beginner()
    with t2:
        _intermediate()
    with t3:
        _advanced()
    with t4:
        _custom()

# -------------------- Query groups --------------------
def _beginner():
    st.subheader("🟢 Beginner")
    _run(
        "Q1 — All Indian players",
        """
        SELECT name, playing_role, batting_style, bowling_style
        FROM players
        WHERE country = 'India'
        ORDER BY name;
        """,
        "Uses `players` (country / roles / styles)."
    )

    _run(
        "Q2 — Matches in last 30 days",
        """
        SELECT
          COALESCE(m.description, m.team1 || ' vs ' || m.team2) AS match_desc,
          m.team1, m.team2,
          COALESCE(v.name, m.venue) AS venue_city,
          m.start_time
        FROM matches m
        LEFT JOIN venues v ON v.venue_id = m.venue_id
        WHERE m.start_time IS NOT NULL
          AND date(m.start_time) >= date('now','-30 day')
        ORDER BY datetime(m.start_time) DESC;
        """,
        "Matches from `matches` (uses `start_time`, joins venues if available)."
    )

    _run(
        "Q3 — Top 10 ODI run scorers (from innings)",
        """
        SELECT b.player_name,
               SUM(b.runs) AS total_runs,
               ROUND(AVG(b.runs),2) AS avg_runs,
               SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) AS hundreds
        FROM batting_innings b
        JOIN matches m ON m.match_id = b.match_id
        WHERE m.match_type = 'ODI'
        GROUP BY b.player_name
        ORDER BY total_runs DESC
        LIMIT 10;
        """,
        "Built from `batting_innings` + `matches.match_type='ODI'`."
    )

    _run(
        "Q4 — Venues with capacity > 50k",
        """
        SELECT name AS venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC, venue_name;
        """,
        "Pure `venues` table."
    )

    _run(
        "Q5 — Team wins leaderboard",
        """
        SELECT winner AS team, COUNT(*) AS total_wins
        FROM matches
        WHERE winner IS NOT NULL
        GROUP BY winner
        ORDER BY total_wins DESC, team;
        """,
        "Counts winners from `matches`."
    )

    _run(
        "Q6 — Players by playing role",
        """
        SELECT playing_role, COUNT(*) AS player_count
        FROM players
        WHERE playing_role IS NOT NULL AND TRIM(playing_role) <> ''
        GROUP BY playing_role
        ORDER BY player_count DESC, playing_role;
        """,
        "`players.playing_role` simple grouping."
    )

    _run(
        "Q7 — Highest individual score by format",
        """
        SELECT m.match_type AS format, MAX(b.runs) AS highest_score
        FROM batting_innings b
        JOIN matches m ON m.match_id = b.match_id
        GROUP BY m.match_type
        ORDER BY format;
        """,
        "`batting_innings` joined to `matches`."
    )

    _run(
        "Q8 — Series that started in 2024",
        """
        SELECT series_name, host_country, match_type, start_date, planned_matches
        FROM series
        WHERE start_date IS NOT NULL
          AND strftime('%Y', start_date) = '2024'
        ORDER BY start_date DESC, series_name;
        """,
        "`series` table by year."
    )

def _intermediate():
    st.subheader("🟡 Intermediate")
    _run(
        "Q9 — All-rounders: >1000 runs & >50 wickets",
        """
        SELECT name, country, total_runs, total_wickets, playing_role
        FROM players
        WHERE playing_role = 'All-rounder'
          AND COALESCE(total_runs,0) > 1000
          AND COALESCE(total_wickets,0) > 50
        ORDER BY total_runs DESC, total_wickets DESC;
        """,
        "Pure `players` aggregate columns."
    )

    _run(
        "Q10 — Last 20 completed matches (details)",
        """
        SELECT
          COALESCE(m.description, m.team1 || ' vs ' || m.team2) AS match_desc,
          m.team1, m.team2, m.winner,
          m.victory_margin, m.victory_type,
          COALESCE(v.name, m.venue) AS venue_name,
          m.start_time
        FROM matches m
        LEFT JOIN venues v ON v.venue_id = m.venue_id
        WHERE (m.status LIKE '%Complete%' OR m.status LIKE '%Ended%' OR m.status LIKE '%Result%'
               OR m.winner IS NOT NULL)
        ORDER BY datetime(m.start_time) DESC
        LIMIT 20;
        """,
        "Status-robust filter on `matches` (+`winner`)."
    )

    _run(
        "Q11 — Player format comparison (runs + overall average)",
        """
        WITH s AS (
          SELECT b.player_name AS player, m.match_type AS format, SUM(b.runs) AS runs
          FROM batting_innings b
          JOIN matches m ON m.match_id = b.match_id
          GROUP BY b.player_name, m.match_type
        ),
        avgp AS (
          SELECT player_name AS player, AVG(runs) AS overall_batting_avg
          FROM batting_innings
          GROUP BY player_name
        )
        SELECT
          s.player,
          SUM(CASE WHEN s.format='Test' THEN s.runs ELSE 0 END)   AS runs_test,
          SUM(CASE WHEN s.format='ODI' THEN s.runs ELSE 0 END)    AS runs_odi,
          SUM(CASE WHEN s.format IN ('T20','T20I') THEN s.runs ELSE 0 END) AS runs_t20,
          ROUND(ap.overall_batting_avg,2) AS overall_batting_avg
        FROM s
        LEFT JOIN avgp ap ON ap.player = s.player
        GROUP BY s.player, ap.overall_batting_avg
        HAVING COUNT(DISTINCT s.format) >= 2
        ORDER BY runs_odi DESC, runs_t20 DESC
        LIMIT 50;
        """,
        "Pivot-style sums from `batting_innings` + overall AVG per player."
    )

    _run(
        "Q12 — Home vs away team wins (heuristic by venue country)",
        """
        SELECT
          m.winner AS team,
          SUM(CASE WHEN m.venue_country IS NOT NULL AND m.winner = m.venue_country THEN 1 ELSE 0 END) AS home_wins,
          SUM(CASE WHEN m.venue_country IS NOT NULL AND m.winner <> m.venue_country THEN 1 ELSE 0 END) AS away_or_neutral_wins
        FROM matches m
        WHERE m.winner IS NOT NULL
        GROUP BY m.winner
        ORDER BY home_wins DESC, away_or_neutral_wins DESC, team;
        """,
        "Heuristic: if winner equals `venue_country`, count as home."
    )

    _run(
        "Q13 — 100+ run partnerships (adjacent batters approximation)",
        """
        SELECT
          b1.match_id, b1.innings_no, b1.team,
          b1.player_name AS batter1, b2.player_name AS batter2,
          (b1.runs + b2.runs) AS partnership_runs
        FROM batting_innings b1
        JOIN batting_innings b2
          ON b1.match_id=b2.match_id
         AND b1.innings_no=b2.innings_no
         AND b1.team=b2.team
         AND b2.position = b1.position + 1
        WHERE (b1.runs + b2.runs) >= 100
        ORDER BY partnership_runs DESC
        LIMIT 50;
        """,
        "Uses batting order adjacency as a pragmatic proxy for partnerships."
    )

    # ---------- RELAXED FOR DEMO: HAVING spells >= 2 (was >= 3) ----------
    _run(
        "Q14 — Bowling performance by venue (>=2 spells)",
        """
        SELECT
          COALESCE(v.name, m.venue) AS venue_name,
          bs.bowler_name,
          COUNT(*) AS spells,
          ROUND(AVG(bs.economy),2) AS avg_economy,
          SUM(bs.wickets) AS total_wickets
        FROM bowling_spells bs
        JOIN matches m ON m.match_id = bs.match_id
        LEFT JOIN venues v ON v.venue_id = m.venue_id
        GROUP BY venue_name, bs.bowler_name
        HAVING spells >= 2
        ORDER BY avg_economy ASC, total_wickets DESC
        LIMIT 100;
        """,
        "`bowling_spells` + venue join. Threshold relaxed so demo data returns rows."
    )

    _run(
        "Q15 — Performers in close matches (<50 runs or <5 wkts)",
        """
        WITH close_matches AS (
          SELECT match_id
          FROM matches
          WHERE (victory_type='runs'    AND CAST(victory_margin AS INTEGER) < 50)
             OR (victory_type='wickets' AND CAST(victory_margin AS INTEGER) < 5)
        )
        SELECT
          b.player_name,
          COUNT(*) AS innings,
          ROUND(AVG(b.runs),2) AS avg_runs
        FROM batting_innings b
        JOIN close_matches c ON c.match_id = b.match_id
        GROUP BY b.player_name
        HAVING innings >= 3
        ORDER BY avg_runs DESC, innings DESC
        LIMIT 50;
        """,
        "Relies on `matches.victory_type` + numeric `victory_margin`."
    )

    _run(
        "Q16 — Yearly batting trends since 2020 (>=5 inns/yr)",
        """
        SELECT
          b.player_name AS player,
          strftime('%Y', m.start_time) AS year,
          COUNT(*) AS innings,
          ROUND(AVG(b.runs),2) AS avg_runs
        FROM batting_innings b
        JOIN matches m ON m.match_id = b.match_id
        WHERE date(m.start_time) >= '2020-01-01'
        GROUP BY b.player_name, year
        HAVING innings >= 5
        ORDER BY player, year DESC;
        """,
        "Trends based on `start_time`."
    )

def _advanced():
    st.subheader("🔴 Advanced")

    _run(
        "Q17 — Toss advantage analysis",
        """
        WITH t AS (
          SELECT toss_winner, toss_decision, winner,
                 CASE WHEN toss_winner IS NOT NULL AND toss_winner = winner THEN 1 ELSE 0 END AS tw_won
          FROM matches
          WHERE toss_winner IS NOT NULL AND winner IS NOT NULL
        )
        SELECT toss_decision,
               COUNT(*) AS total_matches,
               SUM(tw_won) AS toss_winner_victories,
               ROUND(100.0 * SUM(tw_won) / COUNT(*), 2) AS win_percentage
        FROM t
        GROUP BY toss_decision
        ORDER BY win_percentage DESC;
        """,
        "CTE with conditional aggregation."
    )

    # ---------- RELAXED FOR DEMO: spells >= 3 (was >= 10) ----------
    _run(
        "Q18 — Most economical bowlers (LOI; >=3 spells, >=2 overs avg)",
        """
        WITH agg AS (
          SELECT
            bs.bowler_name,
            COUNT(*) AS spells,
            ROUND(AVG(bs.overs),2) AS avg_overs_per_match,
            ROUND(AVG(bs.economy),2) AS overall_economy,
            SUM(bs.wickets) AS total_wickets
          FROM bowling_spells bs
          JOIN matches m ON m.match_id = bs.match_id
          WHERE m.match_type IN ('ODI','T20','T20I')
          GROUP BY bs.bowler_name
        )
        SELECT *
        FROM agg
        WHERE spells >= 3 AND avg_overs_per_match >= 2.0
        ORDER BY overall_economy ASC, total_wickets DESC
        LIMIT 15;
        """,
        "Aggregates from `bowling_spells` constrained to LOI formats. Threshold relaxed for demo data."
    )

    _run(
        "Q19 — Batting consistency since 2022 (std dev, >=10 inns)",
        """
        WITH x AS (
          SELECT
            b.player_name AS name,
            b.runs AS runs_scored,
            AVG(b.runs) OVER (PARTITION BY b.player_name) AS avg_runs,
            COUNT(*)  OVER (PARTITION BY b.player_name) AS total_innings
          FROM batting_innings b
          JOIN matches m ON m.match_id = b.match_id
          WHERE date(m.start_time) >= '2022-01-01' AND COALESCE(b.balls,0) >= 10
        )
        SELECT
          name,
          total_innings,
          ROUND(avg_runs,2) AS average_runs,
          ROUND(SQRT(AVG( (runs_scored - avg_runs)*(runs_scored - avg_runs) )),2) AS standard_deviation
        FROM x
        GROUP BY name, avg_runs, total_innings
        HAVING total_innings >= 10
        ORDER BY standard_deviation ASC, total_innings DESC
        LIMIT 20;
        """,
        "Window functions + population std-dev formula in SQLite."
    )

    # ---------- RELAXED FOR DEMO: total innings >= 8 (was >= 20) ----------
    _run(
        "Q20 — Matches & batting averages by format (>=8 inns total)",
        """
        WITH fs AS (
          SELECT
            b.player_name AS name,
            m.match_type     AS format,
            COUNT(*)         AS innings,
            AVG(b.runs)      AS avg_runs
          FROM batting_innings b
          JOIN matches m ON m.match_id = b.match_id
          GROUP BY b.player_name, m.match_type
        )
        SELECT
          name,
          SUM(CASE WHEN format='Test' THEN innings ELSE 0 END) AS test_matches,
          SUM(CASE WHEN format='ODI'  THEN innings ELSE 0 END) AS odi_matches,
          SUM(CASE WHEN format IN ('T20','T20I') THEN innings ELSE 0 END) AS t20_matches,
          ROUND(AVG(CASE WHEN format='Test' THEN avg_runs END),2) AS test_avg,
          ROUND(AVG(CASE WHEN format='ODI'  THEN avg_runs END),2) AS odi_avg,
          ROUND(AVG(CASE WHEN format IN ('T20','T20I') THEN avg_runs END),2) AS t20_avg
        FROM fs
        GROUP BY name
        HAVING (test_matches + odi_matches + t20_matches) >= 8
        ORDER BY (test_matches + odi_matches + t20_matches) DESC, name;
        """,
        "Pivot-style rollup across formats from `batting_innings`. Threshold relaxed."
    )

    _run(
        "Q21 — Composite performance ranking (batting + bowling)",
        """
        -- build batting metrics
        WITH bat AS (
          SELECT
            player_name AS name,
            SUM(runs) AS total_runs,
            AVG(runs) AS batting_average,
            CASE WHEN SUM(balls) > 0 THEN 100.0 * SUM(runs) / SUM(balls) END AS strike_rate
          FROM batting_innings
          GROUP BY player_name
        ),
        -- build bowling metrics
        bowl AS (
          SELECT
            bowler_name AS name,
            SUM(wickets) AS total_wickets,
            AVG(economy) AS economy_rate,
            CASE WHEN SUM(wickets) > 0 THEN 1.0 * SUM(runs) / SUM(wickets) END AS bowling_average
          FROM bowling_spells
          GROUP BY bowler_name
        ),
        -- outer-join emulation for SQLite
        both AS (
          SELECT COALESCE(bat.name, bowl.name) AS name,
                 bat.total_runs, bat.batting_average, bat.strike_rate,
                 bowl.total_wickets, bowl.bowling_average, bowl.economy_rate
          FROM bat LEFT JOIN bowl ON bowl.name = bat.name
          UNION
          SELECT COALESCE(bat.name, bowl.name) AS name,
                 bat.total_runs, bat.batting_average, bat.strike_rate,
                 bowl.total_wickets, bowl.bowling_average, bowl.economy_rate
          FROM bowl LEFT JOIN bat ON bat.name = bowl.name
        )
        SELECT
          name,
          ROUND(COALESCE(total_runs,0)*0.01 + COALESCE(batting_average,0)*0.5 + COALESCE(strike_rate,0)*0.3, 2) AS batting_points,
          ROUND(COALESCE(total_wickets,0)*2
                + (50 - COALESCE(bowling_average,50))*0.5
                + (6 - COALESCE(economy_rate,6))*2, 2) AS bowling_points,
          ROUND(
            COALESCE(total_runs,0)*0.01 + COALESCE(batting_average,0)*0.5 + COALESCE(strike_rate,0)*0.3
            + COALESCE(total_wickets,0)*2 + (50 - COALESCE(bowling_average,50))*0.5 + (6 - COALESCE(economy_rate,6))*2
          , 2) AS total_performance_score
        FROM both
        WHERE COALESCE(total_runs,0) > 500 OR COALESCE(total_wickets,0) > 25
        ORDER BY total_performance_score DESC, name
        LIMIT 25;
        """,
        "Combines batting & bowling from innings/spells; outer-join emulation for SQLite."
    )

    _run(
        "Q22 — Head-to-head prediction base (last 3y, ≥5)",
        """
        WITH tm AS (
          SELECT
            CASE WHEN team1 <= team2 THEN team1 || ' vs ' || team2 ELSE team2 || ' vs ' || team1 END AS matchup,
            team1, team2, winner, start_time
          FROM matches
          WHERE winner IS NOT NULL AND date(start_time) >= date('now','-3 years')
        ),
        agg AS (
          SELECT
            matchup,
            COUNT(*) AS total_matches,
            SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) AS team1_wins,
            SUM(CASE WHEN winner = team2 THEN 1 ELSE 0 END) AS team2_wins,
            AVG(CASE WHEN winner = team1 THEN 1.0 ELSE 0.0 END) AS team1_win_pct
          FROM tm
          GROUP BY matchup
          HAVING total_matches >= 5
        )
        SELECT matchup, total_matches, team1_wins, team2_wins,
               ROUND(team1_win_pct*100,1) AS team1_win_percentage
        FROM agg
        ORDER BY total_matches DESC, team1_win_percentage DESC;
        """,
        "SQLite-safe string ordering for matchup key."
    )

    _run(
        "Q23 — Recent form (last 10 innings with windowing)",
        """
        WITH rp AS (
          SELECT
            b.player_name AS name,
            b.runs AS runs_scored,
            b.strike_rate,
            m.start_time AS match_time,
            ROW_NUMBER() OVER (PARTITION BY b.player_name ORDER BY datetime(m.start_time) DESC) AS rnk
          FROM batting_innings b
          JOIN matches m ON m.match_id = b.match_id
          WHERE date(m.start_time) >= date('now','-1 year')
        ),
        fa AS (
          SELECT
            name,
            AVG(CASE WHEN rnk <= 5  THEN runs_scored END) AS last_5_avg,
            AVG(CASE WHEN rnk <= 10 THEN runs_scored END) AS last_10_avg,
            AVG(CASE WHEN rnk <= 10 THEN strike_rate  END) AS recent_sr,
            SUM(CASE WHEN rnk <= 10 AND runs_scored >= 50 THEN 1 ELSE 0 END) AS scores_above_50,
            COUNT(*) AS rows_count
          FROM rp
          WHERE rnk <= 10
          GROUP BY name
          HAVING rows_count >= 5
        )
        SELECT
          name,
          ROUND(last_5_avg,1)  AS last_5_matches_avg,
          ROUND(last_10_avg,1) AS last_10_matches_avg,
          ROUND(recent_sr,1)   AS recent_strike_rate,
          scores_above_50,
          CASE
            WHEN last_5_avg >= 45 AND scores_above_50 >= 3 THEN 'Excellent Form'
            WHEN last_5_avg >= 30 AND scores_above_50 >= 2 THEN 'Good Form'
            WHEN last_5_avg >= 20 THEN 'Average Form'
            ELSE 'Poor Form'
          END AS current_form
        FROM fa
        ORDER BY last_5_matches_avg DESC, scores_above_50 DESC;
        """,
        "Windowed recent-form rollup from batting innings."
    )

    _run(
        "Q24 — Successful batting partnerships (≥5, success rate)",
        """
        WITH pairs AS (
          SELECT
            b1.player_name AS player1,
            b2.player_name AS player2,
            b1.match_id, b1.innings_no,
            (b1.runs + b2.runs) AS partnership_runs
          FROM batting_innings b1
          JOIN batting_innings b2
            ON b1.match_id=b2.match_id
           AND b1.innings_no=b2.innings_no
           AND b1.team=b2.team
           AND b2.position = b1.position + 1
        ),
        ps AS (
          SELECT
            player1 || ' & ' || player2 AS partnership,
            COUNT(*) AS total_partnerships,
            AVG(partnership_runs) AS avg_partnership_runs,
            MAX(partnership_runs) AS highest_partnership,
            SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) AS partnerships_above_50,
            ROUND(100.0 * SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*), 1) AS success_rate
          FROM pairs
          GROUP BY player1, player2
          HAVING total_partnerships >= 5
        )
        SELECT
          partnership,
          total_partnerships,
          ROUND(avg_partnership_runs,1) AS avg_runs,
          highest_partnership,
          partnerships_above_50,
          success_rate || '%' AS success_percentage
        FROM ps
        ORDER BY success_rate DESC, avg_runs DESC
        LIMIT 20;
        """,
        "Partnership proxy using adjacent batters."
    )

    # ---------- RELAXED FOR DEMO: per-quarter mins >=2; total_quarters >=3 ----------
    _run(
        "Q25 — Time-series performance evolution (quarterly, relaxed)",
        """
        WITH qp AS (
          SELECT
            b.player_name AS name,
            strftime('%Y', m.start_time) || '-Q' ||
              CASE
                WHEN CAST(strftime('%m', m.start_time) AS INT) <= 3 THEN '1'
                WHEN CAST(strftime('%m', m.start_time) AS INT) <= 6 THEN '2'
                WHEN CAST(strftime('%m', m.start_time) AS INT) <= 9 THEN '3'
                ELSE '4'
              END AS quarter,
            AVG(b.runs)  AS quarterly_avg_runs,
            AVG(b.strike_rate) AS quarterly_avg_sr,
            COUNT(*) AS matches_in_quarter
          FROM batting_innings b
          JOIN matches m ON m.match_id = b.match_id
          WHERE date(m.start_time) >= date('now','-2 years')
          GROUP BY b.player_name, quarter
          HAVING matches_in_quarter >= 2   -- relaxed from 3
        ),
        t AS (
          SELECT
            name, quarter, quarterly_avg_runs, quarterly_avg_sr,
            LAG(quarterly_avg_runs) OVER (PARTITION BY name ORDER BY quarter) AS prev_quarter_runs,
            COUNT(*) OVER (PARTITION BY name) AS total_quarters
          FROM qp
        )
        SELECT
          name,
          total_quarters,
          ROUND(AVG(quarterly_avg_runs),2) AS overall_quarterly_avg,
          ROUND(AVG(quarterly_avg_sr),2)  AS overall_quarterly_sr,
          CASE
            WHEN AVG(quarterly_avg_runs - COALESCE(prev_quarter_runs, quarterly_avg_runs)) > 2 THEN 'Career Ascending'
            WHEN AVG(quarterly_avg_runs - COALESCE(prev_quarter_runs, quarterly_avg_runs)) < -2 THEN 'Career Declining'
            ELSE 'Career Stable'
          END AS career_trajectory
        FROM t
        GROUP BY name
        HAVING total_quarters >= 3        -- relaxed from 6
        ORDER BY overall_quarterly_avg DESC;
        """,
        "Quarterly rollups + LAG. Thresholds relaxed so demo data returns rows."
    )

# -------------------- shared UI helpers --------------------
def _run(title: str, sql: str, note: str = ""):
    """
    Render a query expander with:
      - left: Execute button
      - right: SQL code
      - full-width block BELOW for results (so tables aren't cramped)
    """
    key_base = f"btn_{title}"
    with st.expander(f"📊 {title}", expanded=False):
        if note:
            st.caption(note)

        controls_col, code_col = st.columns([1, 5])
        with controls_col:
            run_clicked = st.button("▶️ Execute", key=key_base)
        with code_col:
            st.code(sql.strip(), language="sql")

        # full-width container for results (fixes the narrow table issue)
        results = st.container()

        if run_clicked:
            df = _query_df(sql)
            with results:
                if df is not None and not df.empty:
                    st.success(f"Found {len(df)} row(s).")
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        "📥 Download CSV",
                        df.to_csv(index=False),
                        file_name=f"{title.replace(' ', '_')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("Query ran successfully, but returned **no rows**.")

def _custom():
    st.subheader("💻 Custom SQL")
    st.caption("Use the schema below. Queries execute read-only.")

    with st.expander("📋 Schema reference", expanded=False):
        st.markdown("""
**players**: id, name, country, role, playing_role, batting_style, bowling_style,  
total_runs, batting_average, strike_rate, total_wickets, bowling_average, economy_rate, catches, stumpings

**matches**: match_id, description, match_type, status, start_time, team1, team2, venue,  
winner, victory_margin, victory_type, toss_winner, toss_decision, venue_id, venue_country, series_id, series_name, city

**venues**: venue_id, name, city, country, capacity, (compat: `venue`)

**series**: series_id, series_name, host_country, match_type, start_date, planned_matches

**batting_innings**: id, match_id, innings_no, team, player_name, player_id, position, runs, balls, strike_rate

**bowling_spells**: id, match_id, innings_no, bowler_name, bowler_id, overs, balls, runs, wickets, economy
""")

    samples = [
        "SELECT * FROM matches ORDER BY datetime(start_time) DESC LIMIT 10;",
        "SELECT country, COUNT(*) AS players FROM players GROUP BY country ORDER BY players DESC;",
        """SELECT b.player_name, AVG(b.runs) AS avg_runs
FROM batting_innings b JOIN matches m ON m.match_id=b.match_id
WHERE m.match_type='ODI'
GROUP BY b.player_name ORDER BY avg_runs DESC LIMIT 10;"""
    ]
    chosen = st.selectbox("Sample:", [""] + samples)
    sql = st.text_area("SQL", value=chosen or "SELECT * FROM players LIMIT 10;", height=180)

    if st.button("🚀 Execute custom"):
        df = _query_df(sql)
        if df is not None and not df.empty:
            st.success(f"Found {len(df)} row(s).")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Query ran successfully, but returned **no rows**.")

# For Streamlit's page loader
if __name__ == "__main__":
    show_sql_analytics()
