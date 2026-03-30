# Home page for Cricket Analytics Dashboard

import streamlit as st

st.title("🏏 Cricket Match Analytics Platform")

st.markdown("""
    ## Welcome to Your Cricket Intelligence Hub
    
    This platform transforms raw cricket data into actionable insights. By combining real-time match feeds
    with persistent data storage and advanced SQL analytics, it creates a comprehensive toolkit for
    cricket enthusiasts, analysts, and data professionals.
    
    ---
    
    ## How This Platform Works
    
    **1. Data Collection** → Live cricket match information is fetched from external API sources
    
    **2. Storage** → Match and player data is permanently stored in a structured database
    
    **3. Analysis** → Query the database with pre-built or custom SQL commands for insights
    
    **4. Management** → Add, update, or remove player records through an intuitive interface
    
    ---
    
    ## Available Features
    
    ### 📊 Live Match Tracking
    Monitor matches as they unfold with real-time scorecard updates, batsman/bowler statistics,
    and commentary feeds. Get the most current information without switching between multiple platforms.
    
    ### 📈 Player Performance Analytics
    Access comprehensive player statistics including career aggregates, batting averages, 
    strike rates, and bowling records. Sort and filter by country, role, or performance metric.
    
    ### 🔍 Custom Query Interface
    Write your own SQL queries or run from our library of 25+ analytics queries.
    Get answers to questions like "Which venue has the highest scoring average?" 
    or "How many centuries were scored in the last month?"
    
    ### ✏️ Data Management
    Maintain the accuracy of your cricket database by adding new players, updating statistics,
    or removing outdated records through a user-friendly form interface.
    
    ---
    
    ## Getting Started
    
    Use the navigation menu on the left to explore:
    - **Live Matches** to see current match updates
    - **Top Stats** to browse player leaderboards
    - **SQL Queries** to analyze cricket data
    - **CRUD Operations** to manage database records
    
    ---
    
    ## Technical Foundation
    
    **Backend**: Python with SQLite database  
    **Frontend**: Streamlit web framework  
    **Data Source**: Cricbuzz Cricket API  
    **Analytics**: Pandas + SQL queries  
    
    This platform demonstrates how to build data-driven applications that combine
    real-time feeds, analytical depth, and practical usability.
""")

st.divider()

st.subheader("💡 Quick Tips")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("""
    **For Broadcasters**
    
    Use live match data to enrich commentary
    and provide viewers with detailed insights.
    """)

with col2:
    st.write("""
    **For Fantasy Players**
    
    Query player performance history to make
    informed selections for your fantasy teams.
    """)

with col3:
    st.write("""
    **For Data Enthusiasts**
    
    Learn SQL and database design while working
    with real cricket statistics.
    """)

st.divider()
st.caption("Cricket Analytics Platform | Built with Python, Streamlit, and SQLite")
