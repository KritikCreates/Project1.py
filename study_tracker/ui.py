"""
ui.py - Graphical User Interface for the Personal Study Tracker.
Built with Python's standard tkinter and ttk libraries for a clean,
responsive, and modern desktop experience.
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date as dt_date

try:
    from . import database
except (ImportError, ValueError):
    import database


class StudyTrackerApp:
    """
    Main application class for the Personal Study Tracker GUI.
    Handles layout creation, user interaction, data validation, and event handling.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Personal Study Tracker")
        self.root.geometry("1100x720")
        self.root.minsize(920, 640)

        # Clean modern color palette
        self.bg_color = "#f1f5f9"        # Soft slate background
        self.card_bg = "#ffffff"         # Clean white card background
        self.primary_color = "#2563eb"    # Royal blue for primary actions
        self.danger_color = "#dc2626"     # Red for delete actions
        self.text_dark = "#0f172a"        # Dark slate text
        self.text_muted = "#64748b"       # Muted subtext
        
        self.root.configure(bg=self.bg_color)

        # Cache for search filtering
        self.all_sessions_cache = []

        # Default subjects list for combobox
        self.default_subjects = [
            "Python", "Data Structures", "Web Development",
            "Algorithms", "Mathematics", "Machine Learning",
            "SQL & Databases", "English", "Physics"
        ]

        # Tkinter Variables for form inputs
        self.var_date = tk.StringVar(value=dt_date.today().isoformat())
        self.var_subject = tk.StringVar()
        self.var_topic = tk.StringVar()
        self.var_duration = tk.StringVar()
        self.var_search = tk.StringVar()
        self.var_status = tk.StringVar(value="Ready to log your learning progress.")

        # Configure custom TTK styles
        self._setup_styles()

        # Build UI components
        self._create_header()
        self._create_dashboard()
        self._create_main_content()
        self._create_status_bar()

        # Load initial data from SQLite
        self.refresh_all()

    def _setup_styles(self):
        """Configures ttk widget styles for a modern and polished appearance."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure Treeview (Table)
        self.style.configure(
            "Treeview",
            background="#ffffff",
            foreground=self.text_dark,
            rowheight=28,
            fieldbackground="#ffffff",
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            background="#e2e8f0",
            foreground="#1e293b",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            relief="flat"
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#cbd5e1")]
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")]
        )

        # Configure Combobox and Entry widgets
        self.style.configure("TCombobox", padding=4, font=("Segoe UI", 10))
        self.style.configure("TEntry", padding=4, font=("Segoe UI", 10))

    def _create_header(self):
        """Creates the top header banner."""
        header_frame = tk.Frame(self.root, bg=self.bg_color, pady=8, padx=20)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="📚 Personal Study Tracker",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_dark
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Track daily study sessions, log topics & notes, and monitor your learning consistency.",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

    def _create_dashboard(self):
        """Creates the 4 KPI summary cards at the top."""
        dashboard_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=4)
        dashboard_frame.pack(fill="x")

        # 4 Card Configurations: (Title, Icon, Top Accent Color)
        card_configs = [
            ("Total Sessions", "📝", "#3b82f6"),
            ("Total Study Time", "⏱️", "#10b981"),
            ("Today's Study Time", "📅", "#8b5cf6"),
            ("Most-Studied Subject", "🎯", "#f59e0b")
        ]

        self.kpi_labels = {}

        for i in range(4):
            dashboard_frame.columnconfigure(i, weight=1, uniform="kpi")

        for idx, (title, icon, accent) in enumerate(card_configs):
            card = tk.Frame(
                dashboard_frame,
                bg=self.card_bg,
                bd=1,
                relief="solid",
                highlightthickness=1,
                highlightbackground="#e2e8f0",
                padx=12,
                pady=8
            )
            card.grid(row=0, column=idx, padx=5, pady=2, sticky="nsew")

            accent_bar = tk.Frame(card, bg=accent, height=3)
            accent_bar.pack(fill="x", side="top", pady=(0, 4))

            top_row = tk.Frame(card, bg=self.card_bg)
            top_row.pack(fill="x")

            t_lbl = tk.Label(
                top_row,
                text=f"{icon} {title}",
                font=("Segoe UI", 9, "bold"),
                bg=self.card_bg,
                fg=self.text_muted
            )
            t_lbl.pack(side="left")

            val_lbl = tk.Label(
                card,
                text="--",
                font=("Segoe UI", 15, "bold"),
                bg=self.card_bg,
                fg=self.text_dark
            )
            val_lbl.pack(anchor="w", pady=(2, 0))

            self.kpi_labels[title] = val_lbl

    def _create_main_content(self):
        """Creates the split view containing the input form and the session history table."""
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=8)
        main_container.pack(fill="both", expand=True)

        # Left Column: Add Study Session Form
        left_frame = tk.Frame(
            main_container,
            bg=self.card_bg,
            padx=16,
            pady=14,
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        # Right Column: Data Table & Actions
        right_frame = tk.Frame(
            main_container,
            bg=self.card_bg,
            padx=16,
            pady=14,
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        right_frame.pack(side="right", fill="both", expand=True)

        self._build_form(left_frame)
        self._build_table(right_frame)

    def _build_form(self, parent):
        """Builds the study session entry form on the left panel."""
        form_title = tk.Label(
            parent,
            text="✍️ Log Study Session",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_dark
        )
        form_title.pack(anchor="w", pady=(0, 8))

        # 1. Date Input
        tk.Label(parent, text="Date (YYYY-MM-DD)*", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_dark).pack(anchor="w")
        date_row = tk.Frame(parent, bg=self.card_bg)
        date_row.pack(fill="x", pady=(2, 8))

        self.entry_date = ttk.Entry(date_row, textvariable=self.var_date, font=("Segoe UI", 10), width=18)
        self.entry_date.pack(side="left", fill="x", expand=True)

        btn_today = tk.Button(
            date_row,
            text="Today",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg=self.text_dark,
            activebackground="#cbd5e1",
            relief="flat",
            cursor="hand2",
            padx=6,
            command=self._set_today_date
        )
        btn_today.pack(side="left", padx=(6, 0))

        # 2. Subject Input
        tk.Label(parent, text="Subject / Course*", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_dark).pack(anchor="w")
        self.combo_subject = ttk.Combobox(parent, textvariable=self.var_subject, values=self.default_subjects, font=("Segoe UI", 10))
        self.combo_subject.pack(fill="x", pady=(2, 8))

        # 3. Topic / Chapter Input
        tk.Label(parent, text="Topic / Concept*", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_dark).pack(anchor="w")
        self.entry_topic = ttk.Entry(parent, textvariable=self.var_topic, font=("Segoe UI", 10))
        self.entry_topic.pack(fill="x", pady=(2, 8))
        self.entry_topic.bind("<Return>", lambda e: self.handle_add_session())

        # 4. Duration Input (in minutes) + Quick preset chips
        tk.Label(parent, text="Duration (Minutes)*", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_dark).pack(anchor="w")
        self.entry_duration = ttk.Entry(parent, textvariable=self.var_duration, font=("Segoe UI", 10))
        self.entry_duration.pack(fill="x", pady=(2, 4))
        self.entry_duration.bind("<Return>", lambda e: self.handle_add_session())

        # Quick preset duration buttons (25m, 45m, 60m, 90m)
        presets_frame = tk.Frame(parent, bg=self.card_bg)
        presets_frame.pack(fill="x", pady=(0, 8))

        preset_mins = [("25m", 25), ("45m", 45), ("60m", 60), ("90m", 90)]
        for label, val in preset_mins:
            p_btn = tk.Button(
                presets_frame,
                text=label,
                font=("Segoe UI", 8),
                bg="#f1f5f9",
                fg=self.primary_color,
                activebackground="#dbeafe",
                relief="flat",
                cursor="hand2",
                padx=6,
                pady=1,
                command=lambda m=val: self._set_duration_preset(m)
            )
            p_btn.pack(side="left", padx=(0, 4))

        # 5. Short Notes
        tk.Label(parent, text="Notes / Key Takeaways", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_dark).pack(anchor="w")
        self.txt_notes = tk.Text(parent, height=3, font=("Segoe UI", 9), relief="solid", bd=1, highlightthickness=1, wrap="word")
        self.txt_notes.config(highlightbackground="#cbd5e1")
        self.txt_notes.pack(fill="x", pady=(2, 12))

        # Action Buttons: Prominent Save Study Session & Clear Form
        btn_save = tk.Button(
            parent,
            text="➕  Save Study Session",
            font=("Segoe UI", 10, "bold"),
            bg=self.primary_color,
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self.handle_add_session
        )
        btn_save.pack(fill="x", pady=(0, 6))

        btn_clear = tk.Button(
            parent,
            text="🔄  Clear Form",
            font=("Segoe UI", 9),
            bg="#f1f5f9",
            fg=self.text_dark,
            activebackground="#e2e8f0",
            relief="flat",
            cursor="hand2",
            pady=5,
            command=self.handle_clear_form
        )
        btn_clear.pack(fill="x")

    def _build_table(self, parent):
        """Builds the session history table and action controls on the right panel."""
        # Top Header row with title & search bar
        table_top = tk.Frame(parent, bg=self.card_bg)
        table_top.pack(fill="x", pady=(0, 8))

        self.table_title = tk.Label(
            table_top,
            text="📋 Study History",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_dark
        )
        self.table_title.pack(side="left")

        # Quick Live Search Box
        search_frame = tk.Frame(table_top, bg=self.card_bg)
        search_frame.pack(side="right")

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 10), bg=self.card_bg, fg=self.text_muted).pack(side="left", padx=(0, 4))
        self.entry_search = ttk.Entry(search_frame, textvariable=self.var_search, font=("Segoe UI", 9), width=20)
        self.entry_search.pack(side="left")
        self.var_search.trace_add("write", lambda *args: self.filter_table())

        # Table Container with Treeview and Scrollbars
        tree_container = tk.Frame(parent, bg=self.card_bg)
        tree_container.pack(fill="both", expand=True)

        columns = ("id", "date", "subject", "topic", "duration", "notes")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Define Columns
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("topic", text="Topic")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("notes", text="Notes")

        self.tree.column("id", width=45, minwidth=35, anchor="center")
        self.tree.column("date", width=95, minwidth=85, anchor="center")
        self.tree.column("subject", width=125, minwidth=100, anchor="w")
        self.tree.column("topic", width=165, minwidth=120, anchor="w")
        self.tree.column("duration", width=85, minwidth=75, anchor="center")
        self.tree.column("notes", width=220, minwidth=140, anchor="w")

        # Alternating row tag colors
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("evenrow", background="#f8fafc")

        # Vertical & Horizontal Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        # Double click on row to view full details
        self.tree.bind("<Double-1>", self._on_row_double_click)

        # Bottom Action Bar
        action_bar = tk.Frame(parent, bg=self.card_bg, pady=6)
        action_bar.pack(fill="x")

        btn_delete = tk.Button(
            action_bar,
            text="🗑️ Delete Selected Session",
            font=("Segoe UI", 9, "bold"),
            bg="#fee2e2",
            fg=self.danger_color,
            activebackground="#fecaca",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.handle_delete_session
        )
        btn_delete.pack(side="left")

        btn_refresh = tk.Button(
            action_bar,
            text="🔄 Refresh List",
            font=("Segoe UI", 9),
            bg="#f1f5f9",
            fg=self.text_dark,
            activebackground="#e2e8f0",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.handle_manual_refresh
        )
        btn_refresh.pack(side="left", padx=(8, 0))

    def _create_status_bar(self):
        """Creates the bottom status bar for user feedback."""
        status_frame = tk.Frame(self.root, bg="#e2e8f0", padx=16, pady=4)
        status_frame.pack(side="bottom", fill="x")

        status_lbl = tk.Label(
            status_frame,
            textvariable=self.var_status,
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg=self.text_muted
        )
        status_lbl.pack(side="left")

    def _set_today_date(self):
        """Sets the date input field to today's date."""
        today_iso = dt_date.today().isoformat()
        self.var_date.set(today_iso)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, today_iso)

    def _set_duration_preset(self, minutes):
        """Sets the duration from preset button click."""
        self.var_duration.set(str(minutes))
        self.entry_duration.delete(0, tk.END)
        self.entry_duration.insert(0, str(minutes))
        self.txt_notes.focus_set()

    def set_status(self, message):
        """Updates the status bar message."""
        self.var_status.set(message)

    def _on_row_double_click(self, event):
        """Displays full details of the double-clicked study session."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item_data = self.tree.item(selected_item[0])["values"]
        if not item_data:
            return

        session_id, s_date, subject, topic, duration, notes = item_data
        details_msg = (
            f"📅 Date: {s_date}\n"
            f"📚 Subject: {subject}\n"
            f"🎯 Topic: {topic}\n"
            f"⏱️ Duration: {duration}\n\n"
            f"📝 Notes:\n{notes if notes else '(No notes provided)'}"
        )
        messagebox.showinfo(f"Study Session #{session_id} Details", details_msg)

    # ------------------ EVENT HANDLERS & LOGIC ------------------

    def handle_add_session(self, show_popup=True):
        """
        Validates form inputs, inserts the session into SQLite, commits,
        automatically refreshes dashboard & table, resets the form,
        and provides instant success confirmation.
        """
        date_raw = self.entry_date.get().strip() or self.var_date.get().strip()
        subject_val = self.combo_subject.get().strip() or self.var_subject.get().strip()
        topic_val = self.entry_topic.get().strip() or self.var_topic.get().strip()
        duration_raw = self.entry_duration.get().strip() or self.var_duration.get().strip()
        notes_val = self.txt_notes.get("1.0", tk.END).strip()

        # 1. Validation: Required Fields
        if not date_raw or not subject_val or not topic_val or not duration_raw:
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all required fields:\n• Date\n• Subject\n• Topic\n• Duration"
            )
            return False

        # 2. Validation: Date normalization & validity
        try:
            date_val = database.normalize_date_string(date_raw)
        except ValueError as ve:
            messagebox.showerror(
                "Invalid Date",
                f"{ve}\n\nExample of valid date: {dt_date.today().isoformat()}"
            )
            self.entry_date.focus_set()
            return False

        # 3. Validation: Duration integer parsing
        clean_dur = re.sub(r'(?i)\s*(mins?|m|minutes?)$', '', duration_raw).strip()
        try:
            duration_int = int(clean_dur)
            if duration_int <= 0:
                raise ValueError("Duration must be greater than zero.")
            if duration_int > 1440:  # 24 hours max per single session
                raise ValueError("Duration cannot exceed 1440 minutes (24 hours).")
        except ValueError:
            messagebox.showerror(
                "Invalid Duration",
                "Study duration must be a positive whole number of minutes (between 1 and 1440).\n\nExamples: 25, 45, 60, 90"
            )
            self.entry_duration.focus_set()
            return False

        # 4. Save to SQLite Database & Commit
        try:
            new_id = database.add_session(
                date=date_val,
                subject=subject_val,
                topic=topic_val,
                duration=duration_int,
                notes=notes_val
            )

            # Update combobox dropdown values if this is a custom subject
            current_subjects = list(self.combo_subject["values"])
            if subject_val not in current_subjects:
                current_subjects.append(subject_val)
                self.combo_subject["values"] = current_subjects

            # Clear search filter to ensure newly added item is immediately visible
            self.var_search.set("")

            # 5. Form Reset: Reset form fields back to defaults
            self.handle_clear_form(preserve_date=False)

            # 6. Automatic Refresh: Immediately refresh dashboard stats and history table
            self.refresh_all()

            # 7. Status and confirmation message
            success_msg = f"Study session #{new_id} ({subject_val} - {duration_int}m) saved successfully!"
            self.set_status(f"✅ {success_msg}")
            if show_popup:
                messagebox.showinfo("Success", "Study session saved successfully!")
            return True

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save study session:\n{e}")
            return False

    def handle_delete_session(self):
        """Deletes the selected session from the table and SQLite database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "Please click on a study session in the table to select it for deletion.")
            return

        item_data = self.tree.item(selected_item[0])["values"]
        session_id = item_data[0]
        subject_name = item_data[2]
        topic_name = item_data[3]

        # Confirm deletion with the user
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete session #{session_id}?\n\n• Subject: {subject_name}\n• Topic: {topic_name}",
            icon="warning"
        )
        if confirm:
            try:
                success = database.delete_session(session_id)
                if success:
                    self.set_status(f"🗑️ Deleted study session #{session_id}.")
                    self.refresh_all()
                else:
                    messagebox.showerror("Error", f"Could not find session #{session_id} in the database.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete session:\n{e}")

    def handle_clear_form(self, preserve_date=False):
        """Resets all input fields in the form without touching database records."""
        self._set_today_date()
        self.var_subject.set("")
        self.combo_subject.set("")
        self.var_topic.set("")
        self.entry_topic.delete(0, tk.END)
        self.var_duration.set("")
        self.entry_duration.delete(0, tk.END)
        self.txt_notes.delete("1.0", tk.END)
        self.combo_subject.focus_set()
        if not preserve_date:
            self.set_status("Form reset.")

    def handle_manual_refresh(self):
        """Explicit manual refresh button handler."""
        self.refresh_all()
        self.set_status("🔄 List and dashboard refreshed from database.")

    def refresh_all(self):
        """Reloads fresh data from SQLite and updates both dashboard KPIs and history table."""
        self.update_dashboard()
        self.populate_table()

    def update_dashboard(self):
        """Calculates and refreshes the 4 KPI cards."""
        try:
            stats = database.get_summary_stats()
            self.kpi_labels["Total Sessions"].config(text=f"{stats['total_sessions']}")
            self.kpi_labels["Total Study Time"].config(text=stats["total_time_formatted"])
            self.kpi_labels["Today's Study Time"].config(text=stats["today_time_formatted"])
            self.kpi_labels["Most-Studied Subject"].config(text=stats["top_subject"])
        except Exception as e:
            self.set_status(f"⚠️ Error updating dashboard: {e}")

    def populate_table(self):
        """Loads all sessions from SQLite into the Treeview widget."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            sessions = database.get_all_sessions()
            self.all_sessions_cache = sessions  # Store in memory for filtering

            # Update table title with count
            self.table_title.config(text=f"📋 Study History ({len(sessions)} total)")

            for index, row in enumerate(sessions):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                formatted_time = database.format_duration(row["duration"])
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["date"],
                        row["subject"],
                        row["topic"],
                        formatted_time,
                        row["notes"] or ""
                    ),
                    tags=(tag,)
                )
        except Exception as e:
            self.set_status(f"⚠️ Error loading sessions: {e}")

    def filter_table(self):
        """Filters table records based on search query in Subject, Topic, Notes, or Date."""
        query = self.var_search.get().lower().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_count = 0
        for index, row in enumerate(self.all_sessions_cache):
            text_pool = f"{row['subject']} {row['topic']} {row['notes'] or ''} {row['date']}".lower()
            if not query or query in text_pool:
                tag = "evenrow" if filtered_count % 2 == 0 else "oddrow"
                formatted_time = database.format_duration(row["duration"])
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["date"],
                        row["subject"],
                        row["topic"],
                        formatted_time,
                        row["notes"] or ""
                    ),
                    tags=(tag,)
                )
                filtered_count += 1

        if query:
            self.table_title.config(text=f"📋 Study History ({filtered_count} matching)")
        else:
            self.table_title.config(text=f"📋 Study History ({len(self.all_sessions_cache)} total)")
