# 📚 SQL Queries Page - Complete Guide for Beginners

## Table of Contents
1. [Overview](#overview)
2. [Page Architecture](#page-architecture)
3. [How the Code Works](#how-the-code-works)
4. [Function Explanations](#function-explanations)
5. [SQL Query Guide](#sql-query-guide)
6. [Step-by-Step Flow](#step-by-step-flow)
7. [25 SQL Queries Explained](#25-sql-queries-explained)

---

## Overview

The **SQL Queries Page** is an interactive interface in the Cricbuzz app that lets users:
- ✅ Run pre-built SQL queries organized by difficulty (Beginner → Intermediate → Advanced)
- ✅ Write and execute custom SQL queries
- ✅ View results in a table format
- ✅ Download results as CSV
- ✅ Learn SQL through examples

**Goal:** Help cricket data analysts explore the database and perform analytics without needing to connect to the database directly.

---

## Page Architecture

### Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│        🧮 SQL Analytics & Queries                           │
│   [Description of the page]                                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Tabs                                                          │
├──────────────────────────────────────────────────────────────┤
│ [🟢 Beginner] [🟡 Intermediate] [🔴 Advanced]               │
│ [📝 Custom Query] [📚 Query Documentation]                  │
└──────────────────────────────────────────────────────────────┘

INSIDE EACH TAB:
┌──────────────────────────────────────────────────────────────┐
│ Level Queries (e.g., "Beginner Level Queries")              │
│                                                              │
│ [Dropdown: Select a query] [▶️ Run Query Button]            │
│                                                              │
│ **Description:** [Shows query purpose]                       │
│                                                              │
│ [📄 View SQL Query] ← Click to see SQL code               │
│                                                              │
│ [Query Results Table] with statistics & CSV download        │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

```
Streamlit (Frontend)
    ↓
sql_queries.py (Page Logic)
    ↓
┌─────────────────────────────┐
│ Predefined Queries:         │
│ - sql_queries_bank.py       │
│ - 25 queries organized      │
│   by difficulty level       │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Database Connection:        │
│ - db_connection.py          │
│ - execute_query()           │
│ - get PostgreSQL data       │
└─────────────────────────────┘
    ↓
PostgreSQL Database (Backend)
```

---

## How the Code Works

### Import Statements (Beginning of file)

```python
import streamlit as st              # UI framework
import pandas as pd                 # Data manipulation & tables
from utils.db_connection import get_connection, execute_query  # Database functions
from utils.sql_queries_bank import BEGINNER_QUERIES, INTERMEDIATE_QUERIES, ADVANCED_QUERIES
# Import dictionaries containing all pre-built SQL queries
```

**What does each import do?**

| Import | Purpose |
|--------|---------|
| `streamlit as st` | Creates interactive UI (buttons, dropdowns, tables) |
| `pandas as pd` | Converts database results into tables & statistics |
| `execute_query()` | Runs SQL queries on the database |
| `BEGINNER_QUERIES` | Dictionary: `{"Query Name": "SELECT ...", ...}` |

### High-Level Flow

```
USER VISITS SQL PAGE
    ↓
Page displays 5 tabs
(Beginner, Intermediate, Advanced, Custom, Documentation)
    ↓
USER SELECTS A TAB
    ↓
┌─────────────────────────────────────────┐
│ IF Beginner/Intermediate/Advanced Tab:  │
│  - Load queries from queries_bank.py   │
│  - Show dropdown to select query       │
│  - Show "Run Query" button             │
│  - Wait for user to click button       │
│                                         │
│ IF Custom Query Tab:                   │
│  - Show text area for SQL input        │
│  - User types their own SQL            │
│  - Show "Execute Query" button         │
│                                         │
│ IF Documentation Tab:                  │
│  - Show helpful tips & examples        │
│  - Show database schema                │
└─────────────────────────────────────────┘
    ↓
USER CLICKS "RUN QUERY" / "EXECUTE QUERY"
    ↓
execute_query(sql_code) → PostgreSQL Database
    ↓
Database returns results (rows of data)
    ↓
Convert to Pandas DataFrame (table)
    ↓
Display results with:
  - Table view
  - Statistics (rows, columns, memory usage)
  - CSV download button
```

---

## Function Explanations

### 1. `show_sql_queries()` - Main Page Function

**What it does:** This is the entry point function. It creates the main page structure and tabs.

```python
def show_sql_queries():
    """Display SQL queries interface with predefined queries and custom query runner."""
    
    # Step 1: Show header and description
    st.header("🧮 SQL Analytics & Queries")
    st.write("[Description text]")
    
    # Step 2: Create 5 tabs (navigation)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🟢 Beginner Queries (1-8)",
        "🟡 Intermediate Queries (9-16)",
        "🔴 Advanced Queries (17-25)",
        "📝 Custom Query",
        "📚 Query Documentation"
    ])
    
    # Step 3: Fill each tab with content
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
```

**Analogy:** Think of this function as creating a book with 5 chapters. Each chapter contains different content.

**What happens line by line:**
1. Creates a header: "🧮 SQL Analytics & Queries"
2. Shows description text
3. Creates 5 tabs (like folder tabs)
4. Fills each tab by calling other functions

---

### 2. `show_query_level()` - Display Beginner/Intermediate/Advanced Queries

**What it does:** Shows queries for a specific difficulty level with dropdowns and execution interface.

```python
def show_query_level(level, queries_dict):
    """
    Input:
      - level: "Beginner" or "Intermediate" or "Advanced" (string)
      - queries_dict: {
          "Q1_Indian_Players": "SELECT ...",
          "Q2_Recent_Matches": "SELECT ...",
          ...
        }
    
    Output:
      - Interactive UI with dropdowns and results table
    """
    
    # Step 1: Show subheader
    st.subheader(f"{level} Level Queries")
    
    # Step 2: Check if queries exist
    if not queries_dict:
        st.warning("No queries available for this level")
        return  # Exit function if no queries
    
    # Step 3: Create 2 columns layout (dropdown on left, button on right)
    col1, col2 = st.columns([3, 1])
    #         ↑ Col1 takes 3/4 of space
    #                  ↑ Col2 takes 1/4 of space
    
    # Step 4: Dropdown to select which query to run
    with col1:
        selected_query = st.selectbox(
            "Select a query:",
            list(queries_dict.keys()),  # Example: ["Q1_Indian_Players", "Q2_Recent_Matches", ...]
            key=f"query_select_{level}"  # Unique ID for this dropdown
        )
    
    # Step 5: Run button
    with col2:
        if st.button("▶️ Run Query", key=f"run_{level}"):
            st.session_state[f"run_{level}_clicked"] = True
            # Note: st.session_state = "memory" of what happened before
    
    # Step 6: Extract and display query description
    if selected_query:
        query_sql = queries_dict[selected_query]  # Get the full SQL code
        
        # SQL queries start with a comment: "-- Q1: Find all Indian players"
        # We extract this comment as a description
        lines = query_sql.strip().split('\n')  # Split by newline
        description = lines[0].replace('--', '').strip() if lines[0].startswith('--') else "No description"
        
        st.write(f"**Description:** {description}")
        
        # Show SQL code in expandable box
        with st.expander("📄 View SQL Query"):
            st.code(query_sql, language="sql")
        
        # Step 7: Run the query if button was clicked
        if st.session_state.get(f"run_{level}_clicked"):
            with st.spinner("Executing query..."):  # Show loading message
                try:
                    # Execute the SQL query
                    data = execute_query(query_sql, fetch=True)
                    
                    if data:  # If query returned results
                        df = pd.DataFrame(data)  # Convert to table
                        st.success(f"✅ Query executed successfully! ({len(df)} rows)")
                        
                        # DISPLAY RESULTS TABLE
                        st.subheader("Query Results")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # CSV DOWNLOAD BUTTON
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"{selected_query}_results.csv",
                            mime="text/csv",
                            key=f"download_{level}"
                        )
                        
                        # DISPLAY SUMMARY STATISTICS
                        st.subheader("📊 Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Rows", len(df))  # How many rows
                        with col2:
                            st.metric("Columns", len(df.columns))  # How many columns
                        with col3:
                            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                        with col4:
                            st.metric("Data Types", len(df.dtypes.unique()))
                    else:
                        st.warning("Query returned no results")
                
                except Exception as e:
                    st.error(f"❌ Query Error: {str(e)}")
                    st.info("Make sure your database connection is configured correctly")
                
                # Reset button state (so query doesn't run again on next refresh)
                st.session_state[f"run_{level}_clicked"] = False
```

**Flow Diagram:**

```
User clicks "Run Query" button
    ↓
Set session_state flag: run_Beginner_clicked = True
    ↓
Page refreshes (Streamlit reruns)
    ↓
Check: Is run_Beginner_clicked == True?
    ↓
YES → Execute SQL query
    ↓
    ├─ If successful:
    │   ├─ Convert results to table
    │   ├─ Display table
    │   ├─ Show statistics (rows, columns, memory)
    │   └─ Show CSV download button
    │
    └─ If error:
        └─ Show error message
    ↓
Set run_Beginner_clicked = False
    ↓
Done
```

---

### 3. `show_custom_query()` - Custom SQL Query Execution

**What it does:** Lets users write their own SQL queries and execute them.

```python
def show_custom_query():
    """Allow users to write and run custom SQL queries."""
    
    # Step 1: Show description
    st.subheader("📝 Write Your Own Query")
    st.write("Write custom SQL queries to explore the cricket database...")
    
    # Step 2: Show SQL templates for help
    with st.expander("💡 Query Templates"):
        st.markdown("""
        **Template 1 - Select from Players:**
        ```sql
        SELECT * FROM players LIMIT 10;
        ```
        
        **Template 2 - Count by Playing Role:**
        ```sql
        SELECT playing_role, COUNT(*) as count 
        FROM players 
        GROUP BY playing_role;
        ```
        
        [More templates...]
        """)
    
    # Step 3: Text area where user types SQL
    custom_query = st.text_area(
        "Enter your SQL query:",
        value="SELECT * FROM players LIMIT 10;",  # Default value
        height=200  # Box height in pixels
    )
    
    # Step 4: Create buttons (Execute Query button)
    col1, col2 = st.columns(2)
    
    with col1:
        run_custom = st.button("▶️ Execute Query", key="run_custom")
    
    # Step 5: Execute if button clicked
    if run_custom:
        # Check if query is empty
        if not custom_query.strip():
            st.warning("Please enter a SQL query")
            return
        
        # Safety check: Warn about dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        if any(keyword in custom_query.upper() for keyword in dangerous_keywords):
            st.warning("⚠️ This query contains potentially dangerous operations. Use with caution!")
        
        # Execute the query
        with st.spinner("Executing query..."):
            try:
                data = execute_query(custom_query, fetch=True)
                
                if data:
                    df = pd.DataFrame(data)
                    st.success(f"✅ Query executed successfully! ({len(df)} rows)")
                    
                    # Display results
                    st.subheader("Results")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # CSV download
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
                """)
```

**Analogy:** This is like a "freestyle mode" where users can experiment with their own SQL queries.

---

### 4. `show_documentation()` - Help & Educational Content

**What it does:** Shows documentation about database schema, query tips, and examples.

```python
def show_documentation():
    """Display helpful documentation and schema information."""
    
    st.subheader("📚 Query Documentation")
    
    # Create 4 tab sections within documentation
    tabs = st.tabs(["Overview", "Database Schema", "Query Guide", "Tips & Tricks"])
    
    with tabs[0]:
        # Show 25 queries overview, organized by level
        st.write("""
        ### 25 SQL Queries for Cricket Analytics
        
        **Beginner Queries (1-8):**
        - Simple SELECT, WHERE, ORDER BY, GROUP BY
        
        **Intermediate Queries (9-16):**
        - JOINs, subqueries, aggregate functions
        
        **Advanced Queries (17-25):**
        - Window functions, CTEs, complex analytics
        """)
    
    with tabs[1]:
        # Database schema explanation
        st.write("""
        ### Database Tables
        
        1. **players**: player_id, full_name, country, playing_role
        2. **matches**: match_id, team1_id, team2_id, venue_id, match_date
        3. **innings**: innings_id, match_id, player_id, runs_scored, wickets_taken
        [More tables...]
        """)
    
    with tabs[2]:
        # SQL writing guide with examples
        st.write("[SQL techniques with examples]")
    
    with tabs[3]:
        # Tips and tricks
        st.write("[Performance optimization tips]")
```

---

## SQL Query Guide

### What is SQL?

**SQL (Structured Query Language)** = A language to talk to databases.

Think of it like giving instructions to a restaurant:
- **"Give me all menu items"** = `SELECT * FROM menu;`
- **"Give me all pizza items"** = `SELECT * FROM menu WHERE category = 'Pizza';`
- **"Count items in each category"** = `SELECT category, COUNT(*) FROM menu GROUP BY category;`

### Basic SQL Concepts

#### 1. SELECT - Get Data

```sql
-- Get all columns from players table
SELECT * FROM players;

-- Get specific columns
SELECT full_name, country FROM players;

-- Rename column in results
SELECT full_name AS "Player Name" FROM players;
```

#### 2. WHERE - Filter Data

```sql
-- Only Indian players
SELECT * FROM players WHERE country = 'India';

-- Runs > 1000
SELECT * FROM innings WHERE runs_scored > 1000;

-- Multiple conditions
SELECT * FROM players 
WHERE country = 'India' AND playing_role = 'Batsman';
```

#### 3. ORDER BY - Sort Data

```sql
-- Sort by runs (ascending)
SELECT * FROM innings ORDER BY runs_scored ASC;

-- Sort by runs (descending - highest first)
SELECT * FROM innings ORDER BY runs_scored DESC;

-- Sort by multiple columns
SELECT * FROM matches ORDER BY match_date DESC, match_id ASC;
```

#### 4. GROUP BY - Summarize Data

```sql
-- Count players from each country
SELECT country, COUNT(*) as player_count 
FROM players 
GROUP BY country;

-- Total runs per player
SELECT 
    player_id, 
    full_name,
    SUM(runs_scored) as total_runs 
FROM innings 
GROUP BY player_id, full_name;
```

#### 5. JOIN - Combine Tables

```sql
-- Get player name and their runs (combines two tables)
SELECT 
    p.full_name,        -- From players table
    i.runs_scored       -- From innings table
FROM players p
INNER JOIN innings i ON p.player_id = i.player_id;
-- ↑ Connect using player_id
```

**Visual Example:**

```
players table:
┌──────────┬────────────┬─────────┐
│ player_id│ full_name  │ country │
├──────────┼────────────┼─────────┤
│ 1        │ Virat      │ India   │
│ 2        │ Root       │ England │
└──────────┴────────────┴─────────┘

innings table:
┌───────────┬───────────┬─────────────┐
│ innings_id│ player_id │ runs_scored │
├───────────┼───────────┼─────────────┤
│ 1         │ 1         │ 100         │
│ 2         │ 1         │ 50          │
│ 3         │ 2         │ 80          │
└───────────┴───────────┴─────────────┘

AFTER JOIN:
┌────────────┬─────────────┐
│ full_name  │ runs_scored │
├────────────┼─────────────┤
│ Virat      │ 100         │
│ Virat      │ 50          │
│ Root       │ 80          │
└────────────┴─────────────┘
```

#### 6. Aggregate Functions - Calculate

```sql
-- COUNT: How many rows
SELECT COUNT(*) FROM players;  -- Answer: 500

-- SUM: Add up all values
SELECT SUM(runs_scored) FROM innings;  -- Answer: 1000000

-- AVG: Average
SELECT AVG(runs_scored) FROM innings;  -- Answer: 35.5

-- MAX/MIN: Highest/Lowest
SELECT MAX(runs_scored) FROM innings;  -- Answer: 250
SELECT MIN(runs_scored) FROM innings;  -- Answer: 0
```

---

## Step-by-Step Flow

### Scenario: User wants to find "Top 10 ODI Scorers"

**User's Journey:**

```
1. User opens Cricbuzz app
   ↓
2. Clicks on "SQL Analytics & Queries" page
   ↓
3. Sees 5 tabs + description
   ↓
4. Clicks "🟢 Beginner Queries" tab
   ↓
5. Page shows:
   - Dropdown: "Select a query"
   - Button: "▶️ Run Query"
   ↓
6. User clicks dropdown and selects "Q3_Top_10_ODI_Scorers"
   ↓
7. Description appears: "List top 10 highest run scorers in ODI cricket"
   ↓
8. User clicks "📄 View SQL Query" to see the code
   ↓
9. User clicks "▶️ Run Query" button
   ↓
10. Streamlit calls: execute_query(query_sql)
    ↓
    Database receives SQL query
    ↓
    Database searches players table, joins with innings table
    ↓
    Calculates SUM(runs), COUNT(matches), AVG(runs)
    ↓
    Database returns 10 rows of results
    ↓
11. Results converted to Pandas DataFrame (table)
    ↓
12. Page displays:
    ✅ Success message: "Query executed successfully! (10 rows)"
    │
    ├─ Table:
    │  ┌─────┬──────────┬───────────┬───────────────┐
    │  │ P#  │ Name     │ Total Runs│ Bat Average   │
    │  └─────┴──────────┴───────────┴───────────────┘
    │
    ├─ 📊 Summary Statistics:
    │  ├─ Total Rows: 10
    │  ├─ Columns: 6
    │  ├─ Memory Usage: 2.45 KB
    │  └─ Data Types: 4
    │
    └─ 📥 Download as CSV button
    ↓
13. Session state: run_Beginner_clicked = False
    (Query won't run again unless button clicked again)
    ↓
14. User is happy! 😊
```

---

## 25 SQL Queries Explained

### Database Schema (What tables exist)

```
┌─────────────────────────────────────────────────────────────┐
│                    CRICBUZZ DATABASE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 players          🏆 teams            🎯 matches        │
│  ├─ player_id       ├─ team_id         ├─ match_id        │
│  ├─ full_name       ├─ team_name       ├─ team1_id        │
│  ├─ country         ├─ coach           ├─ team2_id        │
│  ├─ playing_role    ├─ captain         ├─ venue_id        │
│  ├─ batting_style   └─ country         ├─ match_date      │
│  └─ bowling_style                      ├─ match_status    │
│                                        └─ winning_team_id │
│                                                             │
│  🏟️ venues          📊 innings         🎭 series          │
│  ├─ venue_id       ├─ innings_id      ├─ series_id       │
│  ├─ venue_name     ├─ match_id        ├─ series_name     │
│  ├─ city           ├─ player_id       ├─ host_country    │
│  ├─ country        ├─ runs_scored     └─ start_date      │
│  └─ seating_        ├─ wickets_taken                      │
│     capacity       ├─ strike_rate                         │
│                    └─ economy_rate                        │
│                                                             │
│  🤝 partnerships                                           │
│  ├─ partnership_id                                        │
│  ├─ player1_id                                            │
│  ├─ player2_id                                            │
│  └─ total_runs                                            │
└─────────────────────────────────────────────────────────────┘
```

### BEGINNER QUERIES (Q1-Q8)

#### Q1: Find all Indian players

**Query:**
```sql
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
```

**What it does:**
1. Look at `players` table
2. Filter: Keep only rows where `country = 'India'`
3. Get these columns: player_id, full_name, playing_role, batting_style, bowling_style, country
4. Sort alphabetically by full_name

**Results look like:**
```
┌──────────┬────────────┬──────────────┬───────────────┬────────────────┬─────────┐
│player_id │ full_name  │playing_role  │batting_style  │bowling_style   │country  │
├──────────┼────────────┼──────────────┼───────────────┼────────────────┼─────────┤
│1         │Agarwal     │Batsman       │Right-handed   │NULL            │India    │
│2         │Ashwin      │All-rounder   │Right-handed   │Right-arm       │India    │
│3         │Dhoni       │Wicket-keeper│Right-handed   │NULL            │India    │
│...       │...         │...           │...            │...             │...      │
└──────────┴────────────┴──────────────┴───────────────┴────────────────┴─────────┘
```

---

#### Q2: Recent matches (last 7 days)

**Query:**
```sql
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
```

**What it does:**
1. Look at `matches` table
2. Join with `teams` to get team names (twice - for team1 & team2)
3. Join with `venues` to get venue info
4. Filter: Keep only matches from last 7 days
5. Sort by date (newest first)

**Explanation of JOINs:**
- `m.team1_id = t1.team_id` → Connects team1_id in matches to team_id in teams
- `m.team2_id = t2.team_id` → Connects team2_id in matches to teams again (for team 2)
- `m.venue_id = v.venue_id` → Connects venue_id to get venue name

**Results:**
```
┌──────────┬──────────────┬───────────┬───────────┬──────────────┬────────┬───────────┐
│match_id  │description   │team_1     │team_2     │venue_name    │city    │date      │
├──────────┼──────────────┼───────────┼───────────┼──────────────┼────────┼───────────┤
│M1        │India vs...   │India      │Australia  │MCG           │Melbourne│21 Mar    │
│M2        │England vs... │England    │New Zealand│Lords         │London │20 Mar    │
└──────────┴──────────────┴───────────┴───────────┴──────────────┴────────┴───────────┘
```

---

#### Q3: Top 10 ODI run scorers

**Query:**
```sql
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
```

**What it does:**
1. Join players → innings → matches
2. Filter: Only ODI matches where batting_position > 0
3. Group by player (calculate stats per player):
   - `SUM(runs_scored)` = Total runs
   - `COUNT(innings)` = How many innings
   - `AVG(runs_scored)` = Average per innings
   - Count centuries (runs >= 100)
4. Sort by total_runs (highest first)
5. Get top 10 only

**New Concepts:**
- `GROUP BY` = Combine rows of same player
- `SUM/COUNT/AVG` = Aggregate functions (work on groups)
- `CASE WHEN` = If condition, count it
- `ROUND(..., 2)` = Round to 2 decimal places
- `LIMIT 10` = Get only first 10 rows

**Results:**
```
┌──────────┬──────────┬────────────┬───────────────┬──────────────┬──────────┐
│player_id │full_name │total_runs  │matches_played │batting_avg   │centuries │
├──────────┼──────────┼────────────┼───────────────┼──────────────┼──────────┤
│1         │Virat K.  │15237       │285            │53.45         │46        │
│2         │Kumar S.  │14722       │250            │58.88         │51        │
│3         │Tendulkar │21999       │463            │50.22         │49        │
│...       │...       │...         │...            │...           │...       │
└──────────┴──────────┴────────────┴───────────────┴──────────────┴──────────┘
```

---

#### Q4: Large capacity venues

**Query:**
```sql
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
```

**What it does:**
1. Get all venues
2. Filter: Keep only venues with capacity > 25,000
3. Sort by capacity (largest first)
4. Show top 10

**Simple Query Structure:**
- Only 1 table (no JOINs needed)
- Simple WHERE filter
- Simple ORDER BY + LIMIT

---

#### Q5: Team wins count

**Query:**
```sql
SELECT 
    t.team_id,
    t.team_name,
    COUNT(m.match_id) AS total_wins
FROM teams t
LEFT JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
    AND m.winning_team_id = t.team_id
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;
```

**What it does:**
1. Get all teams
2. For each team, count matches where:
   - Team was team1 OR team2
   - AND team won the match
3. Group by team
4. Sort by wins (highest first)

**Key Concept - LEFT JOIN:**
- Regular JOIN (INNER): Only includes matching records
- LEFT JOIN: Includes all records from left table, even if no match

**Analogy:**
```
Teams:        Matches:
India         Match1: India vs Australia, winner: India ✓
Australia     Match2: India vs England, winner: England ✗
England       Match3: Australia vs England, winner: Australia ✓

Result:
India: 1 win
Australia: 1 win
England: 0 wins
```

---

#### Q6: Count players by role

**Query:**
```sql
SELECT 
    playing_role,
    COUNT(player_id) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;
```

**What it does:**
1. Get all players
2. Group by `playing_role` (Batsman, Bowler, All-rounder, Wicket-keeper)
3. Count players in each group
4. Sort by count (highest first)

**Results:**
```
playing_role    │ player_count
────────────────┼──────────────
Batsman         │ 200
All-rounder     │ 150
Bowler          │ 120
Wicket-keeper   │ 30
```

---

#### Q7: Highest score by format

**Query:**
```sql
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
```

**What it does:**
1. Join innings → players → matches → venues
2. Filter: Only batting innings (batting_position > 0)
3. Find MAX run score for each format
4. Group and sort

---

#### Q8: Cricket series in 2024

**Query:**
```sql
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
```

**What it does:**
1. Get all series
2. Filter: Only series that started in 2024
3. Sort by start_date (newest first)

**New Concept:**
- `EXTRACT(YEAR FROM date)` = Get just the year from a date
- Example: `EXTRACT(YEAR FROM '2024-03-25') = 2024`

---

### INTERMEDIATE QUERIES (Q9-Q16)

#### Q9: All-rounders with 1000+ runs and 50+ wickets

**Query:**
```sql
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
```

**What it does:**
1. Join players → innings → matches
2. Use `CASE WHEN` to separate batting and bowling stats:
   - If `batting_position > 0`: Count as runs
   - If `bowling_position > 0`: Count as wickets
3. Group by player and format
4. **HAVING clause**: Filter groups that meet criteria
   - `total_runs > 1000`
   - `total_wickets > 50`
5. Sort by runs

**New Concepts:**
- `CASE WHEN ... THEN ... ELSE ... END` = Conditional logic
- `HAVING` = Filter groups (like WHERE but for grouped data)

**Difference between WHERE and HAVING:**
- `WHERE` = Filters individual rows BEFORE grouping
- `HAVING` = Filters groups AFTER grouping

---

#### Q10: Last 20 completed matches

**Query:**
```sql
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
```

**What it does:**
1. Join matches → teams (3 times for team1, team2, and winner)
2. Join with venues
3. Filter: Only completed matches
4. Sort by date (newest first)
5. Limit to 20

**Note:** Uses `LEFT JOIN` for winning_team because some matches might not have a winner (cancelled, etc.)

---

#### Q11: Player format performance comparison

**Query:**
```sql
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
```

**What it does:**
1. For each player, calculate runs in EACH format:
   - Test cricket runs
   - ODI runs
   - T20I runs
2. Calculate overall average across all formats
3. Filter: Only players who played >= 2 formats
4. Sort by overall average

**This shows player versatility across different formats.**

---

### ADVANCED QUERIES (Q17-Q25)

#### Q17: Toss advantage analysis

**Query:**
```sql
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
```

**What it does:**
1. Group matches by toss decision (Bat or Bowl)
2. For each group, count:
   - Total matches
   - Matches won by toss winner
3. Calculate win percentage
4. Sort by win percentage

**Insight:** Shows whether batting first or bowling first is an advantage

**Results Example:**
```
Toss Decision  │ Total Matches │ Toss Winner Wins │ Win %
───────────────┼───────────────┼─────────────────┼──────────
Batting First  │ 500           │ 300             │ 60.00%
Bowling First  │ 500           │ 250             │ 50.00%
```

---

### Query Pattern Summary

**Pattern Recognition for Similar Queries:**

```
SIMPLE QUERY PATTERN:
┌─────────────────────────────────────────┐
│ SELECT columns                          │
│ FROM table                              │
│ WHERE condition                         │
│ ORDER BY column                         │
│ LIMIT number                            │
└─────────────────────────────────────────┘

AGGREGATION PATTERN (GROUP BY):
┌─────────────────────────────────────────┐
│ SELECT column, AGGREGATE_FUNCTION()   │
│ FROM table                              │
│ WHERE condition                         │
│ GROUP BY column                         │
│ HAVING aggregate_condition              │
│ ORDER BY aggregate_function()           │
└─────────────────────────────────────────┘

JOIN PATTERN (Multi-table):
┌─────────────────────────────────────────┐
│ SELECT t1.col, t2.col                   │
│ FROM table1 t1                          │
│ JOIN table2 t2 ON t1.id = t2.id        │
│ WHERE condition                         │
│ GROUP BY ...                            │
│ ORDER BY ...                            │
└─────────────────────────────────────────┘

CONDITIONAL AGGREGATION PATTERN:
┌─────────────────────────────────────────┐
│ SELECT                                  │
│   SUM(CASE WHEN condition1              │
│       THEN value ELSE 0 END) AS col1,  │
│   SUM(CASE WHEN condition2              │
│       THEN value ELSE 0 END) AS col2   │
│ FROM table                              │
│ GROUP BY ...                            │
└─────────────────────────────────────────┘
```

---

## Quick Reference Guide

### Common SQL Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `COUNT()` | Count rows | `COUNT(player_id)` → 500 |
| `SUM()` | Add values | `SUM(runs)` → 50000 |
| `AVG()` | Average | `AVG(runs)` → 67.5 |
| `MAX()` | Highest value | `MAX(runs)` → 250 |
| `MIN()` | Lowest value | `MIN(runs)` → 0 |
| `ROUND()` | Round number | `ROUND(3.14159, 2)` → 3.14 |
| `EXTRACT()` | Get part of date | `EXTRACT(YEAR FROM date)` → 2024 |

### Common Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equal | `country = 'India'` |
| `>`, `<` | Greater/Less | `runs > 1000` |
| `>=`, `<=` | Greater/Less or equal | `age >= 18` |
| `<>` or `!=` | Not equal | `status <> 'Injured'` |
| `BETWEEN` | Range | `runs BETWEEN 100 AND 200` |
| `IN` | Multiple values | `country IN ('India', 'Australia')` |
| `LIKE` | Pattern matching | `name LIKE 'V%'` → Names starting with V |
| `AND`, `OR` | Combine conditions | `country='India' AND runs>1000` |

### Common JOIN Types

```
INNER JOIN (Default)
├─ Returns: Matching rows from both tables
├─ Visual:
│  Table1: [1][2][3][4][5]
│  Table2: [3][4][5][6][7]
│  Result: [3][4][5]
└─ Use case: When you want only matched records

LEFT JOIN
├─ Returns: All from Table1 + matched from Table2
├─ Visual:
│  Table1: [1][2][3][4][5]
│  Table2: [3][4][5][6][7]
│  Result: [1][2][3][4][5](+null values)
└─ Use case: Keep all records from main table

FULL OUTER JOIN
├─ Returns: All from both tables
├─ Visual:
│  Result: [1][2][3][4][5][6][7]
└─ Use case: Complete match history
```

---

## Troubleshooting Common Errors

### Error: "Column not found"
```sql
-- ❌ WRONG: Column doesn't exist
SELECT player_name FROM players;

-- ✅ CORRECT: Use actual column name
SELECT full_name FROM players;
```

### Error: "Syntax error near GROUP BY"
```sql
-- ❌ WRONG: Non-aggregated column not in GROUP BY
SELECT full_name, SUM(runs) FROM innings GROUP BY match_id;

-- ✅ CORRECT: Include in GROUP BY
SELECT full_name, SUM(runs) FROM innings 
GROUP BY player_id, full_name;
```

### Error: "No results returned"
- Check WHERE clause filter
- Verify table has data
- Try removing WHERE temporarily
- Check for NULL values

---

## Practice Exercises

### Exercise 1: Find top 5 bowlers by wickets
```sql
-- Your task:
-- SELECT player names and total wickets
-- FROM innings table
-- WHERE bowling position > 0
-- GROUP BY player
-- ORDER BY wickets (highest first)
-- LIMIT 5

-- Solution:
SELECT 
    p.full_name,
    SUM(i.wickets_taken) AS total_wickets
FROM innings i
JOIN players p ON i.player_id = p.player_id
WHERE i.bowling_position > 0
GROUP BY p.player_id, p.full_name
ORDER BY total_wickets DESC
LIMIT 5;
```

### Exercise 2: List all venues and average attendance
```sql
-- Your task:
-- Get venue name and average attendance
-- Sort by attendance (highest first)

-- Solution:
SELECT 
    v.venue_name,
    ROUND(AVG(m.attendance), 0) AS avg_attendance
FROM venues v
LEFT JOIN matches m ON v.venue_id = m.venue_id
GROUP BY v.venue_id, v.venue_name
ORDER BY avg_attendance DESC;
```

---

## Conclusion

The **SQL Queries Page** provides:
1. **Educational Interface** - Learn SQL through examples
2. **Interactive Execution** - Run queries without database client
3. **Results Visualization** - See data in tables with statistics
4. **Custom Query Support** - Experiment with own SQL
5. **Export Functionality** - Download results as CSV

**Key Takeaways for Beginners:**
- SQL = Language to ask database questions
- SELECT-FROM-WHERE = Basic query structure
- JOIN = Combine multiple tables
- GROUP BY = Summarize data
- Aggregate functions = COUNT, SUM, AVG, MAX, MIN
- ORDER BY/LIMIT = Sort and limit results

**Next Steps:**
1. Run beginner queries (Q1-Q8)
2. Experiment with small changes
3. Move to intermediate queries (Q9-Q16)
4. Try custom queries with templates
5. Study advanced patterns (Q17-Q25)

Happy querying! 🚀
