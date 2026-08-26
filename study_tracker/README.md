# 📚 Personal Study Tracker

A clean, modern, and beginner-friendly desktop application built with **Python**, **Tkinter**, and **SQLite**. Track your daily study sessions, monitor total hours learned, and stay consistent with your learning goals.

---

## ✨ Features

- **✍️ Log Study Sessions**:
  - Automatically pre-fills today's date (`YYYY-MM-DD`).
  - Select from common subjects or type any custom subject.
  - Record the topic/concept and study duration in minutes.
  - Quick-preset duration buttons (`25m`, `45m`, `60m`, `90m`).
  - Add notes or key takeaways.
- **📊 Real-time Dashboard Cards**:
  - **Total Sessions**: Total number of logged study sessions.
  - **Total Study Time**: Cumulative study time formatted in hours and minutes (e.g. `14h 30m`).
  - **Today's Study Time**: Track how much you've studied today.
  - **Most-Studied Subject**: Highlights the subject with the most study time.
- **📋 Interactive History Table**:
  - Clean table with alternating row colors.
  - Built-in live search/filter by subject, topic, or date.
  - Formatted time display (`45m`, `1h 30m`, etc.).
  - Vertical scrollbar support for extensive history.
- **🗑️ Session Management**:
  - Select any session in the table and delete it with a confirmation safety prompt.
  - Clear/reset the input form.
  - Refresh the table and statistics anytime.
- **💾 Local SQLite Database**:
  - All data is automatically saved locally to `study_tracker.db`.
  - Everything remains intact when closing and reopening the app.
- **⚡ Zero External Dependencies**:
  - Uses only Python's standard library (`tkinter`, `sqlite3`, `datetime`, `os`, `sys`). No `pip install` required!

---

## 📁 Project Structure

```text
study_tracker/
├── main.py            # Application entry point & window startup
├── database.py        # SQLite database operations (CRUD & statistics)
├── ui.py              # Tkinter GUI layout, styling, widgets & event handlers
├── README.md          # Project documentation & Python learning guide
└── study_tracker.db   # Local SQLite database file (created automatically)
```

---

## 🚀 How to Run the Application

### Prerequisites
Make sure **Python 3.8+** is installed on your computer.

### Step 1: Open Terminal or Command Prompt
Navigate to the project directory:
```bash
cd study_tracker
```

### Step 2: Run `main.py`
```bash
python main.py
```
*(Or run `python main.py` directly from the workspace root).*

---

## 🧠 Core Python Concepts in this Project

This project was specifically designed to demonstrate essential Python and software engineering concepts in a clean, readable way:

### 1. Modular Programming & Separation of Concerns
Instead of writing everything in a single massive file, the code is separated into dedicated modules:
- `database.py`: Handles all database operations (Storage layer).
- `ui.py`: Handles all visual elements and user interactions (Presentation layer).
- `main.py`: Glues everything together and starts the application (Application lifecycle).

### 2. Object-Oriented Programming (OOP)
- The `StudyTrackerApp` class in `ui.py` encapsulates all UI components, state variables (`tk.StringVar`), and event handlers as methods (`self.handle_add_session()`, `self.refresh_all()`).
- Using classes allows clean state management without messy global variables.

### 3. Tkinter GUI Programming & Event Loop
- **Widgets**: `tk.Label`, `tk.Frame`, `ttk.Entry`, `ttk.Combobox`, `ttk.Treeview`, and `tk.Button`.
- **Geometry Managers**: Combining `pack()` (for vertical/horizontal stacking) and `grid()` (for uniform dashboard KPI cards).
- **Reactive Variables**: Using `tk.StringVar` and `.trace_add()` for instant live search/filtering.
- **Event-Driven Architecture**: Buttons trigger callback functions via `command=...`.

### 4. Relational Databases & SQLite CRUD
- **`CREATE TABLE IF NOT EXISTS`**: Schema definition on startup.
- **`INSERT INTO`**: Parameterized queries using `?` placeholders to prevent SQL injection.
- **`SELECT ... ORDER BY ...`**: Fetching rows and ordering by recency.
- **`COUNT(*)` and `SUM(duration)`**: Aggregate SQL functions for instant dashboard statistics.
- **`DELETE FROM ... WHERE id = ?`**: Safe record removal.
- **Context Managers (`with conn:`)**: Automatically handles commits and transactions.

### 5. Input Validation & Exception Handling
- Validates that required fields are filled before saving.
- Validates that duration is a positive integer using `try...except ValueError`.
- Uses `tkinter.messagebox` (`showwarning`, `showerror`, `askyesno`) to give helpful user feedback.

---

## 💡 Ideas for Future Practice

Once you feel comfortable with this codebase, you can try adding these features to practice your skills:
1. **Export to CSV**: Add a button to export all study sessions to an Excel/CSV file using Python's `csv` module.
2. **Built-in Pomodoro Timer**: Add a tab with a countdown timer that logs a study session automatically when the timer finishes!
3. **Weekly & Monthly Goals**: Set a goal (e.g. 10 hours/week) and show a progress bar.
