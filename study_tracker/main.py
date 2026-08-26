"""
main.py - Entry point for the Personal Study Tracker application.
Initializes the database, creates the Tkinter root window, and launches the UI.
"""

import sys
import os
import tkinter as tk

# Ensure current directory is on python path for direct execution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from .database import init_db
    from .ui import StudyTrackerApp
except (ImportError, ValueError):
    from database import init_db
    from ui import StudyTrackerApp


def main():
    """Main function to launch the application."""
    # 1. Initialize the SQLite database
    init_db()

    # 2. Create the Tkinter root window
    root = tk.Tk()
    
    # 3. Configure window icon (optional fallback for standard platforms)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    # 4. Instantiate the Study Tracker Application
    app = StudyTrackerApp(root)

    # 5. Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
