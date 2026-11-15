"""
Doctors & Medical Staff Directory for Medicare Plus Hospital Management System.
Features physician credential cards, OPD schedule, specialization filtering,
new doctor onboarding, and real-time Doctor Availability Status Update.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import Theme
from ui_components import CardFrame, SearchBar, ModernButton


class DoctorsView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=16, pady=12, **kwargs)

        self._build_toolbar()
        self._build_doctors_container()
        self.refresh_doctors()

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search Bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search doctor by name, specialization, or chamber...",
            on_search=lambda q: self.refresh_doctors()
        )
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Department Filter
        dept_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=6, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        dept_box.pack(side="left", padx=(0, 10))

        tk.Label(dept_box, text="Dept:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 3))
        self.dept_var = tk.StringVar(value="All Departments")
        departments = ["All Departments", "Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Internal Medicine", "Pulmonology"]
        dept_menu = ttk.Combobox(dept_box, textvariable=self.dept_var, values=departments, state="readonly", width=15)
        dept_menu.pack(side="left")
        dept_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_doctors())

        # Add Doctor Button
        btn_add = ModernButton(
            toolbar,
            text="Add Doctor",
            icon="+",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=6,
            command=self.open_add_doctor_modal
        )
        btn_add.pack(side="left")

    def _build_doctors_container(self):
        self.canvas = tk.Canvas(self, bg=Theme.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=Theme.BG_MAIN)

        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width - 20)

    def refresh_doctors(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        query = self.search_bar.get_query().lower()
        dept_filter = self.dept_var.get()

        all_doctors = database.get_all_doctors()
        filtered = []
        for d in all_doctors:
            if dept_filter != "All Departments" and d["department"] != dept_filter:
                continue
            if query:
                match = (
                    query in d["full_name"].lower() or
                    query in d["specialization"].lower() or
                    query in d["department"].lower() or
                    query in d["room_no"].lower()
                )
                if not match:
                    continue
            filtered.append(d)

        if not filtered:
            empty_lbl = tk.Label(
                self.grid_frame,
                text="No doctors found matching your search.",
                font=Theme.FONT_HEADING,
                fg=Theme.TEXT_MUTED,
                bg=Theme.BG_MAIN,
                pady=40
            )
            empty_lbl.pack()
            return

        self.grid_frame.columnconfigure(0, weight=1, uniform="doc_col")
        self.grid_frame.columnconfigure(1, weight=1, uniform="doc_col")

        for idx, doc in enumerate(filtered):
            r = idx // 2
            c = idx % 2
            card = self._create_doctor_card(self.grid_frame, doc)
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

    def _create_doctor_card(self, parent, doc):
        card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=14
        )

        top_row = tk.Frame(card, bg=Theme.BG_CARD)
        top_row.pack(fill="x", pady=(0, 8))

        initials = "".join([part[0] for part in doc["full_name"].replace("Dr. ", "").split()[:2]]).upper()
        avatar = tk.Canvas(top_row, width=38, height=38, bg=Theme.BG_CARD, highlightthickness=0)
        avatar.pack(side="left", padx=(0, 10))
        avatar.create_oval(2, 2, 36, 36, fill=Theme.PRIMARY_LIGHT, outline=Theme.PRIMARY_BORDER, width=1.5)
        avatar.create_text(19, 19, text=initials, font=(Theme.FONT_FAMILY, 11, "bold"), fill=Theme.PRIMARY_HOVER)

        title_box = tk.Frame(top_row, bg=Theme.BG_CARD)
        title_box.pack(side="left", fill="both", expand=True)

        name_lbl = tk.Label(
            title_box,
            text=doc["full_name"],
            font=Theme.FONT_TITLE,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD
        )
        name_lbl.pack(anchor="w")

        spec_lbl = tk.Label(
            title_box,
            text=f"{doc['specialization']} • {doc['experience_years']}y exp",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.PRIMARY_HOVER,
            bg=Theme.BG_CARD
        )
        spec_lbl.pack(anchor="w")

        # Right side: Status Pill + Update Status Button
        st_box = tk.Frame(top_row, bg=Theme.BG_CARD)
        st_box.pack(side="right", anchor="n")

        st = doc["availability"]
        if st == "Available":
            st_color = Theme.SUCCESS_TEXT
            st_bg = Theme.SUCCESS_LIGHT
            icon = "●"
        elif st in ["In Surgery", "In OPD"]:
            st_color = Theme.WARNING_TEXT
            st_bg = Theme.WARNING_LIGHT
            icon = "⏱"
        else:
            st_color = Theme.DANGER_TEXT
            st_bg = Theme.DANGER_LIGHT
            icon = "✕"

        pill = tk.Label(
            st_box,
            text=f" {icon} {st} ",
            font=Theme.FONT_CAPTION,
            fg=st_color,
            bg=st_bg,
            padx=6,
            pady=2,
            highlightbackground=Theme.BORDER,
            highlightthickness=1
        )
        pill.pack(anchor="e")

        # Update Doctor Status Button
        update_btn = ModernButton(
            st_box,
            text="Update Status",
            icon="🔄",
            style="subtle",
            font=Theme.FONT_CAPTION,
            padx=6,
            pady=2,
            command=lambda d=doc: self.open_update_status_modal(d)
        )
        update_btn.pack(anchor="e", pady=(4, 0))

        sep = tk.Frame(card, bg=Theme.BORDER, height=1)
        sep.pack(fill="x", pady=(6, 8))

        info_grid = tk.Frame(card, bg=Theme.BG_CARD)
        info_grid.pack(fill="x")

        items = [
            ("Department", doc["department"]),
            ("Chamber / Room", doc["room_no"]),
            ("OPD Timing", doc["opd_hours"]),
            ("Phone", doc["phone"]),
            ("Email", doc["email"])
        ]

        for k, v in items:
            row = tk.Frame(info_grid, bg=Theme.BG_CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=k + ":", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=str(v), font=Theme.FONT_BODY, fg=Theme.TEXT_PRIMARY, bg=Theme.BG_CARD, anchor="w").pack(side="left", fill="x", expand=True)

        return card

    def open_add_doctor_modal(self):
        AddDoctorModal(self, on_save=self.refresh_doctors)

    def open_update_status_modal(self, doc):
        UpdateDoctorStatusModal(self, doctor=doc, on_save=self.refresh_doctors)


class UpdateDoctorStatusModal(tk.Toplevel):
    """Modal dialog for changing a physician's active availability status."""
    def __init__(self, parent, doctor, on_save=None):
        super().__init__(parent)
        self.title(f"Update Status • {doctor['full_name']}")
        self.geometry("560x430")
        self.minsize(520, 400)
        self.configure(bg=Theme.BG_CARD)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.doctor = doctor
        self.on_save = on_save

        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - 560) // 2)
        y = max(0, (self.winfo_screenheight() - 430) // 2)
        self.geometry(f"560x430+{x}+{y}")

        self._build_dialog()
        self.bind("<Escape>", lambda _event: self.destroy())

    def _build_dialog(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=22, pady=18)
        header.pack(fill="x", side="top")

        tk.Label(
            header,
            text="🔄  Update Doctor Availability",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"{self.doctor['full_name']} • {self.doctor['specialization']}",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(5, 0))

        # Pack the action bar FIRST so it always reserves space at the bottom.
        btn_bar = tk.Frame(
            self, bg=Theme.BG_CARD_ALT, padx=22, pady=14,
            highlightbackground=Theme.BORDER, highlightthickness=1
        )
        btn_bar.pack(fill="x", side="bottom")

        cancel_btn = tk.Button(
            btn_bar, text="Cancel", command=self.destroy,
            font=Theme.FONT_BODY_BOLD, bg="#FFFFFF", fg=Theme.TEXT_PRIMARY,
            activebackground="#E2E8F0", activeforeground=Theme.TEXT_PRIMARY,
            relief="solid", bd=1, padx=20, pady=9, cursor="hand2"
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = tk.Button(
            btn_bar, text="✓  Save Status", command=self._save_status,
            font=Theme.FONT_BODY_BOLD, bg=Theme.PRIMARY, fg="#FFFFFF",
            activebackground=Theme.PRIMARY_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=22, pady=10, cursor="hand2"
        )
        save_btn.pack(side="right")

        body = tk.Frame(self, bg=Theme.BG_CARD, padx=24, pady=20)
        body.pack(fill="both", expand=True, side="top")

        tk.Label(
            body, text="Select Current Availability Status:",
            font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD
        ).pack(anchor="w", pady=(0, 10))

        statuses = ["Available", "In OPD", "In Surgery", "On Leave"]
        current = self.doctor.get("availability", "Available")
        self.status_var = tk.StringVar(
            value=current if current in statuses else "Available"
        )

        combo = ttk.Combobox(
            body, textvariable=self.status_var, values=statuses,
            state="readonly", font=Theme.FONT_BODY
        )
        combo.pack(fill="x", ipady=7, pady=(0, 16))
        combo.focus_set()

        guide_box = tk.Frame(
            body, bg=Theme.BG_CARD_ALT, padx=12, pady=10,
            highlightbackground=Theme.BORDER, highlightthickness=1
        )
        guide_box.pack(fill="x")

        tk.Label(guide_box, text="🟢  Available — Ready for patient consultations",
                 font=Theme.FONT_CAPTION, fg=Theme.SUCCESS_TEXT,
                 bg=Theme.BG_CARD_ALT).pack(anchor="w", pady=2)
        tk.Label(guide_box, text="⏱  In OPD — Currently attending clinic patients",
                 font=Theme.FONT_CAPTION, fg=Theme.WARNING_TEXT,
                 bg=Theme.BG_CARD_ALT).pack(anchor="w", pady=2)
        tk.Label(guide_box, text="🟣  In Surgery — In Operation Theatre",
                 font=Theme.FONT_CAPTION, fg=Theme.PURPLE_TEXT,
                 bg=Theme.BG_CARD_ALT).pack(anchor="w", pady=2)
        tk.Label(guide_box, text="🔴  On Leave — Off duty / Leave",
                 font=Theme.FONT_CAPTION, fg=Theme.DANGER_TEXT,
                 bg=Theme.BG_CARD_ALT).pack(anchor="w", pady=2)

    def _save_status(self):
        new_status = self.status_var.get()
        allowed_statuses = ["Available", "In OPD", "In Surgery", "On Leave"]
        if new_status not in allowed_statuses:
            messagebox.showwarning(
                "Select a status", "Please select a valid availability status.",
                parent=self
            )
            return

        try:
            database.update_doctor_status(self.doctor["doctor_id"], new_status)
            if callable(self.on_save):
                self.on_save()
            messagebox.showinfo(
                "Status Updated",
                f"{self.doctor['full_name']} is now marked as: {new_status}",
                parent=self
            )
            self.destroy()
        except Exception as exc:
            messagebox.showerror(
                "Update Failed",
                f"Could not update the doctor's availability.\n\n{exc}",
                parent=self
            )


class AddDoctorModal(tk.Toplevel):
    """Modal dialog for registering a new physician."""
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Add New Doctor • Medicare HMS")
        self.geometry("540x560")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 540) // 2
        y = (self.winfo_screenheight() - 560) // 2
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="👨‍⚕️ Onboard New Physician",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Add doctor credentials, consulting room, and weekly OPD schedule",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        form = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        form.pack(fill="both", expand=True)

        self.entries = {}

        self._add_field(form, "Full Name (with Dr. prefix) *", "full_name", 0, 0, colspan=2)
        self._add_field(form, "Specialization *", "specialization", 1, 0)

        departments = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Internal Medicine", "Pulmonology", "Radiology", "General Surgery"]
        self._add_dropdown(form, "Department *", "department", departments, 1, 1)

        self._add_field(form, "Phone Number *", "phone", 2, 0)
        self._add_field(form, "Email Address *", "email", 2, 1)

        self._add_field(form, "Experience (Years) *", "experience_years", 3, 0)
        self._add_field(form, "Chamber / Room No *", "room_no", 3, 1)

        self._add_dropdown(form, "Initial Availability *", "availability", ["Available", "In OPD", "In Surgery", "On Leave"], 4, 0)
        self._add_field(form, "OPD Hours *", "opd_hours", 4, 1, default_val="09:00 AM - 02:00 PM")

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
            text="Save Doctor",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=16,
            pady=6,
            command=self._save_doctor
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

    def _save_doctor(self):
        full_name = self.entries["full_name"].get().strip()
        spec = self.entries["specialization"].get().strip()
        phone = self.entries["phone"].get().strip()

        if not full_name or not spec or not phone:
            messagebox.showwarning("Validation Error", "Name, Specialization, and Phone are required.", parent=self)
            return

        try:
            exp = int(self.entries["experience_years"].get().strip() or "0")
        except ValueError:
            exp = 0

        data = {
            "full_name": full_name,
            "specialization": spec,
            "department": self.entries["department"].get(),
            "phone": phone,
            "email": self.entries["email"].get().strip(),
            "experience_years": exp,
            "room_no": self.entries["room_no"].get().strip() or "OPD-101",
            "availability": self.entries["availability"].get(),
            "opd_hours": self.entries["opd_hours"].get().strip()
        }

        new_id = database.add_doctor(data)
        messagebox.showinfo("Success", f"Doctor added successfully!\nAssigned ID: {new_id}", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()
