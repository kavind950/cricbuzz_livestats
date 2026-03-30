# For testing database and tables 

import argparse
import os
import sqlite3
import sys

def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [r[0] for r in cur.fetchall()]

def list_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    # returns: cid, name, type, notnull, dflt_value, pk
    return [(r[1], r[2]) for r in cur.fetchall()]

def show_rows(conn, table, limit=10):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} LIMIT {limit};")
    rows = cur.fetchall()
    return rows

def main():
    p = argparse.ArgumentParser(description="Check tables in an SQLite DB.")
    p.add_argument("db", help="Path to SQLite database file (e.g. cricket_db or cricket.db)")
    p.add_argument("--columns", action="store_true", help="Also print columns for each table")
    p.add_argument("--rows", action="store_true", help="Also print rows for each table")
    args = p.parse_args()

    db_path = args.db

    if not os.path.exists(db_path):
        print(f"Database '{db_path}' does NOT exist in the current folder.")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"Could not open database '{db_path}': {e}")
        sys.exit(2)

    tables = list_tables(conn)

    if tables:
        print(f"Database '{db_path}' exists with {len(tables)} table(s):")
        for t in tables:
            print(f"- {t}")
            if args.columns:
                cols = list_columns(conn, t)
                for name, coltype in cols:
                    print(f"    • {name} ({coltype})")
            if args.rows:
                rows = show_rows(conn, t)
                if rows:
                    print(f"      Sample rows from '{t}':")
                    for r in rows:
                        print(f"    • {r}")
                else:
                    print(f"      No rows found in '{t}'.")
    else:
        print(f"Database '{db_path}' exists but has no user tables.")

    conn.close()

if __name__ == "__main__":
    main()
