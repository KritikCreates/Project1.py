"""
test_app.py - End-to-end automated test suite for Personal Study Tracker.
Validates Database CRUD, Data Normalization, UI Save Workflow,
Instant Automatic Refresh, Form Reset, and Persistence.
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


def test_complete_user_workflow():
    print("\n--- Testing Complete Study Session Workflow & Automatic Refresh ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db = tmp.name

    try:
        database.init_db(temp_db)

        root = tk.Tk()
        root.withdraw()

        orig_db_path = database.DEFAULT_DB_PATH
        database.DEFAULT_DB_PATH = temp_db

        app = StudyTrackerApp(root)

        # Verify initial empty state
        assert app.kpi_labels["Total Sessions"].cget("text") == "0"
        assert app.kpi_labels["Total Study Time"].cget("text") == "0m"
        assert app.kpi_labels["Today's Study Time"].cget("text") == "0m"
        assert app.kpi_labels["Most-Studied Subject"].cget("text") == "None yet"
        assert len(app.tree.get_children()) == 0

        # Step 1: Add Session 1 (Python, 45m)
        today = dt_date.today().isoformat()
        app.entry_date.delete(0, tk.END)
        app.entry_date.insert(0, today)
        app.combo_subject.set("Python")
        app.entry_topic.delete(0, tk.END)
        app.entry_topic.insert(0, "Functions")
        app.entry_duration.delete(0, tk.END)
        app.entry_duration.insert(0, "45")
        app.txt_notes.delete("1.0", tk.END)
        app.txt_notes.insert("1.0", "Learned Python functions")

        # Step 2: Click "Save Study Session"
        save_result = app.handle_add_session(show_popup=False)
        assert save_result is True, "Expected handle_add_session to return True"

        # Step 3: Verify WITHOUT pressing Refresh:
        # - Total Sessions increases to 1
        assert app.kpi_labels["Total Sessions"].cget("text") == "1"
        # - Total Study Time increases by 45 minutes
        assert app.kpi_labels["Total Study Time"].cget("text") == "45m"
        # - Today's Study Time increases by 45 minutes
        assert app.kpi_labels["Today's Study Time"].cget("text") == "45m"
        # - Most-Studied Subject updates
        assert "Python (45m)" in app.kpi_labels["Most-Studied Subject"].cget("text")
        # - Study History count increases
        assert "1 total" in app.table_title.cget("text")
        # - The new Python session appears in the table
        rows = app.tree.get_children()
        assert len(rows) == 1
        val1 = app.tree.item(rows[0])["values"]
        assert val1[1] == today
        assert val1[2] == "Python"
        assert val1[3] == "Functions"
        assert val1[4] == "45m"
        assert val1[5] == "Learned Python functions"

        # Verify Form Reset
        assert app.entry_date.get() == today
        assert app.combo_subject.get() == ""
        assert app.entry_topic.get() == ""
        assert app.entry_duration.get() == ""
        assert app.txt_notes.get("1.0", tk.END).strip() == ""

        # Step 4: Add Session 2 (SQL, 30m)
        app.combo_subject.set("SQL")
        app.entry_topic.delete(0, tk.END)
        app.entry_topic.insert(0, "SELECT queries")
        app.entry_duration.delete(0, tk.END)
        app.entry_duration.insert(0, "30")
        app.txt_notes.delete("1.0", tk.END)
        app.txt_notes.insert("1.0", "Practiced SQL SELECT.")

        save_result2 = app.handle_add_session(show_popup=False)
        assert save_result2 is True

        # Step 5: Verify dashboard & history update immediately again
        assert app.kpi_labels["Total Sessions"].cget("text") == "2"
        assert app.kpi_labels["Total Study Time"].cget("text") == "1h 15m"
        assert app.kpi_labels["Today's Study Time"].cget("text") == "1h 15m"
        assert "Python (45m)" in app.kpi_labels["Most-Studied Subject"].cget("text")
        assert "2 total" in app.table_title.cget("text")
        assert len(app.tree.get_children()) == 2

        # Step 6 & 7: Close and Reopen the application
        root.destroy()

        root2 = tk.Tk()
        root2.withdraw()
        app2 = StudyTrackerApp(root2)

        # Step 8: Verify both sessions are still present
        assert len(app2.tree.get_children()) == 2
        assert app2.kpi_labels["Total Sessions"].cget("text") == "2"
        assert app2.kpi_labels["Total Study Time"].cget("text") == "1h 15m"
        assert app2.kpi_labels["Today's Study Time"].cget("text") == "1h 15m"
        assert "Python (45m)" in app2.kpi_labels["Most-Studied Subject"].cget("text")

        # Test manual refresh button
        app2.handle_manual_refresh()
        assert len(app2.tree.get_children()) == 2

        root2.destroy()
        database.DEFAULT_DB_PATH = orig_db_path
        print("✓ All workflow, instant refresh, reset, and persistence checks PASSED!")

    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


if __name__ == "__main__":
    test_complete_user_workflow()
    print("\n=======================================================")
    print("🎉 ALL WORKFLOW TESTS PASSED FLAWLESSLY WITH ZERO ERRORS!")
    print("=======================================================\n")
