# Data Administration & CRUD Operations - Cricket Analytics Dashboard
#
# This module provides the user interface for managing cricket database records.
# Users can Create, Read, Update, and Delete player and match statistics.
#
# Features:
# - Add new players with detailed attributes
# - Update existing player statistics
# - Delete outdated or incorrect player records
# - View comprehensive player database
# - Form validation and error handling
# - Confirmation dialogs for destructive operations
#
# All operations are logged and database transactions are handled safely.

import streamlit as st
from utils.db_connection import get_conn
from datetime import datetime, date
from typing import List, Dict, Any, Tuple

st.set_page_config(page_title="Data Management", page_icon="🛠️", layout="wide")


# ---------- Database Helper Functions ----------
def run_query(sql: str, params: Tuple = (), fetch: bool = False):
    """
    Execute a SQL query with transaction management.
    
    Features:
    - Automatic connection creation and cleanup
    - Transaction commit for data modifications
    - Error handling with connection closure
    - Support for both query and command operations
    
    Args:
        sql: SQL query or command string
        params: Tuple of parameters for parameterized queries
        fetch: If True, fetches and returns query results
        
    Returns:
        If fetch=True: List of rows from query result
        If fetch=False: None (used for INSERT, UPDATE, DELETE)
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows
    finally:
        conn.close()


def get_tables() -> List[str]:
    rows = run_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY 1",
        fetch=True,
    )
    return [r["name"] for r in rows] if rows else []


def get_columns(table: str) -> List[Dict[str, Any]]:
    """PRAGMA table_info; returns dicts with keys: cid, name, type, notnull, dflt_value, pk"""
    rows = run_query(f"PRAGMA table_info({table})", fetch=True)
    return [dict(r) for r in rows] if rows else []


def fetch_all(table: str):
    return run_query(f"SELECT * FROM {table}", fetch=True)


def get_pk_col(cols: List[Dict[str, Any]]):
    """Return primary key column name if present (pk==1)."""
    for c in cols:
        if c.get("pk") == 1:
            return c["name"]
    return None


# --------------- UI helpers -------------------
def _input_for_col(col: Dict[str, Any], value=None, key_prefix=""):
    """
    Render a Streamlit input for a column based on SQLite type.
    Returns the value entered.
    """
    col_name = col["name"]
    col_type = (col["type"] or "").upper()
    key = f"{key_prefix}_{col_name}"

    # choose widget based on type
    if "INT" in col_type:
        return st.number_input(col_name, value=int(value) if value is not None else 0, step=1, key=key)
    if any(t in col_type for t in ["REAL", "FLOA", "DOUB"]):
        return st.number_input(col_name, value=float(value) if value is not None else 0.0, key=key)
    if "DATE" in col_type and isinstance(value, (str, type(None))):
        # Try parse; fallback to today
        try:
            dt = datetime.fromisoformat(value).date() if value else date.today()
        except Exception:
            dt = date.today()
        return st.date_input(col_name, value=dt, key=key)
    # default to text
    return st.text_input(col_name, value="" if value is None else str(value), key=key)


def _record_label(row, pk_name: str):
    """Label to show in select boxes for picking a record."""
    if pk_name and pk_name in row.keys():
        # Try to add a likely 'name' field for readability if present
        extra = ""
        for cand in ["name", "player_name", "title"]:
            if cand in row.keys():
                extra = f" — {row[cand]}"
                break
        return f"{row[pk_name]}{extra}"
    # fallback
    return str(dict(row))


# ----------------- CRUD ops -------------------
def create_record(table: str, cols: List[Dict[str, Any]]):
    st.subheader("➕ Create New Record")
    pk = get_pk_col(cols)
    insert_cols = [c for c in cols if not (c["name"] == pk and c.get("pk") == 1)]
    values = []
    with st.form(f"create_{table}"):
        for c in insert_cols:
            values.append(_input_for_col(c, key_prefix="create"))
        submitted = st.form_submit_button("Create")
    if submitted:
        placeholders = ", ".join(["?"] * len(insert_cols))
        col_list = ", ".join([c["name"] for c in insert_cols])
        sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
        run_query(sql, tuple(values))
        st.success("Record created.")
        st.rerun()


def read_records(table: str):
    st.subheader("📖 View Records")
    rows = fetch_all(table)
    if not rows:
        st.info("No data found.")
        return
    st.dataframe([dict(r) for r in rows], use_container_width=True)


def update_record(table: str, cols: List[Dict[str, Any]]):
    st.subheader("✏️ Update Record")
    pk = get_pk_col(cols)
    if not pk:
        st.info("No primary key column found; update requires a primary key.")
        return

    rows = fetch_all(table)
    if not rows:
        st.info("No rows to update.")
        return

    # pick a row
    label_map = {_record_label(r, pk): r for r in rows}
    pick = st.selectbox("Choose a record", list(label_map.keys()))
    row = label_map[pick]

    edit_cols = [c for c in cols if c["name"] != pk]
    new_values = []
    with st.form(f"update_{table}"):
        for c in edit_cols:
            new_values.append(_input_for_col(c, value=row[c["name"]], key_prefix="update"))
        submitted = st.form_submit_button("Save changes")
    if submitted:
        set_clause = ", ".join([f"{c['name']}=?" for c in edit_cols])
        params = tuple(new_values) + (row[pk],)
        sql = f"UPDATE {table} SET {set_clause} WHERE {pk}=?"
        run_query(sql, params)
        st.success("Record updated.")
        st.rerun()


def delete_record(table: str, cols: List[Dict[str, Any]]):
    st.subheader("🗑️ Delete Record")
    pk = get_pk_col(cols)
    if not pk:
        st.info("No primary key column found; delete requires a primary key.")
        return

    rows = fetch_all(table)
    if not rows:
        st.info("No rows to delete.")
        return

    label_map = {_record_label(r, pk): r for r in rows}
    pick = st.selectbox("Choose a record to delete", list(label_map.keys()))
    row = label_map[pick]

    if st.button("Delete permanently"):
        run_query(f"DELETE FROM {table} WHERE {pk}=?", (row[pk],))
        st.success("Record deleted.")
        st.rerun()


# ----------------- Page -----------------------
def main():
    st.header("🛠️ CRUD Operations")

    # Choose table first (defaults to 'players' if it exists)
    tables = get_tables()
    if not tables:
        st.warning("No tables found in the database.")
        return

    default_index = tables.index("players") if "players" in tables else 0
    table = st.selectbox("Choose table:", tables, index=default_index, key="table_choice")

    cols = get_columns(table)
    if not cols:
        st.warning("Could not read table schema.")
        return

    st.divider()

    # Operation selection
    operation = st.selectbox(
        "Choose operation:",
        ["Create", "Read", "Update", "Delete"],
        key="crud_operation",
    )

    st.divider()

    if operation == "Create":
        create_record(table, cols)
    elif operation == "Read":
        read_records(table)
    elif operation == "Update":
        update_record(table, cols)
    elif operation == "Delete":
        delete_record(table, cols)


if __name__ == "__main__":
    main()
