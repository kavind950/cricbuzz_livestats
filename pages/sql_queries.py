import streamlit as st
import pandas as pd
from utils.db_connection import get_connection, execute_query
from utils.sql_queries_bank import BEGINNER_QUERIES, INTERMEDIATE_QUERIES, ADVANCED_QUERIES

def show_sql_queries():
    """Display SQL queries interface with predefined queries and custom query runner."""
    
    st.header("🧮 SQL Analytics & Queries")
    
    st.write("""
    Explore 25 comprehensive SQL queries organized by difficulty level (Beginner → Intermediate → Advanced),
    or write your own custom SQL queries to analyze cricket data.
    """)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🟢 Beginner Queries (1-8)",
        "🟡 Intermediate Queries (9-16)",
        "🔴 Advanced Queries (17-25)",
        "📝 Custom Query",
        "📚 Query Documentation"
    ])
    
    with tab1:
        show_query_level("Beginner", BEGINNER_QUERIES)
    
    with tab2:
        show_query_level("Intermediate", INTERMEDIATE_QUERIES)
    
    with tab3:
        show_query_level("Advanced", ADVANCED_QUERIES)
    
    with tab4:
        show_custom_query()
    
    with tab5:
        show_documentation()


def show_query_level(level, queries_dict):
    """Display queries for a specific difficulty level."""
    
    st.subheader(f"{level} Level Queries")
    
    if not queries_dict:
        st.warning("No queries available for this level")
        return
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_query = st.selectbox(
            "Select a query:",
            list(queries_dict.keys()),
            key=f"query_select_{level}"
        )
    
    with col2:
        if st.button("▶️ Run Query", key=f"run_{level}"):
            st.session_state[f"run_{level}_clicked"] = True
    
    # Display query description and SQL
    if selected_query:
        query_sql = queries_dict[selected_query]
        
        # Extract description from comment
        lines = query_sql.strip().split('\n')
        description = lines[0].replace('--', '').strip() if lines[0].startswith('--') else "No description"
        
        st.write(f"**Description:** {description}")
        
        # Show SQL code
        with st.expander("📄 View SQL Query"):
            st.code(query_sql, language="sql")
        
        # Run query if button was clicked
        if st.session_state.get(f"run_{level}_clicked"):
            with st.spinner("Executing query..."):
                try:
                    data = execute_query(query_sql, fetch=True)
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.success(f"✅ Query executed successfully! ({len(df)} rows)")
                        
                        # Display results
                        st.subheader("Query Results")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Download option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"{selected_query}_results.csv",
                            mime="text/csv",
                            key=f"download_{level}"
                        )
                        
                        # Display summary statistics
                        st.subheader("📊 Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Rows", len(df))
                        with col2:
                            st.metric("Columns", len(df.columns))
                        with col3:
                            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                        with col4:
                            st.metric("Data Types", len(df.dtypes.unique()))
                    else:
                        st.warning("Query returned no results")
                
                except Exception as e:
                    st.error(f"❌ Query Error: {str(e)}")
                    st.info("Make sure your database connection is configured correctly")
                
                # Reset button state
                st.session_state[f"run_{level}_clicked"] = False


def show_custom_query():
    """Display custom query interface."""
    
    st.subheader("📝 Write Your Own Query")
    
    st.write("""
    Write custom SQL queries to explore the cricket database.
    The database includes tables like: players, matches, innings, teams, venues, series, partnerships
    """)
    
    # Query templates
    with st.expander("💡 Query Templates"):
        st.markdown("""
        **Select from Players:**
        ```sql
        SELECT * FROM players LIMIT 10;
        ```
        
        **Count by Playing Role:**
        ```sql
        SELECT playing_role, COUNT(*) as count FROM players GROUP BY playing_role;
        ```
        
        **Recent Matches:**
        ```sql
        SELECT * FROM matches ORDER BY match_date DESC LIMIT 5;
        ```
        
        **Player Stats:**
        ```sql
        SELECT p.full_name, COUNT(i.innings_id) as matches, 
               SUM(i.runs_scored) as total_runs 
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        GROUP BY p.player_id, p.full_name
        ORDER BY total_runs DESC LIMIT 20;
        ```
        """)
    
    # Query input
    custom_query = st.text_area(
        "Enter your SQL query:",
        value="SELECT * FROM players LIMIT 10;",
        height=200,
        key="custom_query"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        run_custom = st.button("▶️ Execute Query", key="run_custom")
    
    with col2:
        st.write("")  # Spacing
    
    # Execute custom query
    if run_custom:
        if not custom_query.strip():
            st.warning("Please enter a SQL query")
            return
        
        # Security check - warn about dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        if any(keyword in custom_query.upper() for keyword in dangerous_keywords):
            st.warning("⚠️ This query contains potentially dangerous operations. "
                      "Use with caution in production environments!")
        
        with st.spinner("Executing query..."):
            try:
                data = execute_query(custom_query, fetch=True)
                
                if data:
                    df = pd.DataFrame(data)
                    st.success(f"✅ Query executed successfully! ({len(df)} rows returned)")
                    
                    # Display results
                    st.subheader("Results")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
                    
                    # Display statistics
                    if len(df) > 0:
                        st.subheader("📈 Data Preview")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Rows:** {len(df)}")
                            st.write(f"**Columns:** {len(df.columns)}")
                        with col2:
                            st.write(f"**Data Types:**")
                            st.write(df.dtypes)
                else:
                    st.warning("Query returned no results")
            
            except Exception as e:
                st.error(f"❌ Query Error: {str(e)}")
                st.info("""
                **Troubleshooting:**
                - Check SQL syntax is correct
                - Verify table and column names exist
                - Ensure database connection is configured
                - Check user permissions for the database
                """)


def show_documentation():
    """Display documentation about available queries and database schema."""
    
    st.subheader("📚 Query Documentation")
    
    tabs = st.tabs(["Overview", "Database Schema", "Query Guide", "Tips & Tricks"])
    
    with tabs[0]:
        st.write("""
        ### 25 SQL Queries for Cricket Analytics
        
        This dashboard includes **25 comprehensive SQL queries** that demonstrate various SQL techniques:
        
        **Beginner Queries (Questions 1-8)** - *Basic SQL Operations*
        - Simple SELECT statements
        - WHERE clause filtering
        - GROUP BY and ORDER BY
        - DISTINCT and sorting
        
        **Intermediate Queries (Questions 9-16)** - *Advanced Filtering*
        - JOIN operations (INNER, LEFT, FULL OUTER)
        - Subqueries and CTEs
        - Aggregate functions (SUM, COUNT, AVG, MAX)
        - HAVING clause
        
        **Advanced Queries (Questions 17-25)** - *Complex Analytics*
        - Window functions (ROW_NUMBER, LAG, LEAD)
        - Common Table Expressions (WITH)
        - Complex aggregations
        - Multi-level grouping
        """)
    
    with tabs[1]:
        st.write("""
        ### Database Schema Overview
        
        **Tables:**
        1. **players** - Player information and basic details
           - Columns: player_id, full_name, country, playing_role, batting_style, bowling_style
        
        2. **matches** - Cricket match records
           - Columns: match_id, team1_id, team2_id, venue_id, match_date, match_format, match_status
        
        3. **innings** - Individual innings performance
           - Columns: innings_id, match_id, player_id, runs_scored, wickets_taken, strike_rate
        
        4. **teams** - International cricket teams
           - Columns: team_id, team_name, country, coach, captain
        
        5. **venues** - Cricket stadiums and grounds
           - Columns: venue_id, venue_name, city, country, seating_capacity
        
        6. **series** - Cricket series and tournaments
           - Columns: series_id, series_name, host_country, match_type, start_date
        
        7. **partnerships** - Batting pair statistics
           - Columns: partnership_id, player1_id, player2_id, total_runs, matches
        """)
    
    with tabs[2]:
        st.write("""
        ### Query Writing Guide
        
        **Beginner Level Tips:**
        - Use SELECT to retrieve columns
        - Use WHERE to filter rows
        - Use ORDER BY to sort results
        - Use GROUP BY to aggregate data
        
        Example:
        ```sql
        SELECT country, COUNT(*) as player_count
        FROM players
        GROUP BY country
        ORDER BY player_count DESC;
        ```
        
        **Intermediate Level Tips:**
        - Use JOIN to combine data from multiple tables
        - Use subqueries for complex filtering
        - Use aggregate functions effectively
        - Use HAVING to filter grouped data
        
        Example:
        ```sql
        SELECT p.full_name, SUM(i.runs_scored) as total_runs
        FROM players p
        JOIN innings i ON p.player_id = i.player_id
        WHERE i.runs_scored > 0
        GROUP BY p.player_id, p.full_name
        HAVING SUM(i.runs_scored) > 1000;
        ```
        
        **Advanced Level Tips:**
        - Use window functions for ranking
        - Use CTEs for readable complex queries
        - Combine multiple grouping levels
        - Use CASE statements for conditional logic
        
        Example:
        ```sql
        WITH player_stats AS (
            SELECT p.full_name,
                   ROW_NUMBER() OVER (ORDER BY SUM(i.runs_scored) DESC) as rank
            FROM players p
            JOIN innings i ON p.player_id = i.player_id
            GROUP BY p.player_id, p.full_name
        )
        SELECT * FROM player_stats WHERE rank <= 10;
        ```
        """)
    
    with tabs[3]:
        st.write("""
        ### Query Writing Tips & Tricks
        
        **Performance Optimization:**
        - ✅ Use indices on frequently queried columns
        - ✅ Avoid SELECT * - specify needed columns
        - ✅ Use LIMIT to test before running full queries
        - ❌ Avoid nested subqueries when JOINs work better
        
        **Data Quality:**
        - 🔍 Check for NULL values using IS NULL / IS NOT NULL
        - 🔍 Validate data types match expectations
        - 🔍 Use aggregation carefully to avoid unexpected results
        - 🔍 Test queries with small datasets first
        
        **Common Patterns:**
        - Ranking: `ROW_NUMBER() OVER (ORDER BY column DESC)`
        - Moving average: `AVG() OVER (ORDER BY date ROWS BETWEEN ...)`
        - Running total: `SUM() OVER (ORDER BY date)`
        - Year-over-year: `EXTRACT(YEAR FROM date_column)`
        
        **Debugging:**
        - Start simple, then add complexity
        - Test intermediate results
        - Check WHERE clause conditions
        - Verify JOIN conditions
        - Look for data type mismatches
        """)


# Initialize session state for buttons
if "run_Beginner_clicked" not in st.session_state:
    st.session_state.run_Beginner_clicked = False
if "run_Intermediate_clicked" not in st.session_state:
    st.session_state.run_Intermediate_clicked = False
if "run_Advanced_clicked" not in st.session_state:
    st.session_state.run_Advanced_clicked = False
