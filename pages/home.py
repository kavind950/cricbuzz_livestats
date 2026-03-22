import streamlit as st
from utils.db_connection import check_connection
from datetime import datetime, timedelta

def show_home():
    """Display the home page with project information and navigation guide."""
    
    st.header("🏏 Cricbuzz LiveStats Dashboard")
    
    st.write("""
    Welcome to **Cricbuzz LiveStats** - A comprehensive cricket analytics platform that brings 
    together live data, player statistics, SQL-driven analytics, and complete data management capabilities.
    """)
    
    # Project Overview Section
    st.subheader("📖 Project Overview")
    st.write("""
    This dashboard integrates the **Cricbuzz Cricket API** with a **SQL database** to deliver:
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("⚡ Real-time match updates from Cricbuzz API")
    with col2:
        st.info("📊 Comprehensive player statistics and performance metrics")
    with col3:
        st.info("🔍 25+ advanced SQL analytics queries")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🛠️ Full CRUD operations for data management")
    with col2:
        st.info("📈 Interactive visualizations and insights")
    
    # Navigation Guide
    st.subheader("🗺️ Navigation Guide")
    
    st.markdown("""
    Use the **sidebar** to navigate between pages:
    
    1. **Home** (Current Page) - Project overview and features
    2. **Live Matches** - Real-time cricket match data from Cricbuzz API
    3. **Top Stats** - Player statistics and performance rankings
    4. **SQL Queries** - 25 advanced analytics queries and custom SQL interface
    5. **CRUD Operations** - Create, Read, Update, Delete player/match records
    """)
    
    # Technical Stack
    st.subheader("⚙️ Technical Stack")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Frontend**")
        st.code("Streamlit", language="text")
    with col2:
        st.write("**Backend**")
        st.code("Python 3.8+", language="text")
    with col3:
        st.write("**Database**")
        st.code("PostgreSQL", language="text")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**API**")
        st.code("Cricbuzz REST API", language="text")
    with col2:
        st.write("**Data Processing**")
        st.code("Pandas, NumPy", language="text")
    with col3:
        st.write("**Visualization**")
        st.code("Plotly, Streamlit Charts", language="text")
    
    # SQL Queries Overview
    st.subheader("🧮 SQL Queries Overview")
    
    st.write("""
    The project includes **25 comprehensive SQL queries** organized by difficulty level:
    """)
    
    query_info = {
        "🟢 Beginner (Questions 1-8)": [
            "Q1: Indian players with roles and styles",
            "Q2: Recent matches with team and venue info",
            "Q3: Top 10 ODI run scorers",
            "Q4: Large capacity venues (>25K)",
            "Q5: Team wins count",
            "Q6: Player distribution by role",
            "Q7: Highest score by format",
            "Q8: 2024 cricket series"
        ],
        "🟡 Intermediate (Questions 9-16)": [
            "Q9: All-rounders with 1000+ runs & 50+ wickets",
            "Q10: Last 20 completed matches",
            "Q11: Player performance across formats",
            "Q12: Home vs away team performance",
            "Q13: Batting partnerships (100+ runs)",
            "Q14: Bowling performance by venue",
            "Q15: Close match excellence",
            "Q16: Yearly performance trends"
        ],
        "🔴 Advanced (Questions 17-25)": [
            "Q17: Toss advantage analysis",
            "Q18: Most economical bowlers",
            "Q19: Consistency analysis",
            "Q20: Format match counts & averages",
            "Q21: Comprehensive performance ranking",
            "Q22: Head-to-head team analysis",
            "Q23: Recent player form tracking",
            "Q24: Best batting partnerships",
            "Q25: Career evolution time-series"
        ]
    }
    
    for level, queries in query_info.items():
        with st.expander(level, expanded=False):
            for query in queries:
                st.write(f"• {query}")
    
    # System Status
    st.subheader("🔧 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Database Connection**")
        status, message = check_connection()
        if status:
            st.success(message)
        else:
            st.error(message)
    
    with col2:
        st.write("**API Status**")
        st.info("✓ Cricbuzz API: Ready (ensure API key is configured)")
    
    # Quick Start Guide
    st.subheader("🚀 Quick Start")
    
    st.markdown("""
    **Step 1:** Navigate to **Live Matches** to view current cricket matches
    
    **Step 2:** Explore **Top Stats** for player performance metrics
    
    **Step 3:** Run **SQL Queries** to perform advanced analytics
    
    **Step 4:** Use **CRUD Operations** to manage player/match data
    
    **Step 5:** Refer to **README.md** for detailed documentation
    """)
    
    # Project Information
    st.subheader("📚 Additional Information")
    
    with st.expander("📖 Documentation"):
        st.write("""
        For complete documentation, setup instructions, and advanced features, 
        please refer to the **README.md** file in the project root.
        """)
    
    with st.expander("🔑 API Configuration"):
        st.write("""
        To enable live match data:
        1. Get your RapidAPI key from https://rapidapi.com/
        2. Subscribe to Cricbuzz Cricket API
        3. Update API_KEY in `pages/live_matches.py`
        
        Alternatively, use environment variables in `.env` file
        """)
    
    with st.expander("💾 Database Setup"):
        st.write("""
        To populate the database with **LIVE data from Cricbuzz API**:
        
        1. Ensure database is initialized:
           ```
           python utils/init_database.py
           ```
        
        2. Fetch live data from API:
           ```
           python utils/fetch_live_data.py
           ```
        
        This fetches real matches, teams, and venues directly from Cricbuzz.
        Run `fetch_live_data.py` periodically to keep data fresh.
        
        **Your database contains only LIVE data - no sample data!** ✅
        """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Cricbuzz LiveStats © 2026 | Cricket Analytics Dashboard | Built with Streamlit & Python
    </div>
    """, unsafe_allow_html=True)
