"""
Database Initialization Script for Cricbuzz LiveStats

This script creates the database schema with all required tables and sample data.
Run this script once to initialize the database before using the application.

Usage:
    python utils/init_database.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def execute_sql(conn, sql):
    """Execute SQL statement."""
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
        print(f"✅ Executed: {sql[:60]}...")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()

def create_tables():
    """Create all required database tables."""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔄 Creating database tables...")
        
        # Teams table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id SERIAL PRIMARY KEY,
            team_name VARCHAR(100) NOT NULL UNIQUE,
            country VARCHAR(100) NOT NULL,
            coach VARCHAR(100),
            captain VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Teams table created")
        
        # Venues table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id SERIAL PRIMARY KEY,
            venue_name VARCHAR(150) NOT NULL UNIQUE,
            city VARCHAR(100),
            country VARCHAR(100),
            seating_capacity INTEGER,
            country_code VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Venues table created")
        
        # Series table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS series (
            series_id SERIAL PRIMARY KEY,
            series_name VARCHAR(150) NOT NULL,
            host_country VARCHAR(100),
            match_type VARCHAR(50),
            start_date DATE,
            end_date DATE,
            total_matches_planned INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Series table created")
        
        # Players table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id SERIAL PRIMARY KEY,
            full_name VARCHAR(150) NOT NULL,
            country VARCHAR(100) NOT NULL,
            playing_role VARCHAR(50),
            batting_style VARCHAR(50),
            bowling_style VARCHAR(50),
            jersey_number INTEGER,
            date_of_birth DATE,
            height DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Players table created")
        
        # Matches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id SERIAL PRIMARY KEY,
            team1_id INTEGER REFERENCES teams(team_id),
            team2_id INTEGER REFERENCES teams(team_id),
            venue_id INTEGER REFERENCES venues(venue_id),
            series_id INTEGER REFERENCES series(series_id),
            match_date TIMESTAMP NOT NULL,
            match_format VARCHAR(50),
            match_status VARCHAR(50),
            match_description TEXT,
            toss_winner_id INTEGER REFERENCES teams(team_id),
            toss_winner_choice VARCHAR(50),
            winning_team_id INTEGER REFERENCES teams(team_id),
            victory_margin INTEGER,
            victory_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Matches table created")
        
        # Innings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS innings (
            innings_id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(player_id),
            batting_position INTEGER,
            runs_scored INTEGER DEFAULT 0,
            balls_faced INTEGER,
            strike_rate DECIMAL(10,2),
            bowling_position INTEGER,
            overs_bowled DECIMAL(5,1),
            runs_conceded INTEGER,
            wickets_taken INTEGER DEFAULT 0,
            bowling_average DECIMAL(10,2),
            economy_rate DECIMAL(10,2),
            bowling_strike_rate DECIMAL(10,2),
            catches INTEGER DEFAULT 0,
            stumpings INTEGER DEFAULT 0,
            run_outs INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Innings table created")
        
        # Partnerships table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS partnerships (
            partnership_id SERIAL PRIMARY KEY,
            player1_id INTEGER NOT NULL REFERENCES players(player_id),
            player2_id INTEGER NOT NULL REFERENCES players(player_id),
            match_id INTEGER NOT NULL REFERENCES matches(match_id),
            total_runs INTEGER,
            balls_faced INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("✅ Partnerships table created")
        
        # Create indices for better query performance
        print("🔄 Creating indices...")
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_players_country ON players(country);",
            "CREATE INDEX IF NOT EXISTS idx_players_role ON players(playing_role);",
            "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);",
            "CREATE INDEX IF NOT EXISTS idx_matches_format ON matches(match_format);",
            "CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(match_status);",
            "CREATE INDEX IF NOT EXISTS idx_innings_match ON innings(match_id);",
            "CREATE INDEX IF NOT EXISTS idx_innings_player ON innings(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_venues_country ON venues(country);",
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
            print(f"✅ Index created")
        
        conn.commit()
        print("\n✅ All tables and indices created successfully!")
        
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False


def insert_sample_data():
    """
    Database is now populated with LIVE data from API.
    This function is kept for backward compatibility but does nothing.
    
    To populate the database with live data:
    1. Run: python utils/fetch_live_data.py
    
    This will fetch real data from Cricbuzz API and populate the database.
    """
    print("\n⏭️  Skipping sample data insertion...")
    print("📌 To populate with LIVE data from Cricbuzz API:")
    print("   Run: python utils/fetch_live_data.py")
    return True


def main():
    """Main function to initialize database."""
    
    print("=" * 60)
    print("🏏 Cricbuzz LiveStats - Database Initialization")
    print("=" * 60)
    
    print(f"\nDatabase Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    
    # Create tables
    if not create_tables():
        print("\n❌ Failed to create tables")
        return
    
    # Insert sample data
    if not insert_sample_data():
        print("\n❌ Failed to insert sample data")
        return
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now run the Streamlit app:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    main()
