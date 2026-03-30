# utils/load_recent.py
import os
import re
import time
from typing import Dict, Any, List, Optional

import requests
from utils.db_connection import get_conn

HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
BASE = f"https://{HOST}"


def _headers():
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY not set")
    return {"x-rapidapi-key": key, "x-rapidapi-host": HOST}


def _get(path: str, params: Dict[str, Any] | None = None, retries: int = 3):
    url = f"{BASE}{path}"
    for i in range(retries):
        r = requests.get(url, headers=_headers(), params=params or {}, timeout=25)
        if r.status_code == 429:
            time.sleep(1.2 + i)
            continue
        r.raise_for_status()
        time.sleep(0.6)  # gentle throttle
        return r.json()
    raise RuntimeError("Too many 429s")


def _first_nonnull(*args):
    for a in args:
        if a is not None:
            return a
    return None


def _team_name(obj: Any) -> Optional[str]:
    """Cricbuzz returns many shapes for a team field."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    # {..., "team": {"name": "India"}}
    if isinstance(obj, dict):
        if "team" in obj and isinstance(obj["team"], dict):
            return obj["team"].get("name") or obj["team"].get("shortName")
        return obj.get("name") or obj.get("shortName")
    return None


def _ms_to_iso(ms_like: Any) -> Optional[str]:
    """Convert unix epoch (ms or s) to UTC ISO 'YYYY-MM-DD HH:MM:SS'."""
    if not ms_like:
        return None
    try:
        ms = int(ms_like)
    except Exception:
        return None
    if ms > 2_000_000_000_000:  # extremely unlikely (bad value)
        return None
    # handle ms vs s
    if ms > 2_000_000_000:  # looks like ms
        sec = ms // 1000
    else:
        sec = ms
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sec))


def _normalize_status(raw: str) -> str:
    s = (raw or "").lower()
    if any(k in s for k in [" won by ", "won the match", "match tied", "no result", "draw", "abandoned"]):
        return "completed"
    if any(k in s for k in ["live", "stumps", "innings break", "drinks"]):
        return "live"
    return "upcoming"


def _parse_margin(status_text: str) -> tuple[Optional[int], Optional[str]]:
    txt = (status_text or "").lower()
    # "xxx won by 23 runs" / "xxx won by 4 wickets"
    m = re.search(r"won by\s+(\d+)\s+(run|runs|wicket|wickets)", txt)
    if not m:
        return None, None
    val = int(m.group(1))
    typ = "runs" if "run" in m.group(2) else "wickets"
    return val, typ


# ---------- ingest recent matches ----------

def ingest_recent_matches(max_matches: int = 40) -> int:
    """
    Pulls 'matches/v1/recent' and populates matches, venues, series (best-effort).
    - stores ISO UTC start_time so SQLite date() works
    - normalizes status to: upcoming | live | completed
    """
    data = _get("/matches/v1/recent")
    buckets: List[Dict[str, Any]] = data.get("typeMatches") or []

    conn = get_conn()
    cur = conn.cursor()
    inserted = 0

    for bucket in buckets:
        match_type = bucket.get("matchType")  # e.g., 'International', 'League', sometimes 'ODI'/'T20I'
        for sm in bucket.get("seriesMatches", []):
            wrap = sm.get("seriesAdWrapper") or {}
            series_obj = wrap.get("series") or {}
            series_id = str(series_obj.get("id") or series_obj.get("seriesId") or "") or None
            series_name = series_obj.get("name") or wrap.get("seriesName")
            host_country = series_obj.get("hostCountry")

            if series_id:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO series(series_id, series_name, host_country, match_type)
                    VALUES(?,?,?,?)
                """,
                    (series_id, series_name, host_country, match_type),
                )

            # List of matches: usually under 'matches'
            matches_list = wrap.get("matches") or wrap.get("seriesMatches") or []
            for mwrap in matches_list:
                m = mwrap.get("matchInfo") or mwrap.get("matchHeader") or mwrap
                mid = str(m.get("matchId") or m.get("id") or "")
                if not mid:
                    continue

                t1 = _team_name(m.get("team1") or m.get("homeTeam"))
                t2 = _team_name(m.get("team2") or m.get("awayTeam"))
                desc = _first_nonnull(m.get("matchDesc"), m.get("seriesName"), series_name, "")
                status_text = (m.get("status") or "").strip()
                status_norm = _normalize_status(status_text)

                mst = _first_nonnull(m.get("startDate"), m.get("startTime"))
                mst_iso = _ms_to_iso(mst)

                mformat = _first_nonnull(m.get("matchFormat"), m.get("matchType"), match_type)

                vinfo = m.get("venueInfo") or {}
                ground = vinfo.get("ground")
                if isinstance(ground, dict):
                    venue_name = ground.get("name") or ground.get("shortName")
                    venue_city = ground.get("city") or vinfo.get("city")
                else:
                    venue_name = ground or vinfo.get("name")
                    venue_city = vinfo.get("city")
                venue_country = vinfo.get("country")
                vid = _first_nonnull(vinfo.get("id"), vinfo.get("groundId"))
                venue_id = str(vid) if vid else None

                if venue_id:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO venues(venue_id, name, city, country)
                        VALUES(?,?,?,?)
                    """,
                        (venue_id, venue_name, venue_city, venue_country),
                    )

                # winner + margin (best-effort)
                winner = _first_nonnull(
                    m.get("winningTeam"),
                    (_team_name(m.get("team1")) if (m.get("team1") or {}).get("isWinner") else None),
                    (_team_name(m.get("team2")) if (m.get("team2") or {}).get("isWinner") else None),
                )
                victory_margin, victory_type = _parse_margin(status_text)

                # toss details (sometimes missing)
                toss_winner = (m.get("tossResults") or {}).get("tossWinner")
                toss_decision = (m.get("tossResults") or {}).get("decision")

                cur.execute(
                    """
                    INSERT OR REPLACE INTO matches(
                        match_id, description, series_name, match_type, status, start_time,
                        team1, team2, venue, city, venue_country,
                        winner, victory_margin, victory_type,
                        toss_winner, toss_decision, venue_id, series_id
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                    (
                        mid, desc, series_name, mformat, status_norm, mst_iso,
                        t1, t2, venue_name, venue_city, venue_country,
                        winner, victory_margin, victory_type,
                        toss_winner, toss_decision, venue_id, series_id,
                    ),
                )
                inserted += 1
                if inserted >= max_matches:
                    break
            if inserted >= max_matches:
                break
        if inserted >= max_matches:
            break

    conn.commit()
    conn.close()
    return inserted


# ---------- per-match scorecard -> innings tables ----------

def _overs_to_balls(overs_val: Any) -> Optional[int]:
    """
    Convert 'overs' (Cricbuzz often sends decimal in base-10, where .2 == 2 balls)
    to total balls bowled.
    """
    if overs_val is None:
        return None
    try:
        f = float(overs_val)
    except Exception:
        return None
    ov = int(f)
    frac = round((f - ov), 1)
    balls = ov * 6 + int(round(frac * 10))
    return balls


def ingest_scorecards_for_recent(limit: int = 15):
    """
    For the most recent 'limit' matches, fetch a scorecard and populate:
      - batting_innings
      - bowling_spells
      - partnerships (naive: adjacent positions, 50+)
    """
    conn = get_conn()
    cur = conn.cursor()
    mids = [r[0] for r in cur.execute(
        "SELECT match_id FROM matches WHERE start_time IS NOT NULL ORDER BY datetime(start_time) DESC LIMIT ?",
        (limit,),
    ).fetchall()]

    for mid in mids:
        payload = None
        for path in ("/mcenter/v1/scorecard", "/matches/v1/scorecard", "/mcenter/v1/match-scorecard"):
            try:
                payload = _get(path, {"matchId": mid})
                break
            except Exception:
                continue
        if not payload:
            continue

        # Try to find innings arrays across variants
        innings_blocks = []
        if isinstance(payload.get("scorecard"), list):
            innings_blocks = payload["scorecard"]
        elif isinstance(payload.get("innings"), list):
            innings_blocks = payload["innings"]
        elif isinstance(payload.get("matchScore"), dict):
            innings_blocks = (payload["matchScore"].get("innings") or [])

        # wipe any previous rows for this match
        cur.execute("DELETE FROM batting_innings WHERE match_id=?", (mid,))
        cur.execute("DELETE FROM bowling_spells WHERE match_id=?", (mid,))
        cur.execute("DELETE FROM partnerships WHERE match_id=?", (mid,))

        for idx, inn in enumerate(innings_blocks, start=1):
            team = _first_nonnull(inn.get("batTeamName"), inn.get("batTeam"), inn.get("team"), "")

            bats = inn.get("batsmenData") or inn.get("batsmen") or []
            if isinstance(bats, dict):
                bats = list(bats.values())

            order = []
            for b in bats:
                name = _first_nonnull(b.get("name"), b.get("batName"), b.get("batsmanName"), "")
                pid = _first_nonnull(b.get("id"), b.get("playerId"), b.get("batId"))
                runs = int(_first_nonnull(b.get("runs"), b.get("r"), 0) or 0)
                balls = int(_first_nonnull(b.get("balls"), b.get("b"), 0) or 0)
                sr = float(_first_nonnull(b.get("strikeRate"), b.get("sr"), b.get("srNum"), 0) or 0) or None
                pos = int(_first_nonnull(b.get("position"), b.get("battingPosition"), len(order) + 1) or 0)

                cur.execute(
                    """
                    INSERT INTO batting_innings(
                        match_id, innings_no, team, player_name, player_id, position, runs, balls, strike_rate
                    ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                    (mid, idx, team, name, str(pid) if pid else None, pos, runs, balls, sr),
                )
                order.append((pos, name, runs))

            # simple partnerships from adjacent batting positions
            order.sort(key=lambda x: (x[0] if x[0] else 99))
            for i in range(0, max(0, len(order) - 1)):
                _, b1, r1 = order[i]
                _, b2, r2 = order[i + 1]
                pruns = (r1 or 0) + (r2 or 0)
                if pruns >= 50:
                    cur.execute(
                        "INSERT INTO partnerships(match_id, innings_no, batter1, batter2, runs) VALUES(?,?,?,?,?)",
                        (mid, idx, b1, b2, pruns),
                    )

            # bowling
            bowls = inn.get("bowlerData") or inn.get("bowlers") or []
            if isinstance(bowls, dict):
                bowls = list(bowls.values())
            for bw in bowls:
                name = _first_nonnull(bw.get("name"), bw.get("bowlerName"), bw.get("bowlName"), "")
                pid = _first_nonnull(bw.get("id"), bw.get("playerId"), bw.get("bowlId"))
                runs = int(_first_nonnull(bw.get("runs"), bw.get("r"), 0) or 0)
                wkts = int(_first_nonnull(bw.get("wickets"), bw.get("w"), 0) or 0)
                overs = _first_nonnull(bw.get("overs"), bw.get("o"), 0)
                balls = _overs_to_balls(overs)
                eco = float(_first_nonnull(bw.get("economy"), bw.get("econ"), 0) or 0) or None

                cur.execute(
                    """
                    INSERT INTO bowling_spells(
                        match_id, innings_no, bowler_name, bowler_id, overs, balls, runs, wickets, economy
                    ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                    (mid, idx, name, str(pid) if pid else None, float(overs or 0), balls, runs, wkts, eco),
                )

        conn.commit()

    conn.close()
