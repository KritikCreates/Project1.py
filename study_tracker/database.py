"""
database.py - Database operations for the Personal Study Tracker.
Uses Python's built-in sqlite3 module to manage local persistent storage.
"""

import sqlite3
import os
from datetime import date as dt_date, datetime

# Default database file path in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "study_tracker.db")


def get_connection(db_path=None):
    """
    Establishes and returns a connection to the SQLite database.
    Enables sqlite3.Row for dictionary-like column access.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """
    Initializes the database schema by creating the 'sessions' table if it does not exist.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    finally:
        conn.close()


def add_session(date, subject, topic, duration, notes="", db_path=None):
    """
    Adds a new study session record into the SQLite database.
    
    Parameters:
        date (str): Normalized date string in YYYY-MM-DD format.
        subject (str): Subject studied (e.g. 'Python', 'Mathematics').
        topic (str): Specific topic or concept.
        duration (int): Duration in minutes (must be a positive integer).
        notes (str): Optional notes or key takeaways.
        db_path (str): Optional custom database file path.
        
    Returns:
        int: The ID of the newly inserted row.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions (date, subject, topic, duration, notes)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    str(date).strip(),
                    str(subject).strip(),
                    str(topic).strip(),
                    int(duration),
                    str(notes).strip() if notes else ""
                )
            )
            new_id = cursor.lastrowid
        return new_id
    finally:
        conn.close()


def get_all_sessions(db_path=None):
    """
    Retrieves all study sessions from the database, ordered by date descending, then id descending.
    
    Returns:
        list of sqlite3.Row: List of all study sessions.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("""
                SELECT id, date, subject, topic, duration, notes, created_at
                FROM sessions
                ORDER BY date DESC, id DESC;
            """)
            rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def delete_session(session_id, db_path=None):
    """
    Deletes a specific study session by its ID.
    
    Parameters:
        session_id (int): The ID of the session to delete.
        
    Returns:
        bool: True if a record was deleted, False otherwise.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?;", (int(session_id),))
            deleted = cursor.rowcount > 0
        return deleted
    finally:
        conn.close()


def format_duration(total_minutes):
    """
    Helper function to convert minutes into a human-readable 'Xh Ym' or 'Ym' string.
    Example: 90 -> '1h 30m', 45 -> '45m', 0 -> '0m'
    """
    if not total_minutes or total_minutes <= 0:
        return "0m"
    
    total_minutes = int(total_minutes)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def normalize_date_string(date_str):
    """
    Validates and normalizes various date string formats into standard YYYY-MM-DD.
    Supported formats:
      - YYYY-MM-DD (e.g. 2026-08-26, 2026-8-26)
      - YYYY/MM/DD (e.g. 2026/08/26)
      - DD-MM-YYYY or DD/MM/YYYY
    Returns:
      str: Normalized 'YYYY-MM-DD'
    Raises:
      ValueError: If the date string cannot be parsed as a valid calendar date.
    """
    date_str = str(date_str).strip()
    if not date_str:
        raise ValueError("Date cannot be empty.")
    
    # Try ISO format first (YYYY-MM-DD)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(date_str, fmt).date()
            return parsed.isoformat()
        except ValueError:
            continue
            
    # Try splitting by hyphen or slash for flexible single-digit months/days
    cleaned = date_str.replace("/", "-")
    parts = cleaned.split("-")
    if len(parts) == 3:
        try:
            # Check if year is first
            if len(parts[0]) == 4:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            d = dt_date(year, month, day)
            return d.isoformat()
        except Exception:
            pass

    raise ValueError(f"Invalid date format: '{date_str}'. Please use YYYY-MM-DD.")


def get_summary_stats(db_path=None):
    """
    Calculates summary metrics for the dashboard:
    1. Total number of study sessions
    2. Total time studied across all sessions (formatted)
    3. Total time studied today (formatted)
    4. Most-studied subject (name and total duration, grouping case-insensitively)
    
    Returns:
        dict: Summary statistics dictionary.
    """
    conn = get_connection(db_path)
    today_str = dt_date.today().isoformat()  # YYYY-MM-DD
    
    try:
        with conn:
            # 1. Total sessions and total duration
            total_row = conn.execute("""
                SELECT COUNT(*) AS total_count, COALESCE(SUM(duration), 0) AS total_minutes
                FROM sessions;
            """).fetchone()
            
            total_sessions = total_row["total_count"] if total_row else 0
            total_minutes = total_row["total_minutes"] if total_row else 0
            
            # 2. Today's study time
            today_row = conn.execute("""
                SELECT COALESCE(SUM(duration), 0) AS today_minutes
                FROM sessions
                WHERE date = ?;
            """, (today_str,)).fetchone()
            
            today_minutes = today_row["today_minutes"] if today_row else 0
            
            # 3. Most studied subject (grouping case-insensitively for clean stats)
            top_subject_row = conn.execute("""
                SELECT subject, SUM(duration) as subject_minutes
                FROM sessions
                GROUP BY TRIM(subject) COLLATE NOCASE
                ORDER BY subject_minutes DESC
                LIMIT 1;
            """).fetchone()
            
            if top_subject_row and top_subject_row["subject"]:
                top_subject_name = top_subject_row["subject"].strip()
                top_subject_time = format_duration(top_subject_row["subject_minutes"])
                top_subject_display = f"{top_subject_name} ({top_subject_time})"
            else:
                top_subject_display = "None yet"
                
        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "total_time_formatted": format_duration(total_minutes),
            "today_minutes": today_minutes,
            "today_time_formatted": format_duration(today_minutes),
            "top_subject": top_subject_display
        }
    finally:
        conn.close()
