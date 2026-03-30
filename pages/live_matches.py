import os
import time
from datetime import datetime

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv, find_dotenv

# =============================================================================
# Configuration — .env must contain:
# RAPIDAPI_KEY=xxxxxxxxxxxxxxxx
# RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com
# =============================================================================
load_dotenv(find_dotenv(), override=False)
DEFAULT_HOST = "cricbuzz-cricket.p.rapidapi.com"

def get_cfg():
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    api_host = os.getenv("RAPIDAPI_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    return api_key, api_host

def get_headers():
    api_key, api_host = get_cfg()
    if not api_key:
        return None, None, None
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": api_host}
    base_url = f"https://{api_host}"
    return headers, base_url, api_key

# =============================================================================
# API wrappers (cached)
# =============================================================================
@st.cache_data(ttl=60)
def api_matches(base_url, headers, match_type):
    r = requests.get(f"{base_url}/matches/v1/{match_type}", headers=headers, timeout=12)
    return r.status_code, (r.json() if r.content else {})

@st.cache_data(ttl=300)
def api_scorecard(base_url, headers, match_id):
    r = requests.get(f"{base_url}/mcenter/v1/{match_id}/scard", headers=headers, timeout=12)
    return r.status_code, (r.json() if r.content else {})

@st.cache_data(ttl=60)
def api_commentary(base_url, headers, match_id):
    r = requests.get(f"{base_url}/mcenter/v1/{match_id}/comm", headers=headers, timeout=12)
    return r.status_code, (r.json() if r.content else {})

@st.cache_data(ttl=300)
def api_match_info(base_url, headers, match_id):
    r = requests.get(f"{base_url}/mcenter/v1/{match_id}", headers=headers, timeout=12)
    return r.status_code, (r.json() if r.content else {})

# =============================================================================
# Helpers & theming
# =============================================================================
TEMPLATE = "plotly_white"
H_WIDE = 520   # height for wide charts

def convert_ts(ms):
    try:
        return datetime.fromtimestamp(int(ms)/1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "N/A"

def safe_num(v, default=0):
    try:
        return float(v)
    except Exception:
        return default

def innings_header(title, runs, wkts, overs):
    st.markdown(
        f"""
        <div style="background:#0ea5e9;color:#fff;padding:12px 16px;border-radius:10px;margin:8px 0;">
            <span style="font-weight:700;font-size:18px;">{title}</span>
            <span style="margin-left:10px;opacity:.95;">Score: <b>{runs}/{wkts}</b> • Overs: <b>{overs}</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# Visual blocks (wide, below-the-stats layout)
# =============================================================================
def show_batting_section(bat_rows, innings_title):
    """Tables + wide charts stacked vertically to use whitespace."""
    if not bat_rows:
        st.info("No batting data available.")
        return

    df = pd.DataFrame(bat_rows)
    df["Runs"] = df["Runs"].astype(float)
    df["4s"] = df["4s"].astype(float)
    df["6s"] = df["6s"].astype(float)
    df = df.sort_values("Runs", ascending=False).reset_index(drop=True)

    st.subheader("🧍 Batting")
    st.dataframe(
        df[["Batsman", "Runs", "Balls", "4s", "6s", "SR", "Status"]],
        use_container_width=True, hide_index=True
    )

    # Wide horizontal - Runs
    fig_runs = px.bar(
        df[::-1], y="Batsman", x="Runs", orientation="h",
        template=TEMPLATE, title=f"Runs by Batsman — {innings_title}",
        text="Runs"
    )
    fig_runs.update_traces(textposition="outside", cliponaxis=False)
    fig_runs.update_layout(height=H_WIDE, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_runs, use_container_width=True)

    # Wide horizontal - 4s vs 6s
    fig_46 = go.Figure()
    fig_46.add_bar(name="4s", y=df[::-1]["Batsman"], x=df[::-1]["4s"], orientation="h")
    fig_46.add_bar(name="6s", y=df[::-1]["Batsman"], x=df[::-1]["6s"], orientation="h")
    fig_46.update_layout(
        template=TEMPLATE, barmode="group",
        title=f"4s vs 6s — {innings_title}",
        height=H_WIDE, margin=dict(l=10, r=10, t=60, b=10)
    )
    st.plotly_chart(fig_46, use_container_width=True)

def show_bowling_section(bowl_rows, innings_title):
    if not bowl_rows:
        st.info("No bowling data available.")
        return

    df = pd.DataFrame(bowl_rows)
    df["Wickets"] = df["Wickets"].astype(float)
    df["Overs"] = df["Overs"].astype(float)
    df["Economy"] = df["Economy"].astype(float)
    df["Runs"] = df["Runs"].astype(float)
    df = df.sort_values("Wickets", ascending=False).reset_index(drop=True)

    st.subheader("🎯 Bowling")
    st.dataframe(
        df[["Bowler", "Overs", "Maidens", "Runs", "Wickets", "Economy", "Wides"]],
        use_container_width=True, hide_index=True
    )

    # Wide horizontal - wickets
    fig_wkts = px.bar(
        df[::-1], y="Bowler", x="Wickets", orientation="h",
        template=TEMPLATE, title=f"Wickets by Bowler — {innings_title}",
        text="Wickets"
    )
    fig_wkts.update_traces(textposition="outside", cliponaxis=False)
    fig_wkts.update_layout(height=H_WIDE, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_wkts, use_container_width=True)

    # Wide bubble - economy vs runs (size = overs)
    fig_bubble = px.scatter(
        df, x="Economy", y="Runs", size="Overs", color="Wickets",
        hover_name="Bowler", template=TEMPLATE,
        title=f"Economy vs Runs (size=Overs, color=Wickets) — {innings_title}",
    )
    fig_bubble.update_layout(height=H_WIDE, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_bubble, use_container_width=True)

# =============================================================================
# Rendering of cards and details
# =============================================================================
def show_match_card(match_info, match_score, headers, base_url):
    match_id = match_info.get("matchId")
    series_name = match_info.get("seriesName", "")
    desc = match_info.get("matchDesc", "Match")
    fmt = match_info.get("matchFormat", "")
    venue = match_info.get("venueInfo", {})
    ground = venue.get("ground", "—")
    city = venue.get("city", "—")
    state = match_info.get("state", "")
    status = match_info.get("status", "")

    # Card header (lightweight)
    st.markdown(
        '<div style="border:1px solid #e5e7eb;border-radius:12px;padding:14px;margin:10px 0;">',
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"**📘 {series_name or 'Series'}**")
        st.write(f"{desc} • {fmt}")
        st.write(f"🏟️ {ground}, {city}")
        st.write(f"🕒 **{state or '—'}** — {status or '—'}")

    with col2:
        t1 = match_info.get("team1", {}).get("teamName", "Team 1")
        t2 = match_info.get("team2", {}).get("teamName", "Team 2")
        t1s = match_score.get("team1Score", {})
        t2s = match_score.get("team2Score", {})

        def first_innings_block(s):
            if not isinstance(s, dict): return (None,None,None)
            for k,v in s.items():
                if k.lower().startswith("inngs") and isinstance(v, dict):
                    return v.get("runs",0), v.get("wickets",0), v.get("overs",0)
            return (None,None,None)

        r, w, o = first_innings_block(t1s)
        st.markdown(f"**{t1}:** " + (f"{r}/{w} ({o})" if r is not None else "—"))
        r, w, o = first_innings_block(t2s)
        st.markdown(f"**{t2}:** " + (f"{r}/{w} ({o})" if r is not None else "—"))

    # Details button
    show = st.button("📊 View Details (scorecard & charts)", key=f"btn_{match_id}")
    st.markdown("</div>", unsafe_allow_html=True)

    if show:
        show_match_details(match_id, headers, base_url)

def show_match_details(match_id, headers, base_url):
    if not match_id:
        st.error("Match ID missing.")
        return

    # Compact summary top (so the whitespace below stays for visuals)
    st.markdown(f"### 📊 Match Details — ID: {match_id}")

    code_info, info = api_match_info(base_url, headers, match_id)
    if code_info == 200 and info.get("matchHeader"):
        mh = info["matchHeader"]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Type", mh.get("matchType", "—"))
        with c2: st.metric("Series", mh.get("seriesName", "—"))
        with c3: st.metric("Desc", mh.get("matchDescription", "—"))
        ts = mh.get("matchStartTimestamp")
        with c4: st.metric("Start", datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M") if ts else "—")

    # FULL-WIDTH SECTIONS BELOW (uses whitespace)
    code, data = api_scorecard(base_url, headers, match_id)
    if code != 200 or not data:
        st.info("Scorecard not available yet.")
        return

    # Two known response shapes
    if "scorecard" in data:
        innings_list = data["scorecard"]
    elif "matchScoreDetails" in data:
        innings_list = data["matchScoreDetails"].get("inningsScoreList", [])
    else:
        st.info("Scorecard format not recognized.")
        return

    if not innings_list:
        st.info("No innings data.")
        return

    # Render each innings using wide sections
    for i, inn in enumerate(innings_list, start=1):
        st.markdown("---")
        title = inn.get("batTeamName") or inn.get("inningName") or f"Innings {i}"
        runs = inn.get("score") or inn.get("runs", 0)
        wkts = inn.get("wickets", 0)
        overs = inn.get("overs", 0)
        innings_header(title, runs, wkts, overs)

        # Batting rows (support both schemas)
        bat_rows = []
        bats = inn.get("batsman", []) or list(inn.get("batsmenData", {}).values())
        for b in bats:
            if isinstance(b, dict):
                bat_rows.append({
                    "Batsman": b.get("name") or b.get("batName") or "—",
                    "Runs": safe_num(b.get("runs") or b.get("score")),
                    "Balls": safe_num(b.get("balls") or b.get("ballsFaced")),
                    "4s": safe_num(b.get("fours") or b.get("four")),
                    "6s": safe_num(b.get("sixes") or b.get("six")),
                    "SR": round(safe_num(b.get("strkrate") or b.get("strikeRate") or b.get("sr")), 2),
                    "Status": b.get("outdec") or b.get("dismissal") or b.get("howOut") or "not out",
                })
        show_batting_section(bat_rows, title)

        # Bowling rows
        bowl_rows = []
        bowlers = inn.get("bowler", []) or list(inn.get("bowlersData", {}).values())
        for bw in bowlers:
            if isinstance(bw, dict):
                bowl_rows.append({
                    "Bowler": bw.get("name") or bw.get("bowlName") or "—",
                    "Overs": safe_num(bw.get("overs") or bw.get("oversBowled")),
                    "Maidens": safe_num(bw.get("maidens") or bw.get("maidenOvers")),
                    "Runs": safe_num(bw.get("runs") or bw.get("runsConceded")),
                    "Wickets": safe_num(bw.get("wickets") or bw.get("wicketsTaken")),
                    "Economy": round(safe_num(bw.get("economy") or bw.get("economyRate")), 2),
                    "Wides": safe_num(bw.get("wides") or bw.get("wide")),
                })
        show_bowling_section(bowl_rows, title)

    # Commentary (optional) — put in an expander to keep page clean
    code_c, comm = api_commentary(base_url, headers, match_id)
    if code_c == 200 and isinstance(comm, dict) and comm.get("commentaryList"):
        with st.expander("💬 Latest Commentary (click to expand)"):
            for c in comm["commentaryList"][:15]:
                text = c.get("commText")
                if not text:
                    continue
                over = c.get("overNumber")
                ball = c.get("ballNumber")
                prefix = f"**{over}.{ball}** — " if over is not None and ball is not None else "• "
                st.markdown(prefix + text)

# =============================================================================
# Page composition
# =============================================================================
def render_matches_by_type(matches_json, headers, base_url):
    if not matches_json or "typeMatches" not in matches_json:
        st.info("No matches available.")
        return

    for tm in matches_json.get("typeMatches", []):
        mtype = tm.get("matchType", "Matches")
        series_matches = tm.get("seriesMatches", [])
        if not series_matches:
            continue
        st.markdown(f"## 🏏 {mtype}")
        for sm in series_matches:
            if "seriesAdWrapper" not in sm:
                continue
            series = sm["seriesAdWrapper"]
            sname = series.get("seriesName", "Series")
            matches = series.get("matches", [])
            if not matches:
                continue
            st.markdown(f"### 🏆 {sname}")
            for m in matches:
                match_info = m.get("matchInfo", {})
                match_score = m.get("matchScore", {})
                show_match_card(match_info, match_score, headers, base_url)

# =============================================================================
# Main
# =============================================================================
def main():
    st.set_page_config(page_title="Live Matches - Cricbuzz LiveStats", page_icon="🏏", layout="wide")
    st.header("🏏 Live Cricket Matches")

    headers, base_url, api_key = get_headers()
    st.sidebar.subheader("API")
    if api_key:
        st.sidebar.success("Key loaded from .env")
    else:
        st.sidebar.error("RAPIDAPI_KEY missing in .env")
        st.stop()
    st.sidebar.write(f"Host: `{base_url.replace('https://','')}`")

    match_type = st.radio("Select Match Status:", ("live", "recent", "upcoming"),
                          format_func=lambda s: s.capitalize(), horizontal=True)

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0

    _, c2 = st.columns([3,1])
    with c2:
        if st.button("🔄 Refresh",
                     disabled=time.time() - st.session_state.last_refresh < 10,
                     use_container_width=True):
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()

    with st.spinner(f"Loading {match_type} matches..."):
        code, data = api_matches(base_url, headers, match_type)

    if code == 200:
        render_matches_by_type(data, headers, base_url)
    elif code == 429:
        st.error("API rate limit exceeded (429).")
    elif code == 401:
        st.error("Invalid API key (401). Check RAPIDAPI_KEY in .env.")
    else:
        st.error(f"Failed to fetch matches. HTTP {code}")

if __name__ == "__main__":
    main()
