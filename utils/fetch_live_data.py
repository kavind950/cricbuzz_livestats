"""
Fetch Live Cricket Data from Cricbuzz API and Populate Database

This script fetches real-time cricket data from Cricbuzz API via RapidAPI
and stores it in the PostgreSQL database.

Usage:
    python utils/fetch_live_data.py

Requirements:
    - RapidAPI key configured in .env file
    - Database already initialized (run init_database.py first)
"""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

# Database configuration
# Only use defaults for non-sensitive data (host, port, database)
# Credentials (user, password) MUST be in .env - no hardcoded defaults
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'cricbuzz_livestats'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432')
}

class CricbuzzDataFetcher:
    """Fetch and populate cricket data from Cricbuzz API."""
    
    def __init__(self):
        self.headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": API_HOST
        }
        self.conn = None
        self.teams_cache = {}
        self.venues_cache = {}
        self.series_cache = {}
        self.players_cache = {}
    
    def connect_db(self):
        """Connect to database."""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to database")
            return True
        except psycopg2.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        """Execute database query."""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Query error: {e}")
            return False
    
    def fetch_query(self, query, params=None):
        """Fetch query results."""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []
    
    def get_or_create_team(self, team_name, country):
        """Get or create a team in database."""
        if team_name in self.teams_cache:
            return self.teams_cache[team_name]
        
        # Check if team exists
        result = self.fetch_query(
            "SELECT team_id FROM teams WHERE team_name = %s",
            (team_name,)
        )
        
        if result:
            team_id = result[0]['team_id']
        else:
            # Create new team
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO teams (team_name, country)
                VALUES (%s, %s)
                RETURNING team_id
            """, (team_name, country))
            self.conn.commit()
            team_id = cursor.fetchone()[0]
            cursor.close()
            print(f"  ✅ Created team: {team_name}")
        
        self.teams_cache[team_name] = team_id
        return team_id
    
    def get_or_create_venue(self, venue_name, city, country):
        """Get or create a venue in database."""
        if venue_name in self.venues_cache:
            return self.venues_cache[venue_name]
        
        result = self.fetch_query(
            "SELECT venue_id FROM venues WHERE venue_name = %s",
            (venue_name,)
        )
        
        if result:
            venue_id = result[0]['venue_id']
        else:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO venues (venue_name, city, country)
                VALUES (%s, %s, %s)
                RETURNING venue_id
            """, (venue_name, city, country))
            self.conn.commit()
            venue_id = cursor.fetchone()[0]
            cursor.close()
            print(f"  ✅ Created venue: {venue_name}")
        
        self.venues_cache[venue_name] = venue_id
        return venue_id
    
    def get_or_create_player(self, player_name, country, role):
        """Get or create a player in database."""
        if player_name in self.players_cache:
            return self.players_cache[player_name]
        
        result = self.fetch_query(
            "SELECT player_id FROM players WHERE full_name = %s",
            (player_name,)
        )
        
        if result:
            player_id = result[0]['player_id']
        else:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO players (full_name, country, playing_role)
                VALUES (%s, %s, %s)
                RETURNING player_id
            """, (player_name, country, role))
            self.conn.commit()
            player_id = cursor.fetchone()[0]
            cursor.close()
            print(f"  ✅ Created player: {player_name}")
        
        self.players_cache[player_name] = player_id
        return player_id
    
    def fetch_live_matches(self):
        """Fetch live matches from Cricbuzz API."""
        print("\n🔄 Fetching live matches from Cricbuzz API...")
        
        try:
            url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ API Response received")
            
            matches_added = 0
            
            # Parse matches
            for match_type in data.get("typeMatches", []):
                match_format = match_type.get("matchType", "T20I")
                
                for series in match_type.get("seriesMatches", []):
                    series_data = series.get("seriesAdWrapper", {})
                    series_name = series_data.get("seriesName", "Unknown Series")
                    
                    # Get or create series
                    result = self.fetch_query(
                        "SELECT series_id FROM series WHERE series_name = %s",
                        (series_name,)
                    )
                    
                    if result:
                        series_id = result[0]['series_id']
                    else:
                        cursor = self.conn.cursor()
                        cursor.execute("""
                            INSERT INTO series (series_name, match_type, start_date)
                            VALUES (%s, %s, NOW())
                            RETURNING series_id
                        """, (series_name, match_format))
                        self.conn.commit()
                        series_id = cursor.fetchone()[0]
                        cursor.close()
                        print(f"  ✅ Created series: {series_name}")
                    
                    for match in series_data.get("matches", []):
                        try:
                            match_info = match.get("matchInfo", {})
                            match_score = match.get("matchScore", {})
                            
                            team1_name = match_info.get("team1", {}).get("teamName")
                            team2_name = match_info.get("team2", {}).get("teamName")
                            venue_name = match_info.get("venue", {}).get("name", "Unknown")
                            match_status = match_info.get("status", "Scheduled")
                            match_description = match_info.get("matchDescription", "")
                            
                            if not team1_name or not team2_name:
                                continue
                            
                            # Get or create teams and venue
                            team1_id = self.get_or_create_team(team1_name, "Unknown")
                            team2_id = self.get_or_create_team(team2_name, "Unknown")
                            venue_id = self.get_or_create_venue(venue_name, "Unknown", "Unknown")
                            
                            # Check if match already exists
                            existing = self.fetch_query("""
                                SELECT match_id FROM matches 
                                WHERE team1_id = %s AND team2_id = %s 
                                AND series_id = %s
                                LIMIT 1
                            """, (team1_id, team2_id, series_id))
                            
                            if not existing:
                                cursor = self.conn.cursor()
                                cursor.execute("""
                                    INSERT INTO matches 
                                    (team1_id, team2_id, venue_id, series_id, match_date, 
                                     match_format, match_status, match_description)
                                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)
                                """, (team1_id, team2_id, venue_id, series_id, 
                                      match_format, match_status, match_description))
                                self.conn.commit()
                                cursor.close()
                                matches_added += 1
                                print(f"  ✅ Added match: {team1_name} vs {team2_name}")
                        
                        except Exception as e:
                            print(f"  ⚠️  Error processing match: {e}")
                            continue
            
            print(f"\n✅ Total matches added: {matches_added}")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return False
    
    def fetch_upcoming_matches(self):
        """Fetch upcoming matches from Cricbuzz API."""
        print("\n🔄 Fetching upcoming matches...")
        
        try:
            url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Upcoming matches received")
            
            matches_added = 0
            
            for match_type in data.get("typeMatches", []):
                match_format = match_type.get("matchType", "T20I")
                
                for series in match_type.get("seriesMatches", []):
                    series_data = series.get("seriesAdWrapper", {})
                    series_name = series_data.get("seriesName", "Unknown Series")
                    
                    result = self.fetch_query(
                        "SELECT series_id FROM series WHERE series_name = %s",
                        (series_name,)
                    )
                    
                    if result:
                        series_id = result[0]['series_id']
                    else:
                        cursor = self.conn.cursor()
                        cursor.execute("""
                            INSERT INTO series (series_name, match_type, start_date)
                            VALUES (%s, %s, NOW())
                            RETURNING series_id
                        """, (series_name, match_format))
                        self.conn.commit()
                        series_id = cursor.fetchone()[0]
                        cursor.close()
                    
                    for match in series_data.get("matches", [])[:10]:  # Limit to 10
                        try:
                            match_info = match.get("matchInfo", {})
                            
                            team1_name = match_info.get("team1", {}).get("teamName")
                            team2_name = match_info.get("team2", {}).get("teamName")
                            venue_name = match_info.get("venue", {}).get("name", "TBD")
                            
                            if not team1_name or not team2_name:
                                continue
                            
                            team1_id = self.get_or_create_team(team1_name, "Unknown")
                            team2_id = self.get_or_create_team(team2_name, "Unknown")
                            venue_id = self.get_or_create_venue(venue_name, "Unknown", "Unknown")
                            
                            existing = self.fetch_query("""
                                SELECT match_id FROM matches 
                                WHERE team1_id = %s AND team2_id = %s 
                                AND series_id = %s
                                LIMIT 1
                            """, (team1_id, team2_id, series_id))
                            
                            if not existing:
                                cursor = self.conn.cursor()
                                cursor.execute("""
                                    INSERT INTO matches 
                                    (team1_id, team2_id, venue_id, series_id, match_date, 
                                     match_format, match_status)
                                    VALUES (%s, %s, %s, %s, NOW(), %s, %s)
                                """, (team1_id, team2_id, venue_id, series_id, 
                                      match_format, "Scheduled"))
                                self.conn.commit()
                                cursor.close()
                                matches_added += 1
                        
                        except Exception as e:
                            continue
            
            print(f"✅ Total upcoming matches added: {matches_added}")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return False
    
    def run(self):
        """Run the data fetcher."""
        print("=" * 60)
        print("🏏 Cricbuzz Live Data Fetcher")
        print("=" * 60)
        
        if not API_KEY:
            print("❌ API_KEY not configured in .env file")
            print("   Add your RapidAPI key to .env:")
            print("   RAPIDAPI_KEY=your_key_here")
            return
        
        if not self.connect_db():
            return
        
        try:
            # Fetch data
            self.fetch_live_matches()
            self.fetch_upcoming_matches()
            
            print("\n" + "=" * 60)
            print("✅ Data population completed!")
            print("=" * 60)
            print("\n📊 Your database now contains LIVE data from Cricbuzz API")
            print("💡 Run this script periodically to keep data fresh")
            print("🚀 Start the app: streamlit run app.py")
        
        finally:
            self.close_db()


def main():
    """Main entry point."""
    fetcher = CricbuzzDataFetcher()
    fetcher.run()


if __name__ == "__main__":
    main()
