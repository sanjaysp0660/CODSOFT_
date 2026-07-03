import json
import os
import tkinter as tk
from dataclasses import asdict, dataclass
from tkinter import messagebox, simpledialog, ttk, filedialog
from datetime import datetime, timedelta
import csv

DATA_FILE = "todo_tasks.json"

PRIORITY_ICONS = {
    "Urgent": "🔴",
    "High": "🟠",
    "Normal": "🟡",
    "Low": "🟢"
}

COLOR_SCHEME = {
    "bg_main": "#0f1419",
    "bg_secondary": "#1a1f2e",
    "bg_tertiary": "#252d3d",
    "accent_primary": "#00d4ff",
    "accent_secondary": "#7c3aed",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
}


@dataclass
class TodoItem:
    text: str
    completed: bool = False
    priority: str = "Normal"
    category: str = "General"
    due_date: str = ""
    difficulty: str = "Medium"
    notes: str = ""
    created_at: str = ""
    """A lightweight data container for a single todo item.

    Attributes:
        text: The task description.
        completed: Whether the task is completed.
        priority: Priority label (Urgent, High, Normal, Low).
        category: Optional category name.
        due_date: Due date string in YYYY-MM-DD format (optional).
        difficulty: Human-friendly difficulty label.
        notes: Longer free-form notes attached to the task.
        created_at: Timestamp when the task was created.
    """

    def display_text(self) -> str:
        """Return a short, readable representation for list display.

        The returned string includes a priority icon and due date when present.
        """
        icon = PRIORITY_ICONS.get(self.priority, "")
        status = "✓" if self.completed else " "
        due_display = f" 📅 {self.due_date}" if self.due_date else ""
        return f"[{status}] {icon} {self.text}{due_display}"


class TodoApp:
    """Main application class that builds UI and manages task state.

    All UI callbacks are methods on this class so state is kept in `self.tasks`.
    """

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("✨ Sanjay Task Manager")
        self.master.geometry("720x800")
        self.master.resizable(False, False)
        self.master.configure(bg=COLOR_SCHEME["bg_main"])

        self.tasks: list[TodoItem] = []
        self.filtered_tasks: list[int] = []
        self.current_filter = "all"

        self.build_ui()
        self.refresh_task_list()
        self.update_summary()

        self.master.bind("<Control-n>", lambda e: self.focus_task_entry())
        self.master.bind("<Control-s>", lambda e: self.save_tasks())

    def build_ui(self) -> None:
        main_container = tk.Frame(self.master, bg=COLOR_SCHEME["bg_main"])
        main_container.pack(fill="both", expand=True)

        self.build_header(main_container)
        self.build_stats_panel(main_container)
        self.build_input_area(main_container)
        self.build_filter_area(main_container)
        self.build_list_area(main_container)
        self.build_action_area(main_container)

    def build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=COLOR_SCHEME["bg_secondary"], height=80)
        header.pack(fill="x", padx=0, pady=0)

        title = tk.Label(
            header,
            text="✨ Sanjay Task Manager",
            font=("Segoe UI", 26, "bold"),
            fg=COLOR_SCHEME["accent_primary"],
            bg=COLOR_SCHEME["bg_secondary"],
        )
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            header,
            text="Organize, prioritize, and conquer your tasks efficiently",
            font=("Segoe UI", 10),
            fg=COLOR_SCHEME["text_secondary"],
            bg=COLOR_SCHEME["bg_secondary"],
        )
        subtitle.pack(pady=(0, 12))

    def build_stats_panel(self, parent: tk.Frame) -> None:
        stats_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_secondary"])
        stats_frame.pack(fill="x", padx=12, pady=8)

        self.urgent_label = self._create_stat_card(stats_frame, "🔴 Urgent", "0", COLOR_SCHEME["danger"])
        self.high_label = self._create_stat_card(stats_frame, "🟠 High", "0", COLOR_SCHEME["warning"])
        self.completed_label = self._create_stat_card(stats_frame, "✓ Done", "0", COLOR_SCHEME["success"])
        self.total_label = self._create_stat_card(stats_frame, "📋 Total", "0", COLOR_SCHEME["accent_primary"])

    def _create_stat_card(self, parent: tk.Frame, label: str, value: str, color: str) -> tk.Label:
        card = tk.Frame(parent, bg=COLOR_SCHEME["bg_tertiary"], relief="flat")
        card.pack(side="left", padx=4, pady=0, fill="both", expand=True)

        lbl = tk.Label(
            card,
            text=f"{label}\n{value}",
            font=("Segoe UI", 10, "bold"),
            fg=color,
            bg=COLOR_SCHEME["bg_tertiary"],
        )
        lbl.pack(pady=8)
        return lbl

    def build_input_area(self, parent: tk.Frame) -> None:
        input_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_main"])
        input_frame.pack(padx=12, pady=10, fill="x")

        self.task_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg=COLOR_SCHEME["bg_tertiary"],
            fg=COLOR_SCHEME["text_primary"],
            relief="flat",
            insertbackground=COLOR_SCHEME["accent_primary"],
        )
        self.task_entry.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=12, padx=(0, 8))
        self.task_entry.insert(0, "Add a new task...")
        self.task_entry.bind("<FocusIn>", self.clear_placeholder)
        self.task_entry.bind("<FocusOut>", self.restore_placeholder)

        self.priority_box = tk.StringVar(value="Normal")
        priority_menu = tk.OptionMenu(
            input_frame,
            self.priority_box,
            "Low",
            "Normal",
            "High",
            "Urgent",
        )
        priority_menu.config(
            font=("Segoe UI", 10),
            bg=COLOR_SCHEME["bg_tertiary"],
            fg=COLOR_SCHEME["accent_primary"],
            relief="flat",
            activebackground=COLOR_SCHEME["accent_secondary"],
        )
        priority_menu.grid(row=0, column=2, sticky="ew", padx=(0, 8))

        self.difficulty_box = tk.StringVar(value="Medium")
        difficulty_menu = tk.OptionMenu(
            input_frame,
            self.difficulty_box,
            "Easy",
            "Medium",
            "Hard",
        )
        difficulty_menu.config(
            font=("Segoe UI", 10),
            bg=COLOR_SCHEME["bg_tertiary"],
            fg=COLOR_SCHEME["accent_primary"],
            relief="flat",
            activebackground=COLOR_SCHEME["accent_secondary"],
        )
        difficulty_menu.grid(row=0, column=3, sticky="ew", padx=(0, 8))

        add_button = tk.Button(
            input_frame,
            text="Add ✨",
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff",
            bg=COLOR_SCHEME["accent_secondary"],
            activebackground=COLOR_SCHEME["accent_primary"],
            relief="flat",
            command=self.add_task,
        )
        add_button.grid(row=0, column=4, sticky="ew")

        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(4, weight=0)

    def build_filter_area(self, parent: tk.Frame) -> None:
        filter_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_main"])
        filter_frame.pack(padx=12, pady=(0, 10), fill="x")

        self.search_entry = tk.Entry(
            filter_frame,
            font=("Segoe UI", 11),
            bg=COLOR_SCHEME["bg_tertiary"],
            fg=COLOR_SCHEME["text_primary"],
            relief="flat",
            insertbackground=COLOR_SCHEME["accent_primary"],
        )
        self.search_entry.pack(fill="x", ipady=10, padx=(0, 8), side="left", expand=True)
        self.search_entry.insert(0, "🔍 Search tasks...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        theme_button = tk.Button(
            filter_frame,
            text="🌙",
            font=("Segoe UI", 11),
            fg=COLOR_SCHEME["accent_primary"],
            bg=COLOR_SCHEME["bg_tertiary"],
            relief="flat",
            command=self.toggle_theme,
            width=3,
        )
        theme_button.pack(side="left", padx=4)

    def build_list_area(self, parent: tk.Frame) -> None:
        list_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_main"])
        list_frame.pack(padx=12, fill="both", expand=True, pady=(0, 10))

        self.task_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            bg=COLOR_SCHEME["bg_tertiary"],
            fg=COLOR_SCHEME["text_primary"],
            selectbackground=COLOR_SCHEME["accent_secondary"],
            selectforeground="#ffffff",
            activestyle="none",
            highlightthickness=0,
            bd=0,
            height=14,
        )
        self.task_listbox.pack(side="left", fill="both", expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", lambda _: None)

        scrollbar = tk.Scrollbar(list_frame, command=self.task_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_listbox.config(yscrollcommand=scrollbar.set)

    def build_action_area(self, parent: tk.Frame) -> None:
        action_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_main"])
        action_frame.pack(fill="x", padx=12, pady=10)
        
        credit_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_secondary"])
        credit_frame.pack(fill="x", padx=0, pady=(10, 0), side="bottom")
        
        credit_label = tk.Label(
            credit_frame,
            text="💜 Created by SANJAY SP",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_SCHEME["accent_secondary"],
            bg=COLOR_SCHEME["bg_secondary"],
        )
        credit_label.pack(pady=8)

        actions = [
            ("✓ Complete", self.mark_completed, COLOR_SCHEME["success"]),
            ("✏️ Edit", self.edit_task, COLOR_SCHEME["accent_primary"]),
            ("📝 Notes", self.add_notes, COLOR_SCHEME["accent_secondary"]),
            ("📅 Due Date", self.set_due_date, COLOR_SCHEME["warning"]),
            ("📋 Details", self.view_details, COLOR_SCHEME["bg_tertiary"]),
            ("⎘ Duplicate", self.duplicate_task, COLOR_SCHEME["bg_tertiary"]),
            ("↑ Move Up", self.move_up, COLOR_SCHEME["bg_tertiary"]),
            ("↓ Move Down", self.move_down, COLOR_SCHEME["bg_tertiary"]),
        ]

        for idx, (label, command, color) in enumerate(actions):
            button = tk.Button(
                action_frame,
                text=label,
                font=("Segoe UI", 9, "bold"),
                fg="#ffffff",
                bg=color,
                activebackground=COLOR_SCHEME["accent_primary"],
                relief="flat",
                command=command,
            )
            button.grid(row=0, column=idx, padx=3, ipadx=8, ipady=10, sticky="ew")
            action_frame.columnconfigure(idx, weight=1)

        bottom_frame = tk.Frame(parent, bg=COLOR_SCHEME["bg_main"])
        bottom_frame.pack(fill="x", padx=12, pady=(0, 10))

        controls = [
            ("🗑️ Delete", self.delete_task, COLOR_SCHEME["danger"]),
            ("🧹 Clear Done", self.clear_completed, COLOR_SCHEME["warning"]),
            ("💾 Save", self.save_tasks, COLOR_SCHEME["success"]),
            ("🔄 Reload", self.load_tasks, COLOR_SCHEME["accent_primary"]),
            ("⬇ Export CSV", self.export_csv, COLOR_SCHEME["bg_tertiary"]),
            ("⬆ Import CSV", self.import_csv, COLOR_SCHEME["bg_tertiary"]),
            ("🔀 Sort", self.sort_by_priority, COLOR_SCHEME["bg_tertiary"]),
        ]

        for idx, (label, command, color) in enumerate(controls):
            button = tk.Button(
                bottom_frame,
                text=label,
                font=("Segoe UI", 9),
                fg="#ffffff",
                bg=color,
                relief="flat",
                command=command,
            )
            button.grid(row=0, column=idx, padx=3, ipadx=8, ipady=8, sticky="ew")
            bottom_frame.columnconfigure(idx, weight=1)

    def clear_placeholder(self, event: tk.Event) -> None:
        """Remove the input placeholder when user focuses the task entry."""
        if self.task_entry.get() == "Add a new task...":
            self.task_entry.delete(0, tk.END)

    def restore_placeholder(self, event: tk.Event) -> None:
        """Restore the placeholder text if the entry is empty on focus out."""
        if not self.task_entry.get().strip():
            self.task_entry.insert(0, "Add a new task...")

    def clear_search_placeholder(self, event: tk.Event) -> None:
        """Clear the search placeholder when the search field receives focus."""
        if self.search_entry.get() == "🔍 Search tasks...":
            self.search_entry.delete(0, tk.END)

    def restore_search_placeholder(self, event: tk.Event) -> None:
        """Restore the search placeholder when the search box is empty."""
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "🔍 Search tasks...")

    def focus_task_entry(self) -> None:
        """Give keyboard focus to the task input (used by Ctrl+N)."""
        self.task_entry.focus()

    def update_summary(self) -> None:
        """Refresh the statistics cards (urgent/high/completed/total)."""
        total = len(self.tasks)
        completed = sum(task.completed for task in self.tasks)
        urgent = sum(1 for task in self.tasks if task.priority == "Urgent" and not task.completed)
        high = sum(1 for task in self.tasks if task.priority == "High" and not task.completed)

        self.urgent_label.config(text=f"🔴 Urgent\n{urgent}")
        self.high_label.config(text=f"🟠 High\n{high}")
        self.completed_label.config(text=f"✓ Done\n{completed}")
        self.total_label.config(text=f"📋 Total\n{total}")

    def add_task(self) -> None:
        """Create a new TodoItem from the input fields and add to task list.

        This method validates the input, records a creation timestamp, and
        resets the input widgets to their defaults.
        """
        raw_text = self.task_entry.get().strip()
        if not raw_text or raw_text == "Add a new task...":
            messagebox.showwarning("Oops!", "Please type a task first.")
            return

        self.tasks.append(TodoItem(
            text=raw_text,
            priority=self.priority_box.get(),
            difficulty=self.difficulty_box.get(),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        # clear inputs and refresh UI
        self.task_entry.delete(0, tk.END)
        self.priority_box.set("Normal")
        self.difficulty_box.set("Medium")
        self.apply_filter()
        self.update_summary()

    def get_selected_index(self) -> int | None:
        """Return the index (in `self.tasks`) of the selected visible item.

        If there is an active filter the listbox index must be mapped back to
        the global `tasks` list via `self.filtered_tasks`.
        """
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Task", "👉 Please select a task first!")
            return None

        list_index = selection[0]
        if self.filtered_tasks:
            return self.filtered_tasks[list_index]
        return list_index

    def edit_task(self) -> None:
        """Prompt the user to edit the selected task's text."""
        index = self.get_selected_index()
        if index is None:
            return

        task = self.tasks[index]
        updated_text = simpledialog.askstring("Edit Task", "Update the task:", initialvalue=task.text)
        if updated_text is None:
            return

        updated_text = updated_text.strip()
        if not updated_text:
            messagebox.showwarning("Invalid", "Task cannot be empty!")
            return

        task.text = updated_text
        self.apply_filter()
        self.update_summary()

    def add_notes(self) -> None:
        """Open a small dialog to add or edit notes for the selected task."""
        index = self.get_selected_index()
        if index is None:
            return

        task = self.tasks[index]
        note = simpledialog.askstring("Add Notes", "Add or edit notes:", initialvalue=task.notes)
        if note is not None:
            task.notes = note
            messagebox.showinfo("Success", "📝 Notes saved!")

    def set_due_date(self) -> None:
        """Prompt for a due-date string (YYYY-MM-DD) and attach to task."""
        index = self.get_selected_index()
        if index is None:
            return

        task = self.tasks[index]
        due_date = simpledialog.askstring(
            "Set Due Date",
            "Enter due date (YYYY-MM-DD):\nLeave blank to remove",
            initialvalue=task.due_date
        )
        if due_date is not None:
            task.due_date = due_date if due_date.strip() else ""
            self.apply_filter()
            messagebox.showinfo("Success", "📅 Due date updated!")

    def delete_task(self) -> None:
        """Delete the selected task after a confirmation dialog."""
        index = self.get_selected_index()
        if index is None:
            return

        if messagebox.askyesno("Confirm", "🗑️ Delete this task?"):
            del self.tasks[index]
            self.apply_filter()
            self.update_summary()

    def mark_completed(self) -> None:
        """Toggle the completed state of the selected task."""
        index = self.get_selected_index()
        if index is None:
            return

        self.tasks[index].completed = not self.tasks[index].completed
        self.apply_filter()
        self.update_summary()

    def clear_completed(self) -> None:
        """Remove all tasks that are currently marked as completed."""
        if messagebox.askyesno("Confirm", "🧹 Clear all completed tasks?"):
            self.tasks = [task for task in self.tasks if not task.completed]
            self.apply_filter()
            self.update_summary()

    def apply_filter(self) -> None:
        """Apply the search query to tasks and prepare the visible index map.

        The search matches against task text, category and priority labels.
        """
        query = self.search_entry.get().strip().lower()
        placeholder = "🔍 Search tasks..."
        if query and query != placeholder.lower():
            self.filtered_tasks = [
                i for i, task in enumerate(self.tasks)
                if query in task.text.lower() or query in task.category.lower() or query in task.priority.lower()
            ]
        else:
            self.filtered_tasks = []
        self.refresh_task_list()

    def refresh_task_list(self) -> None:
        """Rebuild the listbox contents based on the current filter map."""
        self.task_listbox.delete(0, tk.END)
        current_indices = self.filtered_tasks if self.filtered_tasks else list(range(len(self.tasks)))

        for index in current_indices:
            self.task_listbox.insert(tk.END, self.tasks[index].display_text())

        self.task_listbox.yview_moveto(0)
        self.task_listbox.selection_clear(0, tk.END)

    def view_details(self) -> None:
        index = self.get_selected_index()
        if index is None:
            return
        task = self.tasks[index]
        details = (
            f"Task: {task.text}\n"
            f"Priority: {task.priority}\n"
            f"Difficulty: {task.difficulty}\n"
            f"Category: {task.category}\n"
            f"Due: {task.due_date or '—'}\n"
            f"Created: {task.created_at or '—'}\n"
            f"Completed: {'Yes' if task.completed else 'No'}\n\n"
            f"Notes:\n{task.notes or 'None'}"
        )
        # use a simple scrolling window for details
        detail_win = tk.Toplevel(self.master)
        detail_win.title("Task Details")
        detail_win.configure(bg=COLOR_SCHEME["bg_secondary"]) 
        txt = tk.Text(detail_win, wrap="word", bg=COLOR_SCHEME["bg_tertiary"], fg=COLOR_SCHEME["text_primary"], width=60, height=15)
        txt.insert("1.0", details)
        txt.config(state="disabled")
        txt.pack(padx=12, pady=12)

    def duplicate_task(self) -> None:
        index = self.get_selected_index()
        if index is None:
            return
        original = self.tasks[index]
        copy = TodoItem(
            text=original.text + " (copy)",
            completed=False,
            priority=original.priority,
            category=original.category,
            due_date=original.due_date,
            difficulty=original.difficulty,
            notes=original.notes,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self.tasks.insert(index + 1, copy)
        self.apply_filter()
        self.update_summary()

    def move_up(self) -> None:
        index = self.get_selected_index()
        if index is None or index == 0:
            return
        self.tasks[index - 1], self.tasks[index] = self.tasks[index], self.tasks[index - 1]
        self.apply_filter()

    def move_down(self) -> None:
        index = self.get_selected_index()
        if index is None or index >= len(self.tasks) - 1:
            return
        self.tasks[index + 1], self.tasks[index] = self.tasks[index], self.tasks[index + 1]
        self.apply_filter()

    def export_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="todo_tasks.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["text", "completed", "priority", "category", "due_date", "difficulty", "notes", "created_at"])
                for t in self.tasks:
                    writer.writerow([t.text, t.completed, t.priority, t.category, t.due_date, t.difficulty, t.notes, t.created_at])
            messagebox.showinfo("Exported", f"Tasks exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def import_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.tasks.append(TodoItem(
                        text=row.get("text", ""),
                        completed=row.get("completed", "False") in ("True", "true", "1"),
                        priority=row.get("priority", "Normal"),
                        category=row.get("category", "General"),
                        due_date=row.get("due_date", ""),
                        difficulty=row.get("difficulty", "Medium"),
                        notes=row.get("notes", ""),
                        created_at=row.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
                    ))
            self.apply_filter()
            self.update_summary()
            messagebox.showinfo("Imported", f"Tasks imported from {path}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def sort_by_priority(self) -> None:
        priority_order = {"Urgent": 0, "High": 1, "Normal": 2, "Low": 3}
        def keyfn(t: TodoItem):
            due = t.due_date or "9999-12-31"
            return (t.completed, priority_order.get(t.priority, 2), due, t.text.lower())
        self.tasks.sort(key=keyfn)
        self.apply_filter()

    def save_tasks(self) -> None:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump([asdict(task) for task in self.tasks], file, indent=2)
            messagebox.showinfo("Success", "💾 Tasks saved successfully!")
        except Exception as error:
            messagebox.showerror("Error", f"Failed to save:\n{error}")

    def load_tasks(self) -> None:
        if not os.path.exists(DATA_FILE):
            self.refresh_task_list()
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                raw_tasks = json.load(file)
            self.tasks = [TodoItem(**item) for item in raw_tasks]
            self.apply_filter()
            self.update_summary()
            messagebox.showinfo("Success", "🔄 Tasks reloaded!")
        except Exception as error:
            messagebox.showerror("Error", f"Failed to load:\n{error}")

    def toggle_theme(self) -> None:
        # implement simple dark/light toggle
        if getattr(self, "light_theme", False):
            self.apply_dark_theme()
            self.light_theme = False
        else:
            self.apply_light_theme()
            self.light_theme = True

    def apply_light_theme(self) -> None:
        # light color overrides
        self.master.configure(bg="#f6f7fb")
        for w in self.master.winfo_children():
            self._apply_theme_to_widget(w, light=True)

    def apply_dark_theme(self) -> None:
        self.master.configure(bg=COLOR_SCHEME["bg_main"])
        for w in self.master.winfo_children():
            self._apply_theme_to_widget(w, light=False)

    def _apply_theme_to_widget(self, widget: tk.Widget, light: bool) -> None:
        try:
            if isinstance(widget, tk.Label):
                widget.config(bg=("#f6f7fb" if light else COLOR_SCHEME["bg_secondary"]), fg=("#0f1724" if light else COLOR_SCHEME["text_primary"]))
            elif isinstance(widget, tk.Frame):
                widget.config(bg=("#f6f7fb" if light else COLOR_SCHEME["bg_main"]))
            elif isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
                widget.config(bg=("#ffffff" if light else COLOR_SCHEME["bg_tertiary"]), fg=("#0f1724" if light else COLOR_SCHEME["text_primary"]))
            elif isinstance(widget, tk.Listbox):
                widget.config(bg=("#ffffff" if light else COLOR_SCHEME["bg_tertiary"]), fg=("#0f1724" if light else COLOR_SCHEME["text_primary"]))
            elif isinstance(widget, tk.Button):
                # keep button colors as-is but adjust bg for light theme
                if light:
                    widget.config(bg="#3b82f6")
                else:
                    widget.config(bg=widget.cget("bg"))
        except Exception:
            pass
        for child in widget.winfo_children():
            self._apply_theme_to_widget(child, light)


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
