"""
test_app.py - Comprehensive automated test suite for Personal Study Tracker.
Validates Database CRUD, Data Normalization, UI Event Handling, Edge Cases,
and Full Application Lifecycle.
"""

import os
import sys
import tempfile
import tkinter as tk
from datetime import date as dt_date

# Ensure utf-8 encoding for console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import database
from ui import StudyTrackerApp


def test_database_crud_and_metrics():
    print("\n--- 1. Testing Database CRUD, Aggregations & Case Insensitivity ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db = tmp.name

    try:
        database.init_db(temp_db)
        
        # Initial empty state
        stats0 = database.get_summary_stats(temp_db)
        assert stats0["total_sessions"] == 0
        assert stats0["total_minutes"] == 0
        assert stats0["total_time_formatted"] == "0m"
        assert stats0["today_minutes"] == 0
        assert stats0["today_time_formatted"] == "0m"
        assert stats0["top_subject"] == "None yet"

        today = dt_date.today().isoformat()
        past_date = "2026-08-20"

        # Add requested test sessions
        id1 = database.add_session(today, "Python", "Dictionaries", 60, "Practiced dictionary operations", temp_db)
        id2 = database.add_session(today, "python", "Functions", 45, "Learned function parameters", temp_db)
        id3 = database.add_session(past_date, "SQL", "SELECT queries", 30, "Practiced basic SQL", temp_db)

        assert id1 > 0 and id2 > 0 and id3 > 0

        # Retrieve and verify all sessions
        sessions = database.get_all_sessions(temp_db)
        assert len(sessions) == 3

        # Verify summary stats
        stats = database.get_summary_stats(temp_db)
        assert stats["total_sessions"] == 3
        assert stats["total_minutes"] == 135  # 60 + 45 + 30
        assert stats["total_time_formatted"] == "2h 15m"
        assert stats["today_minutes"] == 105   # 60 + 45
        assert stats["today_time_formatted"] == "1h 45m"
        # Python should be grouped case-insensitively (60 + 45 = 105m = 1h 45m)
        assert "Python" in stats["top_subject"] or "python" in stats["top_subject"]
        assert "1h 45m" in stats["top_subject"]

        # Test deletion
        deleted = database.delete_session(id3, temp_db)
        assert deleted is True
        sessions_after = database.get_all_sessions(temp_db)
        assert len(sessions_after) == 2

        stats_after = database.get_summary_stats(temp_db)
        assert stats_after["total_sessions"] == 2
        assert stats_after["total_minutes"] == 105
        assert stats_after["total_time_formatted"] == "1h 45m"

        print("✓ Database CRUD, metrics calculation, and case-insensitivity tests PASSED!")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


def test_date_and_duration_normalization():
    print("\n--- 2. Testing Date & Duration Normalization ---")
    # Date tests
    today = dt_date.today().isoformat()
    assert database.normalize_date_string(today) == today
    assert database.normalize_date_string("2026-8-26") == "2026-08-26"
    assert database.normalize_date_string("2026/08/26") == "2026-08-26"

    # Invalid dates
    for invalid in ["", "invalid", "2026-13-45", "not-a-date"]:
        try:
            database.normalize_date_string(invalid)
            assert False, f"Expected ValueError for '{invalid}'"
        except ValueError:
            pass

    # Duration formatting
    assert database.format_duration(0) == "0m"
    assert database.format_duration(25) == "25m"
    assert database.format_duration(60) == "1h"
    assert database.format_duration(95) == "1h 35m"
    assert database.format_duration(120) == "2h"
    print("✓ Normalization tests PASSED!")


def test_ui_full_flow():
    print("\n--- 3. Testing Full UI Flow, Live Search & Dashboard Sync ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db = tmp.name

    try:
        database.init_db(temp_db)

        root = tk.Tk()
        root.withdraw()  # Run headless for automated test

        # Override DEFAULT_DB_PATH for this test run
        orig_db_path = database.DEFAULT_DB_PATH
        database.DEFAULT_DB_PATH = temp_db

        app = StudyTrackerApp(root)

        # 1. Add Session 1 via UI
        today = dt_date.today().isoformat()
        app.entry_date.delete(0, tk.END)
        app.entry_date.insert(0, today)
        app.combo_subject.set("Python")
        app.entry_topic.delete(0, tk.END)
        app.entry_topic.insert(0, "Dictionaries")
        app.entry_duration.delete(0, tk.END)
        app.entry_duration.insert(0, "60")
        app.txt_notes.delete("1.0", tk.END)
        app.txt_notes.insert("1.0", "Practiced dictionary operations")
        app.handle_add_session()

        # 2. Add Session 2 via UI (using duration preset 45m)
        app.entry_date.delete(0, tk.END)
        app.entry_date.insert(0, today)
        app.combo_subject.set("Python")
        app.entry_topic.delete(0, tk.END)
        app.entry_topic.insert(0, "Functions")
        app._set_duration_preset(45)
        app.txt_notes.delete("1.0", tk.END)
        app.txt_notes.insert("1.0", "Learned function parameters")
        app.handle_add_session()

        # 3. Add Session 3 via UI (custom subject and suffix duration '30 mins')
        past_date = "2026-08-20"
        app.entry_date.delete(0, tk.END)
        app.entry_date.insert(0, past_date)
        app.combo_subject.set("SQL Database")
        app.entry_topic.delete(0, tk.END)
        app.entry_topic.insert(0, "SELECT queries")
        app.entry_duration.delete(0, tk.END)
        app.entry_duration.insert(0, "30 mins")  # tests suffix cleaning
        app.txt_notes.delete("1.0", tk.END)
        app.txt_notes.insert("1.0", "Practiced basic SQL")
        app.handle_add_session()

        # Verify UI Table & Dashboard Card states
        items = app.tree.get_children()
        assert len(items) == 3, f"Expected 3 rows in Treeview, got {len(items)}"

        assert app.kpi_labels["Total Sessions"].cget("text") == "3"
        assert app.kpi_labels["Total Study Time"].cget("text") == "2h 15m"
        assert app.kpi_labels["Today's Study Time"].cget("text") == "1h 45m"
        assert "Python" in app.kpi_labels["Most-Studied Subject"].cget("text")

        # 4. Test Live Search Filtering
        # Search by Topic
        app.var_search.set("Dictionaries")
        app.filter_table()
        assert len(app.tree.get_children()) == 1

        # Search by Subject
        app.var_search.set("Python")
        app.filter_table()
        assert len(app.tree.get_children()) == 2

        # Search by Notes
        app.var_search.set("basic SQL")
        app.filter_table()
        assert len(app.tree.get_children()) == 1

        # Search by Date
        app.var_search.set(past_date)
        app.filter_table()
        assert len(app.tree.get_children()) == 1

        # Clear search
        app.var_search.set("")
        app.filter_table()
        assert len(app.tree.get_children()) == 3

        # 5. Test Form Clear
        app.handle_clear_form()
        assert app.combo_subject.get() == ""
        assert app.entry_topic.get() == ""
        assert app.entry_duration.get() == ""

        # 6. Test Persistence: Reopen app with same database
        root.destroy()

        root2 = tk.Tk()
        root2.withdraw()
        app2 = StudyTrackerApp(root2)
        assert len(app2.tree.get_children()) == 3
        assert app2.kpi_labels["Total Sessions"].cget("text") == "3"
        assert app2.kpi_labels["Total Study Time"].cget("text") == "2h 15m"
        root2.destroy()

        # Restore original db path
        database.DEFAULT_DB_PATH = orig_db_path
        print("✓ Full UI flow, search filtering, and data persistence tests PASSED!")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


def test_edge_cases():
    print("\n--- 4. Testing Edge Cases & Safety Guards ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db = tmp.name

    try:
        database.init_db(temp_db)

        # 1. Notes with quotes, newlines, and special characters
        special_notes = 'Learned "special" quotes & math symbols: π, ∑, <html> & \nmulti-line insights.'
        id_spec = database.add_session("2026-08-26", "Math & Physics", "Advanced Calculus", 75, special_notes, temp_db)
        assert id_spec > 0

        rows = database.get_all_sessions(temp_db)
        assert len(rows) == 1
        assert rows[0]["notes"] == special_notes

        # 2. Deleting non-existent ID
        deleted_fake = database.delete_session(99999, temp_db)
        assert deleted_fake is False

        # 3. Empty notes handling
        id_empty_notes = database.add_session("2026-08-26", "English", "Grammar", 30, "", temp_db)
        assert id_empty_notes > 0
        rows_empty = database.get_all_sessions(temp_db)
        assert len(rows_empty) == 2

        # 4. Zero and negative minutes formatting
        assert database.format_duration(-10) == "0m"
        assert database.format_duration(None) == "0m"

        print("✓ Edge cases and safety guards tests PASSED!")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


if __name__ == "__main__":
    test_database_crud_and_metrics()
    test_date_and_duration_normalization()
    test_ui_full_flow()
    test_edge_cases()
    print("\n=======================================================")
    print("🎉 ALL 4 TEST SUITES PASSED FLAWLESSLY WITH ZERO ERRORS!")
    print("=======================================================\n")
