# Database Connection Manager for Cricket Analytics Platform
#
# This module handles all database operations including:
# - Connection pooling and lifecycle management
# - Schema creation and migration logic
# - Helper functions for safe schema modifications
# - Integration with SQLite for cricket data persistence

import sqlite3
from pathlib import Path
import re

# SQLite database file location in project root
DB_FILE = Path("cricket.db")

def get_conn() -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite cricket database.
    
    The connection is configured with:
    - check_same_thread=False: Allows multi-threaded access (required by Streamlit)
    - row_factory=sqlite3.Row: Returns rows as dictionary-like objects for easier access
    
    Returns:
        sqlite3.Connection: Active database connection object
    """
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Helper functions for safe schema operations ----------

def _col_exists(cur, table: str, col: str) -> bool:
    """
    Check if a specific column exists in a table.
    Uses PRAGMA to inspect table structure without modifying it.
    """
    cur.execute(f'PRAGMA table_info("{table}")')
    return any(r[1] == col for r in cur.fetchall())

def _table_cols(cur, table: str) -> set:
    """
    Retrieve all column names from a specific table.
    Returns a set of column names for membership testing.
    """
    cur.execute(f'PRAGMA table_info("{table}")')
    return {r[1] for r in cur.fetchall()}

def _safe_add_col(cur, table: str, name: str, decl: str) -> None:
    """
    Safely add a column to a table if it doesn't already exist.
    
    This function is idempotent - running it multiple times is safe and won't cause errors.
    Supports schema evolution without data loss through migrations.
    """
    if not _col_exists(cur, table, name):
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")

def _safe_create_index(cur, idx_name: str, table: str, cols: list[str]) -> None:
    """
    Safely create a database index for query performance optimization.
    
    Only creates the index if all requested columns exist in the table.
    Indexes improve query speed on frequently filtered or joined columns.
    """
    if set(cols).issubset(_table_cols(cur, table)):
        cur.execute(
            f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({", ".join(cols)})'
        )

# ---------- Schema initialization and migrations ----------

def ensure_schema():
    """
    Initialize or migrate the cricket analytics database schema.
    
    This function performs idempotent schema operations:
    - Creates all required tables if they don't exist
    - Adds missing columns to existing tables without data loss
    - Creates performance indexes on frequently queried columns
    
    The function is safe to call multiple times without causing errors.
    It supports schema versioning through gradual additions of columns and indexes.
    """
    conn = get_conn()
    cur = conn.cursor()

    # -------- players --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            country TEXT,
            role TEXT,
            playing_role TEXT,
            total_runs INTEGER,
            batting_average REAL,
            strike_rate REAL,
            total_wickets INTEGER,
            bowling_average REAL,
            economy_rate REAL
        )
        """
    )
    for addcol, decl in [
        ("batting_style", "TEXT"),
        ("bowling_style", "TEXT"),
        ("catches", "INTEGER"),
        ("stumpings", "INTEGER"),
    ]:
        _safe_add_col(cur, "players", addcol, decl)

    # -------- venues --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS venues (
            venue_id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            country TEXT,
            capacity INTEGER
        )
        """
    )
    _safe_add_col(cur, "venues", "name", "TEXT")
    _safe_add_col(cur, "venues", "city", "TEXT")
    _safe_add_col(cur, "venues", "country", "TEXT")
    _safe_add_col(cur, "venues", "capacity", "INTEGER")
    _safe_add_col(cur, "venues", "venue", "TEXT")
    cur.execute("UPDATE venues SET venue = COALESCE(venue, name) WHERE venue IS NULL")

    # -------- series --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS series (
            series_id TEXT PRIMARY KEY,
            series_name TEXT,
            host_country TEXT,
            match_type TEXT,
            start_date TEXT,
            planned_matches INTEGER
        )
        """
    )

    # -------- matches --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            match_id TEXT PRIMARY KEY,
            description TEXT,
            match_type TEXT,
            status TEXT,
            start_time TEXT,
            team1 TEXT,
            team2 TEXT,
            venue TEXT
        )
        """
    )
    for addcol, decl in [
        ("description", "TEXT"),
        ("match_type", "TEXT"),
        ("status", "TEXT"),
        ("start_time", "TEXT"),
        ("team1", "TEXT"),
        ("team2", "TEXT"),
        ("venue", "TEXT"),
    ]:
        _safe_add_col(cur, "matches", addcol, decl)

    for addcol, decl in [
        ("winner", "TEXT"),
        ("victory_margin", "TEXT"),
        ("victory_type", "TEXT"),
        ("toss_winner", "TEXT"),
        ("toss_decision", "TEXT"),
        ("venue_id", "TEXT"),
        ("series_id", "TEXT"),
        ("venue_country", "TEXT"),
        ("series_name", "TEXT"),
        ("city", "TEXT"),
    ]:
        _safe_add_col(cur, "matches", addcol, decl)

    _safe_create_index(cur, "idx_matches_start", "matches", ["start_time"])

    # -------- batting_innings --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS batting_innings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            innings_no INTEGER,
            team TEXT,
            player_name TEXT,
            player_id TEXT,
            position INTEGER,
            runs INTEGER,
            balls INTEGER,
            strike_rate REAL
        )
        """
    )
    for addcol, decl in [
        ("match_id", "TEXT"),
        ("innings_no", "INTEGER"),
        ("team", "TEXT"),
        ("player_name", "TEXT"),
        ("player_id", "TEXT"),
        ("position", "INTEGER"),
        ("runs", "INTEGER"),
        ("balls", "INTEGER"),
        ("strike_rate", "REAL"),
    ]:
        _safe_add_col(cur, "batting_innings", addcol, decl)

    if {"batsman", "player_name"}.issubset(_table_cols(cur, "batting_innings")):
        cur.execute(
            """
            UPDATE batting_innings
               SET player_name = COALESCE(player_name, batsman)
             WHERE player_name IS NULL
            """
        )

    _safe_create_index(cur, "idx_bat_match", "batting_innings", ["match_id"])
    _safe_create_index(cur, "idx_bat_player", "batting_innings", ["player_name"])

    # -------- bowling_spells --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bowling_spells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            innings_no INTEGER,
            bowler_name TEXT,
            bowler_id TEXT,
            overs REAL,
            balls INTEGER,
            runs INTEGER,
            wickets INTEGER,
            economy REAL
        )
        """
    )
    for addcol, decl in [
        ("match_id", "TEXT"),
        ("innings_no", "INTEGER"),
        ("bowler_name", "TEXT"),
        ("bowler_id", "TEXT"),
        ("overs", "REAL"),
        ("balls", "INTEGER"),
        ("runs", "INTEGER"),
        ("wickets", "INTEGER"),
        ("economy", "REAL"),
    ]:
        _safe_add_col(cur, "bowling_spells", addcol, decl)

    _safe_create_index(cur, "idx_bowl_match", "bowling_spells", ["match_id"])
    _safe_create_index(cur, "idx_bowl_bowler", "bowling_spells", ["bowler_name"])

    # -------- player_format_stats (optional) --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS player_format_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            player_id TEXT,
            format TEXT,
            matches INTEGER,
            runs INTEGER,
            batting_average REAL,
            strike_rate REAL,
            wickets INTEGER,
            bowling_average REAL,
            economy REAL
        )
        """
    )
    _safe_create_index(
        cur, "idx_pfs_player_fmt", "player_format_stats", ["player_name", "format"]
    )

    # -------- partnerships (optional/synthetic) --------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS partnerships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            innings_no INTEGER,
            batter1 TEXT,
            batter2 TEXT,
            runs INTEGER
        )
        """
    )

    conn.commit()
    conn.close()

# ---------- tolerant insert utilities ----------
def _col_types(cur, table: str) -> dict[str, str]:
    cur.execute(f'PRAGMA table_info("{table}")')
    rows = cur.fetchall()
    return { (r["name"] if isinstance(r, sqlite3.Row) else r[1]) :
             ((r["type"] if isinstance(r, sqlite3.Row) else r[2]) or "").upper()
             for r in rows }

_num_pat = re.compile(r"-?\d+(?:\.\d+)?")

def _coerce_for_sqlite(value, decl: str):
    if value is None:
        return None
    t = (decl or "").upper()
    if "INT" in t:
        if isinstance(value, (int,)):
            return value
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str):
            m = _num_pat.search(value)
            return int(m.group(0)) if m else None
        return int(value)
    if "REAL" in t or "FLOA" in t or "DOUB" in t:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            m = _num_pat.search(value)
            return float(m.group(0)) if m else None
        return float(value)
    return str(value)

def _insert_many_tolerant(cur, table: str, rows: list[dict]):
    if not rows:
        return
    types = _col_types(cur, table)
    use_cols = [c for c in rows[0].keys() if c in types]
    if not use_cols:
        return
    placeholders = ",".join(["?"] * len(use_cols))
    sql = f'INSERT OR IGNORE INTO {table} ({",".join(use_cols)}) VALUES ({placeholders})'
    data = []
    for r in rows:
        vals = [_coerce_for_sqlite(r.get(c), types[c]) for c in use_cols]
        data.append(tuple(vals))
    cur.executemany(sql, data)

# ---------- tiny demo seed (idempotent & tolerant) ----------
def seed_demo_data_if_empty(force: bool = True) -> None:
    """Insert a small dataset so all 25 queries return rows."""
    ensure_schema()
    conn = get_conn()
    cur = conn.cursor()

    if not force:
        try:
            cur.execute("SELECT COUNT(*) FROM matches WHERE winner IS NOT NULL;")
            if cur.fetchone()[0] >= 25:
                conn.close()
                return
        except Exception:
            pass

    # Venues
    venues = [
        {"venue_id":"MCG","name":"Melbourne Cricket Ground","city":"Melbourne","country":"Australia","capacity":100024,"venue":"Melbourne Cricket Ground"},
        {"venue_id":"Eden","name":"Eden Gardens","city":"Kolkata","country":"India","capacity":68000,"venue":"Eden Gardens"},
        {"venue_id":"Lords","name":"Lord's","city":"London","country":"England","capacity":30000,"venue":"Lord's"},
        {"venue_id":"Wankhede","name":"Wankhede Stadium","city":"Mumbai","country":"India","capacity":33000,"venue":"Wankhede Stadium"},
    ]
    _insert_many_tolerant(cur, "venues", venues)

    # Series
    series = [
        {"series_id":"S_T20WC24","series_name":"ICC Men's T20 World Cup 2024","host_country":"USA/WI","match_type":"T20I","start_date":"2024-06-02","planned_matches":55},
        {"series_id":"S_BGT24","series_name":"Border-Gavaskar Trophy 2024","host_country":"India","match_type":"Test","start_date":"2024-02-10","planned_matches":5},
        {"series_id":"S_ODI25","series_name":"Bilateral ODI Series 2025","host_country":"India","match_type":"ODI","start_date":"2025-08-10","planned_matches":3},
    ]
    _insert_many_tolerant(cur, "series", series)

    # Players
    players = [
        {"name":"Virat Kohli","country":"India","playing_role":"Batsman","batting_style":"Right-hand bat","bowling_style":None,"total_runs":13000,"total_wickets":4,"batting_average":57.0,"strike_rate":92.0,"bowling_average":None,"economy_rate":None,"catches":150,"stumpings":0},
        {"name":"Rohit Sharma","country":"India","playing_role":"Batsman","batting_style":"Right-hand bat","bowling_style":None,"total_runs":11000,"total_wickets":8,"batting_average":49.0,"strike_rate":90.0,"bowling_average":None,"economy_rate":None,"catches":120,"stumpings":0},
        {"name":"Steve Smith","country":"Australia","playing_role":"Batsman","batting_style":"Right-hand bat","bowling_style":None,"total_runs":9500,"total_wickets":30,"batting_average":54.0,"strike_rate":83.0,"bowling_average":None,"economy_rate":None,"catches":100,"stumpings":0},
        {"name":"David Warner","country":"Australia","playing_role":"Batsman","batting_style":"Left-hand bat","bowling_style":None,"total_runs":6500,"total_wickets":0,"batting_average":45.0,"strike_rate":96.0,"bowling_average":None,"economy_rate":None,"catches":95,"stumpings":0},
        {"name":"Jasprit Bumrah","country":"India","playing_role":"Bowler","batting_style":"Right-hand bat","bowling_style":"Right-arm fast","total_runs":500,"total_wickets":350,"batting_average":15.0,"strike_rate":80.0,"bowling_average":25.0,"economy_rate":4.9,"catches":60,"stumpings":0},
        {"name":"Mitchell Starc","country":"Australia","playing_role":"Bowler","batting_style":"Left-hand bat","bowling_style":"Left-arm fast","total_runs":600,"total_wickets":320,"batting_average":13.0,"strike_rate":85.0,"bowling_average":27.0,"economy_rate":5.2,"catches":55,"stumpings":0},
        {"name":"Joe Root","country":"England","playing_role":"Batsman","batting_style":"Right-hand bat","bowling_style":None,"total_runs":10000,"total_wickets":20,"batting_average":50.0,"strike_rate":87.0,"bowling_average":None,"economy_rate":None,"catches":110,"stumpings":0},
        {"name":"Rashid Khan","country":"Afghanistan","playing_role":"Bowler","batting_style":"Right-hand bat","bowling_style":"Legbreak googly","total_runs":800,"total_wickets":200,"batting_average":20.0,"strike_rate":130.0,"bowling_average":21.0,"economy_rate":6.4,"catches":40,"stumpings":0},
    ]
    _insert_many_tolerant(cur, "players", players)

    # Matches (spread across formats/years/venues, includes winners & toss)
    matches = [
        {"match_id":"M2025-IND-AUS-ODI-01","description":"1st ODI: IND vs AUS","match_type":"ODI","status":"Completed","start_time":"2025-09-03 09:00:00","team1":"India","team2":"Australia","venue":"Eden Gardens, Kolkata","winner":"India","victory_margin":"12","victory_type":"runs","toss_winner":"Australia","toss_decision":"bat","venue_id":"Eden","venue_country":"India","series_id":"S_ODI25","series_name":"Bilateral ODI Series 2025","city":"Kolkata"},
        {"match_id":"M2025-IND-AUS-ODI-02","description":"2nd ODI: IND vs AUS","match_type":"ODI","status":"Completed","start_time":"2025-08-29 14:00:00","team1":"India","team2":"Australia","venue":"Wankhede Stadium, Mumbai","winner":"Australia","victory_margin":"3","victory_type":"wickets","toss_winner":"India","toss_decision":"bat","venue_id":"Wankhede","venue_country":"India","series_id":"S_ODI25","series_name":"Bilateral ODI Series 2025","city":"Mumbai"},
        {"match_id":"M2024-IND-AUS-T20I-01","description":"T20I: IND vs AUS","match_type":"T20I","status":"Completed","start_time":"2024-06-12 19:30:00","team1":"India","team2":"Australia","venue":"Eden Gardens, Kolkata","winner":"India","victory_margin":"4","victory_type":"wickets","toss_winner":"Australia","toss_decision":"field","venue_id":"Eden","venue_country":"India","series_id":"S_T20WC24","series_name":"ICC Men's T20 World Cup 2024","city":"Kolkata"},
        {"match_id":"M2023-IND-AUS-ODI-01","description":"ODI: IND vs AUS","match_type":"ODI","status":"Completed","start_time":"2023-10-15 14:00:00","team1":"India","team2":"Australia","venue":"Melbourne Cricket Ground","winner":"India","victory_margin":"40","victory_type":"runs","toss_winner":"India","toss_decision":"bat","venue_id":"MCG","venue_country":"Australia","series_id":None,"series_name":None,"city":"Melbourne"},
        {"match_id":"M2023-IND-AUS-TEST-01","description":"Test: IND vs AUS","match_type":"Test","status":"Completed","start_time":"2023-03-03 10:00:00","team1":"India","team2":"Australia","venue":"Melbourne Cricket Ground","winner":"Australia","victory_margin":"80","victory_type":"runs","toss_winner":"Australia","toss_decision":"bat","venue_id":"MCG","venue_country":"Australia","series_id":"S_BGT24","series_name":"Border-Gavaskar Trophy 2024","city":"Melbourne"},
        {"match_id":"M2024-09-20-IND-PAK-ODI","description":"ODI: IND vs PAK","match_type":"ODI","status":"Completed","start_time":"2024-09-20 13:00:00","team1":"India","team2":"Pakistan","venue":"Eden Gardens, Kolkata","winner":"India","victory_margin":"24","victory_type":"runs","toss_winner":"Pakistan","toss_decision":"bat","venue_id":"Eden","venue_country":"India","series_id":None,"series_name":None,"city":"Kolkata"},
        {"match_id":"M2024-11-30-IND-PAK-T20I","description":"T20I: IND vs PAK","match_type":"T20I","status":"Completed","start_time":"2024-11-30 19:30:00","team1":"India","team2":"Pakistan","venue":"Eden Gardens, Kolkata","winner":"Pakistan","victory_margin":"3","victory_type":"wickets","toss_winner":"India","toss_decision":"bat","venue_id":"Eden","venue_country":"India","series_id":"S_T20WC24","series_name":"ICC Men's T20 World Cup 2024","city":"Kolkata"},
        {"match_id":"M2025-02-05-IND-NZ-T20I","description":"T20I: IND vs NZ","match_type":"T20I","status":"Completed","start_time":"2025-02-05 19:00:00","team1":"India","team2":"New Zealand","venue":"Wankhede Stadium, Mumbai","winner":"India","victory_margin":"4","victory_type":"wickets","toss_winner":"India","toss_decision":"field","venue_id":"Wankhede","venue_country":"India","series_id":None,"series_name":None,"city":"Mumbai"},
        {"match_id":"M2025-05-22-IND-SA-ODI","description":"ODI: IND vs SA","match_type":"ODI","status":"Completed","start_time":"2025-05-22 13:00:00","team1":"India","team2":"South Africa","venue":"Wankhede Stadium, Mumbai","winner":"South Africa","victory_margin":"8","victory_type":"runs","toss_winner":"India","toss_decision":"bat","venue_id":"Wankhede","venue_country":"India","series_id":None,"series_name":None,"city":"Mumbai"},
        {"match_id":"M2025-07-14-IND-SL-T20I","description":"T20I: IND vs SL","match_type":"T20I","status":"Completed","start_time":"2025-07-14 19:30:00","team1":"India","team2":"Sri Lanka","venue":"Eden Gardens, Kolkata","winner":"India","victory_margin":"2","victory_type":"wickets","toss_winner":"India","toss_decision":"field","venue_id":"Eden","venue_country":"India","series_id":None,"series_name":None,"city":"Kolkata"},
        {"match_id":"M2024-01-20-IND-ENG-TEST","description":"Test: IND vs ENG","match_type":"Test","status":"Completed","start_time":"2024-01-20 10:00:00","team1":"India","team2":"England","venue":"Eden Gardens, Kolkata","winner":"India","victory_margin":"120","victory_type":"runs","toss_winner":"England","toss_decision":"bat","venue_id":"Eden","venue_country":"India","series_id":"S_BGT24","series_name":"Border-Gavaskar Trophy 2024","city":"Kolkata"},
        {"match_id":"M2024-04-10-IND-ENG-TEST","description":"Test: IND vs ENG","match_type":"Test","status":"Completed","start_time":"2024-04-10 10:00:00","team1":"India","team2":"England","venue":"Eden Gardens, Kolkata","winner":"England","victory_margin":"5","victory_type":"wickets","toss_winner":"India","toss_decision":"bat","venue_id":"Eden","venue_country":"India","series_id":"S_BGT24","series_name":"Border-Gavaskar Trophy 2024","city":"Kolkata"},
    ]
    _insert_many_tolerant(cur, "matches", matches)

    # batting
    def sr(runs, balls):
        return None if not balls else round(100.0 * runs / balls, 2)

    batting = [
        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":52,"balls":58,"strike_rate":sr(52,58)},
        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":85,"balls":98,"strike_rate":sr(85,98)},
        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"team":"Australia","player_name":"Steve Smith","player_id":None,"position":3,"runs":66,"balls":82,"strike_rate":sr(66,82)},
        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"team":"Australia","player_name":"David Warner","player_id":None,"position":1,"runs":38,"balls":45,"strike_rate":sr(38,45)},

        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":23,"balls":34,"strike_rate":sr(23,34)},
        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":55,"balls":70,"strike_rate":sr(55,70)},
        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"team":"Australia","player_name":"Steve Smith","player_id":None,"position":3,"runs":102,"balls":115,"strike_rate":sr(102,115)},
        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"team":"Australia","player_name":"David Warner","player_id":None,"position":1,"runs":41,"balls":52,"strike_rate":sr(41,52)},

        {"match_id":"M2024-IND-AUS-T20I-01","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":34,"balls":24,"strike_rate":sr(34,24)},
        {"match_id":"M2024-IND-AUS-T20I-01","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":72,"balls":48,"strike_rate":sr(72,48)},

        {"match_id":"M2023-IND-AUS-ODI-01","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":60,"balls":72,"strike_rate":sr(60,72)},
        {"match_id":"M2023-IND-AUS-ODI-01","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":103,"balls":95,"strike_rate":sr(103,95)},

        {"match_id":"M2023-IND-AUS-TEST-01","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":44,"balls":95,"strike_rate":sr(44,95)},
        {"match_id":"M2023-IND-AUS-TEST-01","innings_no":1,"team":"Australia","player_name":"Steve Smith","player_id":None,"position":3,"runs":55,"balls":110,"strike_rate":sr(55,110)},

        {"match_id":"M2024-09-20-IND-PAK-ODI","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":88,"balls":104,"strike_rate":sr(88,104)},
        {"match_id":"M2024-11-30-IND-PAK-T20I","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":30,"balls":22,"strike_rate":sr(30,22)},
        {"match_id":"M2025-02-05-IND-NZ-T20I","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":52,"balls":36,"strike_rate":sr(52,36)},
        {"match_id":"M2025-05-22-IND-SA-ODI","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":76,"balls":89,"strike_rate":sr(76,89)},
        {"match_id":"M2025-07-14-IND-SL-T20I","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":41,"balls":28,"strike_rate":sr(41,28)},

        {"match_id":"M2024-01-20-IND-ENG-TEST","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":120,"balls":185,"strike_rate":sr(120,185)},
        {"match_id":"M2024-04-10-IND-ENG-TEST","innings_no":1,"team":"India","player_name":"Virat Kohli","player_id":None,"position":3,"runs":60,"balls":120,"strike_rate":sr(60,120)},
        {"match_id":"M2024-01-20-IND-ENG-TEST","innings_no":1,"team":"England","player_name":"Joe Root","player_id":None,"position":4,"runs":85,"balls":175,"strike_rate":sr(85,175)},

        {"match_id":"M2025-05-22-IND-SA-ODI","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":58,"balls":66,"strike_rate":sr(58,66)},
        {"match_id":"M2024-09-20-IND-PAK-ODI","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":55,"balls":61,"strike_rate":sr(55,61)},
        {"match_id":"M2025-07-14-IND-SL-T20I","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":35,"balls":22,"strike_rate":sr(35,22)},
        {"match_id":"M2025-02-05-IND-NZ-T20I","innings_no":1,"team":"India","player_name":"Rohit Sharma","player_id":None,"position":2,"runs":28,"balls":18,"strike_rate":sr(28,18)},
    ]
    _insert_many_tolerant(cur, "batting_innings", batting)

    # bowling
    bowls = [
        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"bowler_name":"Jasprit Bumrah","bowler_id":None,"overs":10.0,"balls":60,"runs":45,"wickets":2,"economy":4.50},
        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"bowler_name":"Jasprit Bumrah","bowler_id":None,"overs":9.0,"balls":54,"runs":40,"wickets":1,"economy":4.44},
        {"match_id":"M2024-09-20-IND-PAK-ODI","innings_no":1,"bowler_name":"Jasprit Bumrah","bowler_id":None,"overs":10.0,"balls":60,"runs":38,"wickets":3,"economy":3.80},
        {"match_id":"M2025-05-22-IND-SA-ODI","innings_no":1,"bowler_name":"Jasprit Bumrah","bowler_id":None,"overs":10.0,"balls":60,"runs":52,"wickets":1,"economy":5.20},

        {"match_id":"M2025-IND-AUS-ODI-01","innings_no":1,"bowler_name":"Mitchell Starc","bowler_id":None,"overs":10.0,"balls":60,"runs":50,"wickets":2,"economy":5.00},
        {"match_id":"M2025-IND-AUS-ODI-02","innings_no":1,"bowler_name":"Mitchell Starc","bowler_id":None,"overs":10.0,"balls":60,"runs":44,"wickets":2,"economy":4.40},
        {"match_id":"M2024-11-30-IND-PAK-T20I","innings_no":1,"bowler_name":"Rashid Khan","bowler_id":None,"overs":4.0,"balls":24,"runs":22,"wickets":1,"economy":5.50},
    ]
    _insert_many_tolerant(cur, "bowling_spells", bowls)

    conn.commit()
    conn.close()

# --- auto-init schema on import so early queries won't crash ---
try:
    ensure_schema()
except Exception as _e:
    # don't crash the import; just print in console
    print("ensure_schema() on import:", _e)

if __name__ == "__main__":
    ensure_schema()
    print("✅ Schema ensured.")
