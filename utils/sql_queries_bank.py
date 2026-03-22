# SQL Queries Bank for Cricbuzz LiveStats
# 25 Comprehensive Cricket Analytics Queries (Beginner to Advanced)

BEGINNER_QUERIES = {
    "Q1_Indian_Players": """
    -- Q1: Find all players who represent India
    SELECT 
        player_id,
        full_name,
        playing_role,
        batting_style,
        bowling_style,
        country
    FROM players
    WHERE country = 'India'
    ORDER BY full_name;
    """,
    
    "Q2_Recent_Matches": """
    -- Q2: Show all cricket matches played in recent days
    SELECT 
        m.match_id,
        m.match_description,
        t1.team_name AS team_1,
        t2.team_name AS team_2,
        v.venue_name,
        v.city,
        m.match_date,
        m.match_status
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE m.match_date >= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY m.match_date DESC;
    """,
    
    "Q3_Top_10_ODI_Scorers": """
    -- Q3: List top 10 highest run scorers in ODI cricket
    SELECT 
        p.player_id,
        p.full_name,
        SUM(i.runs_scored) AS total_runs,
        COUNT(i.innings_id) AS matches_played,
        ROUND(AVG(i.runs_scored), 2) AS batting_average,
        SUM(CASE WHEN i.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE m.match_format = 'ODI' AND i.batting_position > 0
    GROUP BY p.player_id, p.full_name
    ORDER BY total_runs DESC
    LIMIT 10;
    """,
    
    "Q4_Large_Capacity_Venues": """
    -- Q4: Display all cricket venues with capacity > 25,000
    SELECT 
        venue_id,
        venue_name,
        city,
        country,
        seating_capacity
    FROM venues
    WHERE seating_capacity > 25000
    ORDER BY seating_capacity DESC
    LIMIT 10;
    """,
    
    "Q5_Team_Wins_Count": """
    -- Q5: Calculate total wins for each team
    SELECT 
        t.team_id,
        t.team_name,
        COUNT(m.match_id) AS total_wins
    FROM teams t
    LEFT JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
        AND m.winning_team_id = t.team_id
    GROUP BY t.team_id, t.team_name
    ORDER BY total_wins DESC;
    """,
    
    "Q6_Players_By_Role": """
    -- Q6: Count players in each playing role
    SELECT 
        playing_role,
        COUNT(player_id) AS player_count
    FROM players
    GROUP BY playing_role
    ORDER BY player_count DESC;
    """,
    
    "Q7_Highest_Score_By_Format": """
    -- Q7: Find highest individual batting score in each format
    SELECT 
        m.match_format,
        MAX(i.runs_scored) AS highest_score,
        p.full_name AS player_name,
        v.venue_name,
        m.match_date
    FROM innings i
    JOIN players p ON i.player_id = p.player_id
    JOIN matches m ON i.match_id = m.match_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE i.batting_position > 0
    GROUP BY m.match_format, i.runs_scored, p.full_name, v.venue_name, m.match_date
    ORDER BY m.match_format;
    """,
    
    "Q8_Series_2024": """
    -- Q8: Show all cricket series that started in 2024
    SELECT 
        series_id,
        series_name,
        host_country,
        match_type,
        start_date,
        total_matches_planned
    FROM series
    WHERE EXTRACT(YEAR FROM start_date) = 2024
    ORDER BY start_date DESC;
    """
}

INTERMEDIATE_QUERIES = {
    "Q9_Allrounders_Stats": """
    -- Q9: Find all-rounders with 1000+ runs and 50+ wickets
    SELECT 
        p.player_id,
        p.full_name,
        SUM(CASE WHEN i.batting_position > 0 THEN i.runs_scored ELSE 0 END) AS total_runs,
        SUM(CASE WHEN i.bowling_position > 0 THEN i.wickets_taken ELSE 0 END) AS total_wickets,
        m.match_format
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    GROUP BY p.player_id, p.full_name, m.match_format
    HAVING 
        SUM(CASE WHEN i.batting_position > 0 THEN i.runs_scored ELSE 0 END) > 1000
        AND SUM(CASE WHEN i.bowling_position > 0 THEN i.wickets_taken ELSE 0 END) > 50
    ORDER BY total_runs DESC;
    """,
    
    "Q10_Last_20_Matches": """
    -- Q10: Get details of last 20 completed matches
    SELECT 
        m.match_id,
        m.match_description,
        t1.team_name AS team_1,
        t2.team_name AS team_2,
        tw.team_name AS winning_team,
        m.victory_margin,
        m.victory_type,
        v.venue_name,
        m.match_date
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    LEFT JOIN teams tw ON m.winning_team_id = tw.team_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE m.match_status = 'Completed'
    ORDER BY m.match_date DESC
    LIMIT 20;
    """,
    
    "Q11_Player_Format_Performance": """
    -- Q11: Compare player performance across different cricket formats
    SELECT 
        p.full_name,
        SUM(CASE WHEN m.match_format = 'Test' AND i.batting_position > 0 
                 THEN i.runs_scored ELSE 0 END) AS test_runs,
        SUM(CASE WHEN m.match_format = 'ODI' AND i.batting_position > 0 
                 THEN i.runs_scored ELSE 0 END) AS odi_runs,
        SUM(CASE WHEN m.match_format = 'T20I' AND i.batting_position > 0 
                 THEN i.runs_scored ELSE 0 END) AS t20i_runs,
        ROUND(AVG(i.runs_scored), 2) AS overall_avg
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE i.batting_position > 0
    GROUP BY p.player_id, p.full_name
    HAVING COUNT(DISTINCT m.match_format) >= 2
    ORDER BY overall_avg DESC;
    """,
    
    "Q12_Home_Away_Performance": """
    -- Q12: Analyze team performance at home vs away
    SELECT 
        t.team_name,
        CASE 
            WHEN v.country = t.country THEN 'Home'
            ELSE 'Away'
        END AS match_type,
        COUNT(m.match_id) AS total_matches,
        SUM(CASE WHEN m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS wins
    FROM teams t
    JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
    JOIN venues v ON m.venue_id = v.venue_id
    GROUP BY t.team_id, t.team_name, match_type
    ORDER BY t.team_name, wins DESC;
    """,
    
    "Q13_Batting_Partnerships": """
    -- Q13: Identify batting partnerships scoring 100+ runs
    SELECT 
        p1.full_name AS batsman_1,
        p2.full_name AS batsman_2,
        SUM(CASE WHEN i1.batting_position + 1 = i2.batting_position 
                 THEN i1.runs_scored + i2.runs_scored ELSE 0 END) AS partnership_runs,
        i1.innings_id
    FROM innings i1
    JOIN innings i2 ON i1.match_id = i2.match_id 
        AND i1.batting_position + 1 = i2.batting_position
    JOIN players p1 ON i1.player_id = p1.player_id
    JOIN players p2 ON i2.player_id = p2.player_id
    GROUP BY p1.player_id, p1.full_name, p2.player_id, p2.full_name, i1.innings_id
    HAVING SUM(i1.runs_scored + i2.runs_scored) >= 100
    ORDER BY partnership_runs DESC;
    """,
    
    "Q14_Bowling_Venue_Performance": """
    -- Q14: Examine bowling performance at different venues
    SELECT 
        p.full_name,
        v.venue_name,
        COUNT(DISTINCT m.match_id) AS matches_at_venue,
        SUM(i.wickets_taken) AS total_wickets,
        ROUND(AVG(i.economy_rate), 2) AS avg_economy_rate
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE i.bowling_position > 0 AND i.overs_bowled >= 4
    GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name
    HAVING COUNT(DISTINCT m.match_id) >= 3
    ORDER BY avg_economy_rate ASC, total_wickets DESC;
    """,
    
    "Q15_Close_Match_Performance": """
    -- Q15: Identify players excelling in close matches
    SELECT 
        p.full_name,
        COUNT(DISTINCT m.match_id) AS close_matches_played,
        ROUND(AVG(i.runs_scored), 2) AS avg_runs_close_matches,
        SUM(CASE WHEN m.winning_team_id = 
                  (SELECT team_id FROM teams 
                   WHERE team_id IN (m.team1_id, m.team2_id)) 
                 THEN 1 ELSE 0 END) AS close_matches_won
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE i.batting_position > 0
        AND (m.victory_margin < 50 OR m.victory_margin IS NULL)
    GROUP BY p.player_id, p.full_name
    ORDER BY avg_runs_close_matches DESC;
    """,
    
    "Q16_Yearly_Performance_Trends": """
    -- Q16: Track players' batting performance by year
    SELECT 
        p.full_name,
        EXTRACT(YEAR FROM m.match_date) AS year,
        COUNT(i.innings_id) AS matches_played,
        ROUND(AVG(i.runs_scored), 2) AS avg_runs,
        ROUND(AVG(i.strike_rate), 2) AS avg_strike_rate
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE i.batting_position > 0 AND EXTRACT(YEAR FROM m.match_date) >= 2020
    GROUP BY p.player_id, p.full_name, EXTRACT(YEAR FROM m.match_date)
    HAVING COUNT(i.innings_id) >= 5
    ORDER BY year DESC, avg_runs DESC;
    """
}

ADVANCED_QUERIES = {
    "Q17_Toss_Advantage": """
    -- Q17: Analyze toss advantage in winning matches
    SELECT 
        CASE WHEN m.toss_winner_choice = 'Bat' THEN 'Batting First' 
             ELSE 'Bowling First' END AS toss_decision,
        COUNT(m.match_id) AS total_matches,
        SUM(CASE WHEN m.toss_winner_id = m.winning_team_id THEN 1 ELSE 0 END) AS toss_winner_wins,
        ROUND(
            (SUM(CASE WHEN m.toss_winner_id = m.winning_team_id THEN 1 ELSE 0 END)::FLOAT 
             / COUNT(m.match_id) * 100), 2
        ) AS win_percentage
    FROM matches m
    WHERE m.match_status = 'Completed'
    GROUP BY toss_decision
    ORDER BY win_percentage DESC;
    """,
    
    "Q18_Economical_Bowlers": """
    -- Q18: Find most economical bowlers in limited-overs cricket
    SELECT 
        p.full_name,
        m.match_format,
        COUNT(DISTINCT m.match_id) AS matches_bowled,
        SUM(i.wickets_taken) AS total_wickets,
        ROUND(AVG(i.economy_rate), 3) AS economy_rate,
        ROUND(AVG(i.overs_bowled), 2) AS avg_overs_per_match
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE m.match_format IN ('ODI', 'T20I') AND i.bowling_position > 0
    GROUP BY p.player_id, p.full_name, m.match_format
    HAVING COUNT(DISTINCT m.match_id) >= 10 
        AND ROUND(AVG(i.overs_bowled), 2) >= 2
    ORDER BY economy_rate ASC
    LIMIT 20;
    """,
    
    "Q19_Consistency_Analysis": """
    -- Q19: Determine most consistent batsmen
    SELECT 
        p.full_name,
        COUNT(i.innings_id) AS total_innings,
        ROUND(AVG(i.runs_scored), 2) AS avg_runs,
        ROUND(STDDEV(i.runs_scored), 2) AS consistency_score
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE i.batting_position > 0 
        AND i.balls_faced >= 10
        AND m.match_date >= CURRENT_DATE - INTERVAL '2 years'
    GROUP BY p.player_id, p.full_name
    HAVING COUNT(i.innings_id) >= 10
    ORDER BY consistency_score ASC, avg_runs DESC;
    """,
    
    "Q20_Format_Match_Counts": """
    -- Q20: Analyze player matches and averages by format
    SELECT 
        p.full_name,
        SUM(CASE WHEN m.match_format = 'Test' THEN 1 ELSE 0 END) AS test_matches,
        ROUND(AVG(CASE WHEN m.match_format = 'Test' THEN i.runs_scored END), 2) AS test_avg,
        SUM(CASE WHEN m.match_format = 'ODI' THEN 1 ELSE 0 END) AS odi_matches,
        ROUND(AVG(CASE WHEN m.match_format = 'ODI' THEN i.runs_scored END), 2) AS odi_avg,
        SUM(CASE WHEN m.match_format = 'T20I' THEN 1 ELSE 0 END) AS t20i_matches,
        ROUND(AVG(CASE WHEN m.match_format = 'T20I' THEN i.runs_scored END), 2) AS t20i_avg
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE i.batting_position > 0
    GROUP BY p.player_id, p.full_name
    HAVING COUNT(DISTINCT m.match_id) >= 20
    ORDER BY test_matches DESC;
    """,
    
    "Q21_Performance_Ranking": """
    -- Q21: Comprehensive performance ranking system
    WITH player_stats AS (
        SELECT 
            p.player_id,
            p.full_name,
            m.match_format,
            SUM(CASE WHEN i.batting_position > 0 THEN i.runs_scored ELSE 0 END) AS runs_scored,
            ROUND(AVG(CASE WHEN i.batting_position > 0 THEN i.runs_scored END), 2) AS batting_avg,
            ROUND(AVG(CASE WHEN i.batting_position > 0 THEN i.strike_rate END), 2) AS strike_rate,
            SUM(CASE WHEN i.bowling_position > 0 THEN i.wickets_taken ELSE 0 END) AS wickets_taken,
            ROUND(AVG(CASE WHEN i.bowling_position > 0 THEN i.bowling_average END), 2) AS bowling_avg,
            ROUND(AVG(CASE WHEN i.bowling_position > 0 THEN i.economy_rate END), 2) AS economy_rate,
            SUM(CASE WHEN i.catches > 0 THEN i.catches ELSE 0 END) AS catches,
            SUM(CASE WHEN i.stumpings > 0 THEN i.stumpings ELSE 0 END) AS stumpings,
            SUM(CASE WHEN i.run_outs > 0 THEN i.run_outs ELSE 0 END) AS run_outs
        FROM players p
        LEFT JOIN innings i ON p.player_id = i.player_id
        LEFT JOIN matches m ON i.match_id = m.match_id
        GROUP BY p.player_id, p.full_name, m.match_format
    )
    SELECT 
        full_name,
        match_format,
        ROUND(
            (runs_scored * 0.01) + (COALESCE(batting_avg, 0) * 0.5) + (COALESCE(strike_rate, 0) * 0.3)
            + (COALESCE(wickets_taken, 0) * 2) + ((6 - COALESCE(economy_rate, 6)) * 2)
            + catches + (stumpings * 2) + (run_outs * 1.5)
        , 2) AS performance_score,
        ROW_NUMBER() OVER (PARTITION BY match_format ORDER BY 
            (runs_scored * 0.01) + (COALESCE(batting_avg, 0) * 0.5) + (COALESCE(strike_rate, 0) * 0.3) DESC
        ) AS rank
    FROM player_stats
    WHERE match_format IS NOT NULL
    ORDER BY match_format, performance_score DESC;
    """,
    
    "Q22_Head_to_Head": """
    -- Q22: Head-to-head analysis between teams
    WITH h2h_matches AS (
        SELECT 
            CASE WHEN t1.team_id < t2.team_id THEN t1.team_id ELSE t2.team_id END AS team_a,
            CASE WHEN t1.team_id < t2.team_id THEN t2.team_id ELSE t1.team_id END AS team_b,
            m.match_id,
            m.winning_team_id,
            m.victory_margin
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        WHERE m.match_date >= CURRENT_DATE - INTERVAL '3 years'
            AND m.match_status = 'Completed'
    )
    SELECT 
        ta.team_name AS team_a,
        tb.team_name AS team_b,
        COUNT(h2h.match_id) AS total_matches,
        SUM(CASE WHEN h2h.winning_team_id = ta.team_id THEN 1 ELSE 0 END) AS team_a_wins,
        SUM(CASE WHEN h2h.winning_team_id = tb.team_id THEN 1 ELSE 0 END) AS team_b_wins,
        ROUND(AVG(h2h.victory_margin), 2) AS avg_victory_margin,
        ROUND(
            (SUM(CASE WHEN h2h.winning_team_id = ta.team_id THEN 1 ELSE 0 END)::FLOAT 
             / COUNT(h2h.match_id) * 100), 2
        ) AS team_a_win_percentage
    FROM h2h_matches h2h
    JOIN teams ta ON h2h.team_a = ta.team_id
    JOIN teams tb ON h2h.team_b = tb.team_id
    GROUP BY ta.team_id, ta.team_name, tb.team_id, tb.team_name
    HAVING COUNT(h2h.match_id) >= 5
    ORDER BY total_matches DESC;
    """,
    
    "Q23_Player_Form_Analysis": """
    -- Q23: Recent player form and momentum analysis
    WITH recent_performance AS (
        SELECT 
            p.full_name,
            i.runs_scored,
            ROW_NUMBER() OVER (PARTITION BY p.player_id ORDER BY m.match_date DESC) AS recency_rank
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        JOIN matches m ON i.match_id = m.match_id
        WHERE i.batting_position > 0
        ORDER BY p.player_id, m.match_date DESC
    )
    SELECT 
        full_name,
        ROUND(AVG(CASE WHEN recency_rank <= 5 THEN runs_scored END), 2) AS last_5_avg,
        ROUND(AVG(CASE WHEN recency_rank <= 10 THEN runs_scored END), 2) AS last_10_avg,
        SUM(CASE WHEN recency_rank <= 10 AND runs_scored > 50 THEN 1 ELSE 0 END) AS fifties_last_10,
        CASE 
            WHEN AVG(CASE WHEN recency_rank <= 5 THEN runs_scored END) > 40 THEN 'Excellent Form'
            WHEN AVG(CASE WHEN recency_rank <= 5 THEN runs_scored END) > 30 THEN 'Good Form'
            WHEN AVG(CASE WHEN recency_rank <= 5 THEN runs_scored END) > 15 THEN 'Average Form'
            ELSE 'Poor Form'
        END AS current_form
    FROM recent_performance
    GROUP BY full_name
    ORDER BY last_5_avg DESC;
    """,
    
    "Q24_Best_Partnerships": """
    -- Q24: Study successful batting partnerships
    WITH partnerships AS (
        SELECT 
            p1.full_name AS batsman_1,
            p2.full_name AS batsman_2,
            COUNT(DISTINCT CONCAT(i1.match_id, i1.innings_id)) AS partnership_count,
            ROUND(AVG(i1.runs_scored + i2.runs_scored), 2) AS avg_partnership_runs,
            MAX(i1.runs_scored + i2.runs_scored) AS highest_partnership,
            SUM(CASE WHEN (i1.runs_scored + i2.runs_scored) >= 50 THEN 1 ELSE 0 END) AS fifties_plus
        FROM innings i1
        JOIN innings i2 ON i1.match_id = i2.match_id 
            AND i1.batting_position + 1 = i2.batting_position
        JOIN players p1 ON i1.player_id = p1.player_id
        JOIN players p2 ON i2.player_id = p2.player_id
        GROUP BY p1.player_id, p1.full_name, p2.player_id, p2.full_name
    )
    SELECT 
        batsman_1,
        batsman_2,
        partnership_count,
        avg_partnership_runs,
        highest_partnership,
        fifties_plus,
        ROUND((fifties_plus::FLOAT / partnership_count * 100), 2) AS success_rate
    FROM partnerships
    WHERE partnership_count >= 5
    ORDER BY success_rate DESC, avg_partnership_runs DESC
    LIMIT 20;
    """,
    
    "Q25_Career_Evolution": """
    -- Q25: Time-series analysis of player performance evolution
    WITH quarterly_stats AS (
        SELECT 
            p.full_name,
            DATE_TRUNC('quarter', m.match_date)::DATE AS quarter,
            COUNT(DISTINCT i.innings_id) AS matches_in_quarter,
            ROUND(AVG(i.runs_scored), 2) AS quarterly_avg,
            ROUND(AVG(i.strike_rate), 2) AS quarterly_strike_rate,
            LAG(ROUND(AVG(i.runs_scored), 2)) OVER 
                (PARTITION BY p.player_id ORDER BY DATE_TRUNC('quarter', m.match_date)) AS prev_quarter_avg
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        JOIN matches m ON i.match_id = m.match_id
        WHERE i.batting_position > 0
        GROUP BY p.player_id, p.full_name, DATE_TRUNC('quarter', m.match_date)
    )
    SELECT 
        full_name,
        quarter,
        matches_in_quarter,
        quarterly_avg,
        quarterly_strike_rate,
        CASE 
            WHEN prev_quarter_avg IS NULL THEN 'First Quarter'
            WHEN quarterly_avg > prev_quarter_avg THEN 'Improving'
            WHEN quarterly_avg < prev_quarter_avg THEN 'Declining'
            ELSE 'Stable'
        END AS trend,
        CASE 
            WHEN ROW_NUMBER() OVER (PARTITION BY full_name ORDER BY quarter DESC) <= 4 
                AND quarterly_avg > 30 THEN 'Career Ascending'
            WHEN ROW_NUMBER() OVER (PARTITION BY full_name ORDER BY quarter DESC) <= 4 
                AND quarterly_avg < 20 THEN 'Career Declining'
            ELSE 'Career Stable'
        END AS career_phase
    FROM quarterly_stats
    WHERE matches_in_quarter >= 3
    ORDER BY full_name, quarter DESC;
    """
}

# Dictionary mapping query levels and names
QUERIES_BY_LEVEL = {
    "Beginner": BEGINNER_QUERIES,
    "Intermediate": INTERMEDIATE_QUERIES,
    "Advanced": ADVANCED_QUERIES
}

def get_query_by_id(query_id):
    """
    Retrieve a specific query by its ID.
    
    Args:
        query_id (str): Query identifier (e.g., 'Q1_Indian_Players', 'Q9_Allrounders_Stats')
    
    Returns:
        str: SQL query string or None if not found
    """
    for queries in [BEGINNER_QUERIES, INTERMEDIATE_QUERIES, ADVANCED_QUERIES]:
        if query_id in queries:
            return queries[query_id]
    return None

def get_all_queries():
    """Returns all 25 queries organized by difficulty level."""
    return QUERIES_BY_LEVEL
