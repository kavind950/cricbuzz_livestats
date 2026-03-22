import streamlit as st
import pandas as pd
from utils.db_connection import execute_query

def show_crud():
    """Display CRUD operations interface for player and match management."""
    
    st.header("🛠️ CRUD Operations")
    
    st.write("""
    Manage cricket data with full Create, Read, Update, and Delete operations.
    Perform data manipulation on players, matches, and related records.
    """)
    
    # Create main tabs for CRUD operations
    tab_create, tab_read, tab_update, tab_delete = st.tabs([
        "➕ Create",
        "📖 Read",
        "✏️ Update",
        "🗑️ Delete"
    ])
    
    with tab_create:
        show_create_operations()
    
    with tab_read:
        show_read_operations()
    
    with tab_update:
        show_update_operations()
    
    with tab_delete:
        show_delete_operations()


def show_create_operations():
    """Display create (INSERT) operations."""
    
    st.subheader("➕ Create New Records")
    
    # Subtabs for different entity types
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["👤 Add Player", "🏟️ Add Match", "📍 Add Venue"])
    
    with sub_tab1:
        st.write("**Add a new player to the database**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            player_name = st.text_input("Full Name", placeholder="e.g., Virat Kohli")
            country = st.selectbox("Country", ["India", "Australia", "Pakistan", "England", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"])
            playing_role = st.selectbox("Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
        
        with col2:
            batting_style = st.selectbox("Batting Style", ["Right-handed", "Left-handed"])
            bowling_style = st.selectbox("Bowling Style", ["Right-arm fast", "Right-arm medium", "Right-arm off-break", "Right-arm leg-break", "Left-arm fast", "Left-arm medium", "Left-arm orthodox", "Left-arm chinaman", "N/A"])
            jersey_number = st.number_input("Jersey Number", min_value=1, max_value=99, value=1)
        
        if st.button("➕ Add Player", key="add_player"):
            if player_name and country:
                try:
                    query = """
                    INSERT INTO players (full_name, country, playing_role, batting_style, bowling_style, jersey_number)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    execute_query(query, (player_name, country, playing_role, batting_style, bowling_style, jersey_number))
                    st.success(f"✅ Player '{player_name}' added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("Please fill in required fields")
    
    with sub_tab2:
        st.write("**Add a new match to the database**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team1 = st.text_input("Team 1", placeholder="e.g., India")
            team2 = st.text_input("Team 2", placeholder="e.g., Australia")
            venue = st.text_input("Venue", placeholder="e.g., MCG")
            match_format = st.selectbox("Match Format", ["Test", "ODI", "T20I"])
        
        with col2:
            match_date = st.date_input("Match Date")
            match_status = st.selectbox("Match Status", ["Scheduled", "Live", "Completed", "Cancelled"])
            description = st.text_area("Match Description", placeholder="Enter match details...")
        
        if st.button("➕ Add Match", key="add_match"):
            if team1 and team2:
                try:
                    query = """
                    INSERT INTO matches (team1_id, team2_id, venue_id, match_date, match_format, match_status, match_description)
                    VALUES (
                        (SELECT team_id FROM teams WHERE team_name = %s LIMIT 1),
                        (SELECT team_id FROM teams WHERE team_name = %s LIMIT 1),
                        (SELECT venue_id FROM venues WHERE venue_name = %s LIMIT 1),
                        %s, %s, %s, %s
                    )
                    """
                    execute_query(query, (team1, team2, venue, match_date, match_format, match_status, description))
                    st.success("✅ Match added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("Please fill in required fields")
    
    with sub_tab3:
        st.write("**Add a new venue to the database**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            venue_name = st.text_input("Venue Name", placeholder="e.g., Melbourne Cricket Ground")
            city = st.text_input("City", placeholder="e.g., Melbourne")
            country = st.text_input("Country", placeholder="e.g., Australia")
        
        with col2:
            capacity = st.number_input("Seating Capacity", min_value=1000, step=1000)
            country_code = st.text_input("Country Code", placeholder="e.g., AU", max_chars=2)
        
        if st.button("➕ Add Venue", key="add_venue"):
            if venue_name and city and country:
                try:
                    query = """
                    INSERT INTO venues (venue_name, city, country, seating_capacity, country_code)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    execute_query(query, (venue_name, city, country, capacity, country_code))
                    st.success("✅ Venue added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("Please fill in required fields")


def show_read_operations():
    """Display read (SELECT) operations."""
    
    st.subheader("📖 View Records")
    
    # Entity selection
    entity = st.selectbox("Select record type:", ["Players", "Matches", "Venues", "Teams", "Series"])
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input(f"Search in {entity.lower()}...")
    
    with col2:
        sort_by = st.selectbox("Sort by:", ["Name", "Date Added", "ID"])
    
    with col3:
        limit = st.number_input("Rows to display:", min_value=5, max_value=100, value=20)
    
    # Build appropriate query
    if entity == "Players":
        query = """
        SELECT 
            player_id,
            full_name,
            country,
            playing_role,
            batting_style,
            bowling_style
        FROM players
        """
        if search_term:
            query += " WHERE full_name ILIKE %s OR country ILIKE %s"
        query += f" LIMIT {limit}"
    
    elif entity == "Matches":
        query = """
        SELECT 
            m.match_id,
            m.match_description,
            t1.team_name AS team_1,
            t2.team_name AS team_2,
            v.venue_name,
            m.match_date,
            m.match_format,
            m.match_status
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        """
        if search_term:
            query += " WHERE t1.team_name ILIKE %s OR t2.team_name ILIKE %s OR v.venue_name ILIKE %s"
        query += f" ORDER BY m.match_date DESC LIMIT {limit}"
    
    elif entity == "Venues":
        query = """
        SELECT 
            venue_id,
            venue_name,
            city,
            country,
            seating_capacity
        FROM venues
        """
        if search_term:
            query += " WHERE venue_name ILIKE %s OR city ILIKE %s OR country ILIKE %s"
        query += f" LIMIT {limit}"
    
    elif entity == "Teams":
        query = """
        SELECT 
            team_id,
            team_name,
            country,
            coach,
            captain
        FROM teams
        """
        if search_term:
            query += " WHERE team_name ILIKE %s OR country ILIKE %s"
        query += f" LIMIT {limit}"
    
    elif entity == "Series":
        query = """
        SELECT 
            series_id,
            series_name,
            host_country,
            match_type,
            start_date,
            total_matches_planned
        FROM series
        """
        if search_term:
            query += " WHERE series_name ILIKE %s OR host_country ILIKE %s"
        query += f" LIMIT {limit}"
    
    # Execute query
    if st.button("🔍 Search", key="read_search"):
        try:
            # Prepare parameters for parameterized queries
            params = None
            if search_term:
                if entity == "Players":
                    params = (f"%{search_term}%", f"%{search_term}%")
                elif entity == "Matches":
                    params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
                elif entity == "Venues":
                    params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
                elif entity == "Teams":
                    params = (f"%{search_term}%", f"%{search_term}%")
                elif entity == "Series":
                    params = (f"%{search_term}%", f"%{search_term}%")
            
            data = execute_query(query, params, fetch=True)
            
            if data:
                df = pd.DataFrame(data)
                st.success(f"✅ Found {len(df)} records")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{entity.lower()}_data.csv",
                    mime="text/csv"
                )
            else:
                st.info("No records found")
        except Exception as e:
            st.error(f"❌ Error: {e}")


def show_update_operations():
    """Display update (UPDATE) operations."""
    
    st.subheader("✏️ Update Records")
    
    st.write("Select a record type to update:")
    
    update_type = st.radio("Update:", ["Player Information", "Match Status"], horizontal=True)
    
    if update_type == "Player Information":
        st.write("**Update player details**")
        
        # Get player to update
        player_id = st.number_input("Player ID", min_value=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_role = st.selectbox("New Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper", "No change"])
            new_country = st.text_input("New Country (leave blank for no change)")
        
        with col2:
            new_batting_style = st.selectbox("New Batting Style", ["Right-handed", "Left-handed", "No change"])
            new_bowling_style = st.selectbox("New Bowling Style", ["Right-arm fast", "Right-arm medium", "Right-arm off-break", "Right-arm leg-break", "Left-arm fast", "Left-arm medium", "Left-arm orthodox", "Left-arm chinaman", "N/A", "No change"])
        
        if st.button("✏️ Update Player"):
            try:
                updates = []
                params = []
                
                if new_country:
                    updates.append("country = %s")
                    params.append(new_country)
                
                if new_role != "No change":
                    updates.append("playing_role = %s")
                    params.append(new_role)
                
                if new_batting_style != "No change":
                    updates.append("batting_style = %s")
                    params.append(new_batting_style)
                
                if new_bowling_style != "No change":
                    updates.append("bowling_style = %s")
                    params.append(new_bowling_style)
                
                if updates:
                    query = f"UPDATE players SET {', '.join(updates)} WHERE player_id = %s"
                    params.append(player_id)
                    execute_query(query, tuple(params))
                    st.success("✅ Player updated successfully!")
                else:
                    st.warning("No changes to update")
            
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    else:  # Match Status
        st.write("**Update match status**")
        
        match_id = st.number_input("Match ID", min_value=1)
        new_status = st.selectbox("New Match Status", ["Scheduled", "Live", "Completed", "Cancelled"])
        winning_team = st.text_input("Winning Team (for completed matches)", placeholder="Leave blank if not applicable")
        victory_margin = st.number_input("Victory Margin", value=0)
        victory_type = st.selectbox("Victory Type", ["Runs", "Wickets", "N/A"])
        
        if st.button("✏️ Update Match"):
            try:
                query = """
                UPDATE matches 
                SET match_status = %s,
                    winning_team_id = CASE WHEN %s != '' 
                                      THEN (SELECT team_id FROM teams WHERE team_name = %s LIMIT 1)
                                      ELSE NULL END,
                    victory_margin = %s,
                    victory_type = %s
                WHERE match_id = %s
                """
                execute_query(query, (new_status, winning_team, winning_team, victory_margin, victory_type, match_id))
                st.success("✅ Match updated successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")


def show_delete_operations():
    """Display delete (DELETE) operations."""
    
    st.subheader("🗑️ Delete Records")
    
    st.warning("⚠️ Warning: Deletion is permanent. Please be careful!", icon="⚠️")
    
    delete_type = st.selectbox("Select record type to delete:", ["Player", "Match", "Venue"])
    
    if delete_type == "Player":
        st.write("**Delete a player record**")
        
        player_id = st.number_input("Player ID to delete", min_value=1, key="delete_player")
        
        # Show player details before deletion
        try:
            query = "SELECT full_name, country FROM players WHERE player_id = %s"
            data = execute_query(query, (player_id,), fetch=True)
            if data:
                player = data[0]
                st.info(f"Will delete: **{player['full_name']}** from {player['country']}")
            else:
                st.warning("Player not found")
        except:
            pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Player", key="confirm_delete_player"):
                confirmation = st.text_input("Type 'DELETE' to confirm", key="player_confirm_input")
                if confirmation == "DELETE":
                    try:
                        query = "DELETE FROM players WHERE player_id = %s"
                        execute_query(query, (player_id,))
                        st.success("✅ Player deleted successfully")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.error("Confirmation text doesn't match")
        
        with col2:
            if st.button("❌ Cancel"):
                st.info("Deletion cancelled")
    
    elif delete_type == "Match":
        st.write("**Delete a match record**")
        
        match_id = st.number_input("Match ID to delete", min_value=1, key="delete_match")
        
        if st.button("🗑️ Delete Match", key="confirm_delete_match"):
            confirmation = st.text_input("Type 'DELETE' to confirm", key="match_confirm_input")
            if confirmation == "DELETE":
                try:
                    query = "DELETE FROM matches WHERE match_id = %s"
                    execute_query(query, (match_id,))
                    st.success("✅ Match deleted successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("Confirmation text doesn't match")
    
    elif delete_type == "Venue":
        st.write("**Delete a venue record**")
        
        venue_id = st.number_input("Venue ID to delete", min_value=1, key="delete_venue")
        
        if st.button("🗑️ Delete Venue", key="confirm_delete_venue"):
            confirmation = st.text_input("Type 'DELETE' to confirm", key="venue_confirm_input")
            if confirmation == "DELETE":
                try:
                    query = "DELETE FROM venues WHERE venue_id = %s"
                    execute_query(query, (venue_id,))
                    st.success("✅ Venue deleted successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("Confirmation text doesn't match")
