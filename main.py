"""
Top-level entry point for running the Personal Study Tracker.
"""

import sys
import os

# Add study_tracker folder to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDY_TRACKER_DIR = os.path.join(BASE_DIR, "study_tracker")
if STUDY_TRACKER_DIR not in sys.path:
    sys.path.insert(0, STUDY_TRACKER_DIR)

from study_tracker.main import main

if __name__ == "__main__":
    main()
