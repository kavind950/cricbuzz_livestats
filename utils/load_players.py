# Player Data Loading Module - Cricket Analytics Dashboard
#
# This module handles loading cricket player statistics from the Cricbuzz API
# and persisting them to the local SQLite database.
#
# Key Functions:
# - load_from_trending(): Load trending players from source data
# - load_by_ids(): Load specific players by their player IDs
# - Automatic format preference (ODI > T20I > Test > IPL)
# - Retry logic with exponential backoff for API resilience
# - Rate limiting to respect API quotas
#
# All loaded data is normalized and stored in the players table.

import os
import time
import requests
from typing import Dict, Any, List, Optional

from utils.db_connection import get_conn

HOST = "cricbuzz-cricket.p.rapidapi.com"

# Format preference order - prioritizes international cricket formats
# Ensures consistent data selection when players appear in multiple formats
FORMAT_PREFERENCE = ["ODI", "ODIs", "One Day", "T20I", "T20", "TESTS", "TEST", "Tests", "Test", "IPL"]


# ---------- HTTP Request Utilities with Rate Limiting ----------
def _headers() -> Dict[str, str]:
    """
    Generate HTTP headers for Cricbuzz API authentication.
    
    Retrieves API credentials from environment variables (RAPIDAPI_KEY).
    Raises RuntimeError if credentials are not configured.
    """
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY not found (.env or Streamlit secrets).")
    return {"x-rapidapi-key": key, "x-rapidapi-host": HOST}

def _get(path: str, params: Dict[str, Any] | None = None, max_retries: int = 5) -> Dict[str, Any]:
    """
    Make HTTP GET request to Cricbuzz API with retry and backoff logic.
    
    Implements exponential backoff to handle rate limiting gracefully.
    Respects API quota limits by spacing requests appropriately.
    Returns parsed JSON response from successful requests.
    """
    url = f"https://{HOST}{path}"
    wait = 1.6  # initial sleep between calls
    for attempt in range(max_retries):
        r = requests.get(url, headers=_headers(), params=params or {}, timeout=25)
        if r.status_code == 429:
            ra = r.headers.get("Retry-After")
            backoff = float(ra) if ra else (wait + attempt * 0.8)
            time.sleep(backoff)
            continue
        if r.status_code == 403:
            raise RuntimeError("403 from RapidAPI. Check your subscription, host header, or API key.")
        r.raise_for_status()
        time.sleep(wait)  # throttle
        return r.json()
    raise RuntimeError("Gave up after repeated 429 responses.")

# Try the new path first; if it 404s, try the legacy one.
def _fetch_batting(pid: str) -> Dict[str, Any]:
    try:
        return _get(f"/stats/v1/player/{pid}/batting")
    except Exception:
        return _get("/players/get-batting", {"playerId": pid})

def _fetch_bowling(pid: str) -> Dict[str, Any]:
    try:
        return _get(f"/stats/v1/player/{pid}/bowling")
    except Exception:
        return _get("/players/get-bowling", {"playerId": pid})


# ------------------------
# Parsing helpers
# ------------------------
def _to_int(x) -> int:
    try:
        return int(float(str(x).replace(",", "").strip()))
    except Exception:
        return 0

def _to_float(x) -> Optional[float]:
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return None

def _find_format_index(headers: List[str]) -> Optional[int]:
    """
    headers example: ["ROWHEADER", "Test", "ODI", "T20", "IPL"]
    Return index of preferred format. Allow substring matches (t20i vs t20).
    """
    if not isinstance(headers, list) or not headers:
        return None
    lowered = [h.lower() for h in headers]

    def non_row():
        return [i for i, h in enumerate(lowered) if h != "rowheader"]

    for want in FORMAT_PREFERENCE:
        wl = want.lower()
        for i, h in enumerate(lowered):
            if h == "rowheader":
                continue
            if wl == h or wl in h or h in wl:
                return i
    inds = non_row()
    return inds[0] if inds else None

def _row_value(rows: List[Dict[str, Any]], labels: List[str], col: int, numeric=True):
    """
    rows: [{"values": ["Runs","2547","1634","1831","3641"]}, ...]
    """
    for r in rows:
        vals = r.get("values") or []
        if not vals:
            continue
        head = str(vals[0]).strip().lower()
        for lab in labels:
            if head == lab.lower():
                if 0 <= col < len(vals):
                    v = vals[col]
                    return _to_float(v) if numeric else v
    return None

def _parse_batting(bat_json: Dict[str, Any]) -> Dict[str, Any]:
    headers = bat_json.get("headers") or []
    rows = bat_json.get("values") or []
    if not headers or not rows:
        return {"total_runs": 0, "batting_average": None, "strike_rate": None}

    col = _find_format_index(headers)
    if col is None:
        return {"total_runs": 0, "batting_average": None, "strike_rate": None}

    runs = _row_value(rows, ["Runs"], col, numeric=True)
    avg  = _row_value(rows, ["Average", "Avg"], col, numeric=True)
    sr   = _row_value(rows, ["SR", "Strike Rate", "StrikeRate"], col, numeric=True)

    return {
        "total_runs": int(runs or 0),
        "batting_average": avg,
        "strike_rate": sr,
    }

def _parse_bowling(bowl_json: Dict[str, Any]) -> Dict[str, Any]:
    headers = bowl_json.get("headers") or []
    rows = bowl_json.get("values") or []
    if not headers or not rows:
        return {"total_wickets": 0, "bowling_average": None, "economy_rate": None}

    col = _find_format_index(headers)
    if col is None:
        return {"total_wickets": 0, "bowling_average": None, "economy_rate": None}

    wkts = _row_value(rows, ["Wickets", "Wkts"], col, numeric=True)
    avg  = _row_value(rows, ["Avg", "Average"], col, numeric=True)
    eco  = _row_value(rows, ["Eco", "Economy"], col, numeric=True)

    return {
        "total_wickets": int(wkts or 0),
        "bowling_average": avg,
        "economy_rate": eco,
    }


# ------------------------
# DB upsert (with playing_role safety)
# ------------------------
def _ensure_playing_role_column(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(players)")
    cols = [r[1] for r in cur.fetchall()]
    if "playing_role" not in cols:
        cur.execute("ALTER TABLE players ADD COLUMN playing_role TEXT")
        conn.commit()

def upsert_players(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    conn = get_conn()
    _ensure_playing_role_column(conn)
    cur = conn.cursor()
    # ensure ON CONFLICT works on (name, country)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_players_name_country
        ON players(name, country);
    """)
    cur.executemany(
        """
        INSERT INTO players
          (name, country, role, playing_role, total_runs, batting_average, strike_rate,
           total_wickets, bowling_average, economy_rate)
        VALUES
          (:name, :country, :role, :playing_role, :total_runs, :batting_average, :strike_rate,
           :total_wickets, :bowling_average, :economy_rate)
        ON CONFLICT(name, country) DO UPDATE SET
          role=excluded.role,
          playing_role=excluded.playing_role,
          total_runs=excluded.total_runs,
          batting_average=excluded.batting_average,
          strike_rate=excluded.strike_rate,
          total_wickets=excluded.total_wickets,
          bowling_average=excluded.bowling_average,
          economy_rate=excluded.economy_rate;
        """,
        rows,
    )
    conn.commit()
    conn.close()


# ------------------------
# Main loaders
# ------------------------
def load_from_trending(trending_json: Dict[str, Any], max_players: int = 30) -> None:
    """
    trending_json: object from players/list-trending
    For each trending player -> get-batting + get-bowling -> parse -> UPSERT.
    """
    players = trending_json.get("player", []) or trending_json.get("players", [])
    rows: List[Dict[str, Any]] = []

    for p in players[:max_players]:
        pid = p.get("id") or p.get("playerId")
        name = p.get("name") or "Unknown"
        country = p.get("teamName") or p.get("country") or "Unknown"
        if not pid:
            continue

        row = {
            "name": name,
            "country": country,
            "role": "Batter",
            "playing_role": "Batter",
            "total_runs": 0,
            "batting_average": None,
            "strike_rate": None,
            "total_wickets": 0,
            "bowling_average": None,
            "economy_rate": None,
        }

        try:
            bat = _fetch_batting(pid)
            row.update(_parse_batting(bat))
        except Exception as e:
            print(f"[get-batting] playerId={pid} failed: {e}")

        try:
            bowl = _fetch_bowling(pid)
            row.update(_parse_bowling(bowl))
        except Exception as e:
            print(f"[get-bowling] playerId={pid} failed: {e}")

        # Infer role
        if (row["total_wickets"] or 0) > 0 and (row["total_runs"] or 0) > 0:
            row["role"] = row["playing_role"] = "All-rounder"
        elif (row["total_wickets"] or 0) > 0:
            row["role"] = row["playing_role"] = "Bowler"
        else:
            row["role"] = row["playing_role"] = "Batter"

        rows.append(row)

    upsert_players(rows)

def load_by_ids(id_name_country: List[tuple[str, str, str]]) -> None:
    """
    Manually load specific players by (id, name, country).
    """
    rows: List[Dict[str, Any]] = []
    for pid, name, country in id_name_country:
        row = {
            "name": name,
            "country": country,
            "role": "Batter",
            "playing_role": "Batter",
            "total_runs": 0,
            "batting_average": None,
            "strike_rate": None,
            "total_wickets": 0,
            "bowling_average": None,
            "economy_rate": None,
        }
        try:
            bat = _fetch_batting(pid)
            row.update(_parse_batting(bat))
        except Exception as e:
            print(f"[manual batting] {pid} failed: {e}")
        try:
            bowl = _fetch_bowling(pid)
            row.update(_parse_bowling(bowl))
        except Exception as e:
            print(f"[manual bowling] {pid} failed: {e}")

        if (row["total_wickets"] or 0) > 0 and (row["total_runs"] or 0) > 0:
            row["role"] = row["playing_role"] = "All-rounder"
        elif (row["total_wickets"] or 0) > 0:
            row["role"] = row["playing_role"] = "Bowler"
        else:
            row["role"] = row["playing_role"] = "Batter"

        rows.append(row)

    upsert_players(rows)
