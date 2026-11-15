"""
Anti-Clipping Patients View for Medicare Plus Hospital Management System.
Features proportional stretch columns, concise headers, and flexible search/filter bar.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database
from styles import Theme
from ui_components import CardFrame, SearchBar, ModernButton


class PatientsView(tk.Frame):
    def __init__(self, parent, on_view_patient=None, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=16, pady=12, **kwargs)
        self.on_view_patient = on_view_patient

        self._build_top_controls()
        self._build_patient_table()
        self.refresh_table()

    def _build_top_controls(self):
        """Action toolbar with flexible search, filters, and high-contrast buttons."""
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search by Name, Patient ID, Phone or Doctor...",
            on_search=lambda q: self.refresh_table()
        )
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Department Filter
        dept_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=6, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        dept_box.pack(side="left", padx=(0, 8))

        tk.Label(dept_box, text="Dept:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 3))
        self.dept_var = tk.StringVar(value="All Departments")
        departments = ["All Departments", "Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Internal Medicine", "Pulmonology"]
        dept_menu = ttk.Combobox(dept_box, textvariable=self.dept_var, values=departments, state="readonly", width=14)
        dept_menu.pack(side="left")
        dept_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Status Filter
        status_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=6, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        status_box.pack(side="left", padx=(0, 10))

        tk.Label(status_box, text="Status:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 3))
        self.status_var = tk.StringVar(value="All Status")
        statuses = ["All Status", "Admitted", "ICU", "Under Observation", "Outpatient", "Discharged"]
        status_menu = ttk.Combobox(status_box, textvariable=self.status_var, values=statuses, state="readonly", width=12)
        status_menu.pack(side="left")
        status_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Action Buttons
        btn_add = ModernButton(
            toolbar,
            text="Register",
            icon="+",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=12,
            pady=6,
            command=self.open_add_patient_modal
        )
        btn_add.pack(side="left", padx=(0, 6))

        btn_view = ModernButton(
            toolbar,
            text="Dossier",
            icon="👁",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=self._view_selected_patient
        )
        btn_view.pack(side="left", padx=(0, 6))

        btn_del = ModernButton(
            toolbar,
            text="Delete",
            icon="🗑",
            style="danger",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=self._delete_selected_patient
        )
        btn_del.pack(side="left")

    def _build_patient_table(self):
        card = CardFrame(
            self,
            title="Patient Master Registry",
            subtitle="Central directory of all hospital admissions and medical records"
        )
        card.pack(fill="both", expand=True)

        table_box = tk.Frame(card, bg=Theme.BG_CARD)
        table_box.pack(fill="both", expand=True, pady=(2, 0))

        columns = ("id", "name", "demographics", "blood", "dept", "doctor", "admission", "status", "condition")
        self.tree = ttk.Treeview(table_box, columns=columns, show="headings")

        # Concise headings that never cut off
        self.tree.heading("id", text="PATIENT ID", anchor="w")
        self.tree.heading("name", text="FULL NAME", anchor="w")
        self.tree.heading("demographics", text="AGE/SEX", anchor="w")
        self.tree.heading("blood", text="BLOOD", anchor="center")
        self.tree.heading("dept", text="DEPARTMENT", anchor="w")
        self.tree.heading("doctor", text="PHYSICIAN", anchor="w")
        self.tree.heading("admission", text="ADMITTED", anchor="center")
        self.tree.heading("status", text="STATUS", anchor="center")
        self.tree.heading("condition", text="CONDITION", anchor="center")

        # Proportional widths with stretch=True
        self.tree.column("id", width=105, minwidth=90, stretch=True)
        self.tree.column("name", width=140, minwidth=120, stretch=True)
        self.tree.column("demographics", width=85, minwidth=75, stretch=True)
        self.tree.column("blood", width=65, minwidth=55, stretch=True)
        self.tree.column("dept", width=115, minwidth=95, stretch=True)
        self.tree.column("doctor", width=145, minwidth=115, stretch=True)
        self.tree.column("admission", width=100, minwidth=90, stretch=True)
        self.tree.column("status", width=95, minwidth=85, stretch=True)
        self.tree.column("condition", width=110, minwidth=90, stretch=True)

        scroll_y = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8fafc")

        self.tree.bind("<Double-1>", lambda e: self._view_selected_patient())

    def refresh_table(self):
        query = self.search_bar.get_query()
        dept = self.dept_var.get()
        status = self.status_var.get()

        for r in self.tree.get_children():
            self.tree.delete(r)

        patients = database.get_all_patients(
            search_text=query,
            department_filter=dept,
            status_filter=status
        )

        for idx, p in enumerate(patients):
            tag = "even" if idx % 2 == 0 else "odd"
            
            cond = p["condition"]
            cond_display = f"● {cond}"
            if cond == "Critical":
                cond_display = "⚠️ Critical"
            elif cond == "Stable":
                cond_display = "✔ Stable"

            self.tree.insert(
                "",
                "end",
                values=(
                    p["patient_id"],
                    p["full_name"],
                    f"{p['age']}y / {p['gender'][:1]}",
                    p["blood_group"] or "—",
                    p["department"],
                    p["doctor_name"],
                    p["admission_date"],
                    f"● {p['status']}",
                    cond_display
                ),
                tags=(tag,)
            )

    def _get_selected_patient_id(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("No Selection", "Please select a patient from the table.")
            return None
        return self.tree.item(item[0], "values")[0]

    def _view_selected_patient(self):
        pid = self._get_selected_patient_id()
        if pid:
            self.show_patient_details(pid)

    def _delete_selected_patient(self):
        pid = self._get_selected_patient_id()
        if not pid:
            return
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete patient record {pid}?\nThis action cannot be undone."
        )
        if confirm:
            database.delete_patient(pid)
            self.refresh_table()
            messagebox.showinfo("Success", f"Patient record {pid} deleted.")

    def open_add_patient_modal(self):
        AddPatientModal(self, on_save=self.refresh_table)

    def show_patient_details(self, patient_id):
        PatientDossierModal(self, patient_id=patient_id)


class AddPatientModal(tk.Toplevel):
    """High-contrast modal dialog for registering a new patient."""
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("New Patient Registration • Medicare HMS")
        self.geometry("580x620")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 580) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🏥 New Patient Admission",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Enter patient demographics, assigned physician, and clinical status",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        form = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        form.pack(fill="both", expand=True)

        self.entries = {}

        self._add_field(form, "Full Name *", "full_name", row=0, col=0, colspan=2)
        self._add_field(form, "Age *", "age", row=1, col=0, width=12)
        self._add_dropdown(form, "Gender *", "gender", ["Female", "Male", "Other"], row=1, col=1)

        self._add_dropdown(form, "Blood Group", "blood_group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], row=2, col=0)
        self._add_field(form, "Phone Number *", "phone", row=2, col=1)

        self._add_field(form, "Email Address", "email", row=3, col=0)
        departments = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Internal Medicine", "Pulmonology"]
        self._add_dropdown(form, "Department *", "department", departments, row=3, col=1)

        doctors = [d["full_name"] for d in database.get_all_doctors()]
        if not doctors:
            doctors = ["Dr. Sarah Jenkins", "Dr. Rajesh Sharma", "Dr. Emily Watson"]
        self._add_dropdown(form, "Attending Physician *", "doctor_name", doctors, row=4, col=0)
        self._add_dropdown(form, "Admission Status *", "status", ["Admitted", "ICU", "Under Observation", "Outpatient"], row=4, col=1)

        self._add_dropdown(form, "Clinical Condition *", "condition", ["Stable", "Critical", "Under Observation", "Recovering"], row=5, col=0)
        self._add_field(form, "Residential Address", "address", row=6, col=0, colspan=2)

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
            text="Admit Patient",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=16,
            pady=6,
            command=self._save_patient
        ).pack(side="right")

    def _add_field(self, parent, label, key, row, col, colspan=1, width=None):
        frame = tk.Frame(parent, bg=Theme.BG_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(frame, text=label, font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        entry = tk.Entry(frame, font=Theme.FONT_BODY, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0)
        if width:
            entry.config(width=width)
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

    def _save_patient(self):
        full_name = self.entries["full_name"].get().strip()
        age_str = self.entries["age"].get().strip()
        phone = self.entries["phone"].get().strip()

        if not full_name:
            messagebox.showwarning("Validation Error", "Patient full name is required.", parent=self)
            return

        try:
            age = int(age_str)
            if age <= 0 or age > 130:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid age (1-130).", parent=self)
            return

        if not phone:
            messagebox.showwarning("Validation Error", "Contact phone number is required.", parent=self)
            return

        data = {
            "full_name": full_name,
            "age": age,
            "gender": self.entries["gender"].get(),
            "blood_group": self.entries["blood_group"].get(),
            "phone": phone,
            "email": self.entries["email"].get().strip(),
            "address": self.entries["address"].get().strip(),
            "department": self.entries["department"].get(),
            "doctor_name": self.entries["doctor_name"].get(),
            "admission_date": datetime.now().strftime("%Y-%m-%d"),
            "status": self.entries["status"].get(),
            "condition": self.entries["condition"].get()
        }

        new_id = database.add_patient(data)
        messagebox.showinfo("Admission Successful", f"Patient admitted successfully!\nAssigned ID: {new_id}", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()


class PatientDossierModal(tk.Toplevel):
    """Detailed Medical Dossier Popup for a selected patient."""
    def __init__(self, parent, patient_id):
        super().__init__(parent)
        self.title(f"Patient Dossier • {patient_id}")
        self.geometry("600x520")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        patients = database.get_all_patients()
        self.patient = next((p for p in patients if p["patient_id"] == patient_id), None)

        if not self.patient:
            messagebox.showerror("Error", f"Patient {patient_id} not found.", parent=self)
            self.destroy()
            return

        self._build_dossier()

    def _build_dossier(self):
        p = self.patient

        top_header = tk.Frame(self, bg=Theme.SECONDARY, padx=20, pady=16)
        top_header.pack(fill="x")

        id_pill = tk.Label(
            top_header,
            text=f"  {p['patient_id']}  ",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.SECONDARY_HOVER
        )
        id_pill.pack(anchor="w")

        name_lbl = tk.Label(
            top_header,
            text=p["full_name"],
            font=Theme.FONT_TITLE_HERO,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.SECONDARY
        )
        name_lbl.pack(anchor="w", pady=(3, 1))

        sub_lbl = tk.Label(
            top_header,
            text=f"{p['age']} Yrs • {p['gender']} • Blood: {p['blood_group'] or 'N/A'}",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.PRIMARY_BORDER,
            bg=Theme.SECONDARY
        )
        sub_lbl.pack(anchor="w")

        body = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        items = [
            ("Department", p["department"]),
            ("Physician", p["doctor_name"]),
            ("Admitted On", p["admission_date"]),
            ("Status", p["status"]),
            ("Condition", p["condition"]),
            ("Phone", p["phone"]),
            ("Email", p["email"] or "None provided"),
            ("Address", p["address"] or "None provided")
        ]

        for i, (k, val) in enumerate(items):
            r = i // 2
            c = i % 2
            card = tk.Frame(body, bg=Theme.BG_CARD_ALT, padx=12, pady=8, highlightbackground=Theme.BORDER, highlightthickness=1)
            card.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
            body.columnconfigure(c, weight=1)

            tk.Label(card, text=k.upper(), font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD_ALT).pack(anchor="w")
            tk.Label(card, text=str(val), font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_PRIMARY, bg=Theme.BG_CARD_ALT).pack(anchor="w", pady=(2, 0))

        btn_bar = tk.Frame(self, bg=Theme.BG_CARD_ALT, padx=20, pady=12, highlightbackground=Theme.BORDER, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        ModernButton(
            btn_bar,
            text="Close Dossier",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=18,
            pady=6,
            command=self.destroy
        ).pack(side="right")
