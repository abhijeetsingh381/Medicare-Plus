"""
Anti-Clipping Appointments Scheduler View for Medicare Plus Hospital Management System.
Features proportional stretch columns and clean compact action controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database
from styles import Theme
from ui_components import CardFrame, SearchBar, ModernButton


class AppointmentsView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=16, pady=12, **kwargs)

        self._build_toolbar()
        self._build_table()
        self.refresh_table()

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search Bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search by Patient Name, Doctor or Appt ID...",
            on_search=lambda q: self.refresh_table()
        )
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Status filter
        st_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=6, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        st_box.pack(side="left", padx=(0, 10))

        tk.Label(st_box, text="Status:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 3))
        self.status_var = tk.StringVar(value="All Status")
        statuses = ["All Status", "Scheduled", "In Progress", "Completed", "Cancelled"]
        st_menu = ttk.Combobox(st_box, textvariable=self.status_var, values=statuses, state="readonly", width=13)
        st_menu.pack(side="left")
        st_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Action Buttons
        btn_book = ModernButton(
            toolbar,
            text="Book",
            icon="+",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=12,
            pady=6,
            command=self.open_book_modal
        )
        btn_book.pack(side="left", padx=(0, 6))

        btn_comp = ModernButton(
            toolbar,
            text="Done",
            icon="✔",
            style="success",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=lambda: self._update_status("Completed")
        )
        btn_comp.pack(side="left", padx=(0, 6))

        btn_cancel = ModernButton(
            toolbar,
            text="Cancel",
            icon="✕",
            style="danger",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=lambda: self._update_status("Cancelled")
        )
        btn_cancel.pack(side="left")

    def _build_table(self):
        card = CardFrame(
            self,
            title="Outpatient Consultation Schedule",
            subtitle="Scheduled doctor consultations, checkups, and reviews"
        )
        card.pack(fill="both", expand=True)

        table_box = tk.Frame(card, bg=Theme.BG_CARD)
        table_box.pack(fill="both", expand=True, pady=(2, 0))

        columns = ("id", "patient", "doctor", "department", "date", "time", "status", "reason")
        self.tree = ttk.Treeview(table_box, columns=columns, show="headings")

        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("patient", text="PATIENT NAME", anchor="w")
        self.tree.heading("doctor", text="PHYSICIAN", anchor="w")
        self.tree.heading("department", text="DEPARTMENT", anchor="w")
        self.tree.heading("date", text="DATE", anchor="center")
        self.tree.heading("time", text="TIME", anchor="center")
        self.tree.heading("status", text="STATUS", anchor="center")
        self.tree.heading("reason", text="CLINICAL REASON", anchor="w")

        self.tree.column("id", width=95, minwidth=85, stretch=True)
        self.tree.column("patient", width=140, minwidth=120, stretch=True)
        self.tree.column("doctor", width=145, minwidth=120, stretch=True)
        self.tree.column("department", width=115, minwidth=95, stretch=True)
        self.tree.column("date", width=95, minwidth=85, stretch=True)
        self.tree.column("time", width=90, minwidth=80, stretch=True)
        self.tree.column("status", width=105, minwidth=90, stretch=True)
        self.tree.column("reason", width=200, minwidth=140, stretch=True)

        scroll_y = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8fafc")

    def refresh_table(self):
        query = self.search_bar.get_query()
        status_filter = self.status_var.get()

        for r in self.tree.get_children():
            self.tree.delete(r)

        appts = database.get_all_appointments(search_text=query, status_filter=status_filter)

        for idx, a in enumerate(appts):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert(
                "",
                "end",
                values=(
                    a["appointment_id"],
                    a["patient_name"],
                    a["doctor_name"],
                    a["department"],
                    a["appt_date"],
                    a["appt_time"],
                    f"● {a['status']}",
                    a["reason"] or "Routine Consultation"
                ),
                tags=(tag,)
            )

    def _update_status(self, new_status):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("No Selection", "Please select an appointment from the table.")
            return
        appt_id = self.tree.item(item[0], "values")[0]
        database.update_appointment_status(appt_id, new_status)
        self.refresh_table()
        messagebox.showinfo("Status Updated", f"Appointment {appt_id} marked as {new_status}.")

    def open_book_modal(self):
        BookAppointmentModal(self, on_save=self.refresh_table)


class BookAppointmentModal(tk.Toplevel):
    """Modal dialog for scheduling an appointment."""
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Schedule Consultation • Medicare HMS")
        self.geometry("540x520")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 540) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="📅 Book Consultation Appointment",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Schedule outpatient appointments with doctors & choose consultation slot",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        form = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        form.pack(fill="both", expand=True)

        self.entries = {}

        self._add_field(form, "Patient Name *", "patient_name", 0, 0, colspan=2)

        doctors_records = database.get_all_doctors()
        doctor_names = [d["full_name"] for d in doctors_records]
        if not doctor_names:
            doctor_names = ["Dr. Sarah Jenkins", "Dr. Rajesh Sharma", "Dr. Emily Watson"]

        self._add_dropdown(form, "Consulting Physician *", "doctor_name", doctor_names, 1, 0)
        departments = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Internal Medicine", "Pulmonology"]
        self._add_dropdown(form, "Department *", "department", departments, 1, 1)

        today_str = datetime.now().strftime("%Y-%m-%d")
        self._add_field(form, "Date (YYYY-MM-DD) *", "appt_date", 2, 0, default_val=today_str)

        time_slots = [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
            "11:30 AM", "01:00 PM", "01:30 PM", "02:00 PM", "03:00 PM", "04:30 PM"
        ]
        self._add_dropdown(form, "Time Slot *", "appt_time", time_slots, 2, 1)

        self._add_field(form, "Reason for Visit / Symptoms", "reason", 3, 0, colspan=2)

        btn_bar = tk.Frame(self, bg=Theme.BG_CARD_ALT, padx=20, pady=12, highlightbackground=Theme.BORDER, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        ModernButton(
            btn_bar,
            text="Cancel",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=6,
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Confirm Booking",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=16,
            pady=6,
            command=self._save_appointment
        ).pack(side="right")

    def _add_field(self, parent, label, key, row, col, colspan=1, default_val=""):
        frame = tk.Frame(parent, bg=Theme.BG_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(frame, text=label, font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        entry = tk.Entry(frame, font=Theme.FONT_BODY, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0)
        if default_val:
            entry.insert(0, default_val)
        entry.pack(fill="x", ipady=3)
        self.entries[key] = entry

    def _add_dropdown(self, parent, label, key, options, row, col, colspan=1):
        frame = tk.Frame(parent, bg=Theme.BG_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(frame, text=label, font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        var = tk.StringVar(value=options[0] if options else "")
        combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
        combo.pack(fill="x", ipady=2)
        self.entries[key] = var

    def _save_appointment(self):
        pname = self.entries["patient_name"].get().strip()
        if not pname:
            messagebox.showwarning("Validation Error", "Patient name is required.", parent=self)
            return

        data = {
            "patient_name": pname,
            "doctor_name": self.entries["doctor_name"].get(),
            "department": self.entries["department"].get(),
            "appt_date": self.entries["appt_date"].get().strip(),
            "appt_time": self.entries["appt_time"].get(),
            "status": "Scheduled",
            "reason": self.entries["reason"].get().strip()
        }

        new_id = database.add_appointment(data)
        messagebox.showinfo("Appointment Booked", f"Appointment confirmed!\nBooking ID: {new_id}", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()
