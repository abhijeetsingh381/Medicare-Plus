"""
Wards & Bed Allocation Visualizer for Medicare Plus HMS.
Features interactive visual floor plan, dedicated Bed Maintenance / Sanitization controls,
patient assignment, discharge workflows, and status filters.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import Theme
from ui_components import CardFrame, ModernButton


class WardsView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=16, pady=12, **kwargs)

        self._build_summary_bar()
        self._build_toolbar()
        self._build_scrollable_wards_canvas()
        self.refresh_wards()

    def _build_summary_bar(self):
        self.summary_frame = tk.Frame(self, bg=Theme.BG_MAIN)
        self.summary_frame.pack(fill="x", pady=(0, 8))

        for i in range(4):
            self.summary_frame.columnconfigure(i, weight=1, uniform="ward_stat")

        self.stat_total = self._make_quick_metric(self.summary_frame, "TOTAL BEDS", "0", Theme.PRIMARY, 0)
        self.stat_occupied = self._make_quick_metric(self.summary_frame, "OCCUPIED", "0", Theme.DANGER, 1)
        self.stat_available = self._make_quick_metric(self.summary_frame, "VACANT & READY", "0", Theme.SUCCESS, 2)
        self.stat_maintenance = self._make_quick_metric(self.summary_frame, "MAINTENANCE / PREP", "0", Theme.WARNING, 3)

    def _make_quick_metric(self, parent, title, val, color, col):
        card = tk.Frame(parent, bg=Theme.BG_CARD, padx=14, pady=8, highlightbackground=Theme.BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=4)

        t_lbl = tk.Label(card, text=title, font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD)
        t_lbl.pack(anchor="w")

        v_lbl = tk.Label(card, text=val, font=Theme.FONT_TITLE_LARGE, fg=color, bg=Theme.BG_CARD)
        v_lbl.pack(anchor="w", pady=(1, 0))
        return v_lbl

    def _build_toolbar(self):
        """Toolbar with bed status filter and maintenance quick actions."""
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 8))

        filter_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=8, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        filter_box.pack(side="left")

        tk.Label(filter_box, text="Filter Beds:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.bed_filter_var = tk.StringVar(value="All Beds")
        options = ["All Beds", "Available Only", "Occupied Only", "Maintenance Only"]
        combo = ttk.Combobox(filter_box, textvariable=self.bed_filter_var, values=options, state="readonly", width=16)
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_wards())

        # Legend pill labels
        legend_row = tk.Frame(toolbar, bg=Theme.BG_MAIN)
        legend_row.pack(side="right")

        tk.Label(legend_row, text="🟢 Available", font=Theme.FONT_CAPTION, fg=Theme.SUCCESS_TEXT, bg=Theme.SUCCESS_LIGHT, padx=6, pady=2).pack(side="left", padx=2)
        tk.Label(legend_row, text="🔴 Occupied", font=Theme.FONT_CAPTION, fg=Theme.DANGER_TEXT, bg=Theme.DANGER_LIGHT, padx=6, pady=2).pack(side="left", padx=2)
        tk.Label(legend_row, text="🟡 In Maintenance", font=Theme.FONT_CAPTION, fg=Theme.WARNING_TEXT, bg=Theme.WARNING_LIGHT, padx=6, pady=2).pack(side="left", padx=2)

    def _build_scrollable_wards_canvas(self):
        self.canvas = tk.Canvas(self, bg=Theme.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.wards_content = tk.Frame(self.canvas, bg=Theme.BG_MAIN)

        self.wards_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.wards_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width - 20)

    def refresh_wards(self):
        for w in self.wards_content.winfo_children():
            w.destroy()

        wards = database.get_all_wards()
        total_beds = len(wards)
        occupied = sum(1 for b in wards if b["status"] == "Occupied")
        available = sum(1 for b in wards if b["status"] == "Available")
        maint = sum(1 for b in wards if b["status"] == "Maintenance")

        self.stat_total.config(text=f"{total_beds} Beds")
        self.stat_occupied.config(text=f"{occupied} Inpatients")
        self.stat_available.config(text=f"{available} Ready")
        self.stat_maintenance.config(text=f"{maint} In Prep")

        filter_val = self.bed_filter_var.get()

        grouped = {}
        for b in wards:
            st = b["status"]
            if filter_val == "Available Only" and st != "Available":
                continue
            if filter_val == "Occupied Only" and st != "Occupied":
                continue
            if filter_val == "Maintenance Only" and st != "Maintenance":
                continue

            wn = b["ward_name"]
            if wn not in grouped:
                grouped[wn] = []
            grouped[wn].append(b)

        if not grouped:
            empty_lbl = tk.Label(
                self.wards_content,
                text="No beds found matching the selected filter.",
                font=Theme.FONT_HEADING,
                fg=Theme.TEXT_MUTED,
                bg=Theme.BG_MAIN,
                pady=40
            )
            empty_lbl.pack()
            return

        for ward_name, bed_list in grouped.items():
            ward_card = CardFrame(
                self.wards_content,
                title=f"🏥 {ward_name}",
                subtitle=f"{len(bed_list)} Beds Shown • {bed_list[0]['ward_type']} Category • ${bed_list[0]['daily_rate']:.0f}/day"
            )
            ward_card.pack(fill="x", pady=(0, 12))

            grid = tk.Frame(ward_card, bg=Theme.BG_CARD)
            grid.pack(fill="x", pady=(2, 0))

            cols = 4
            for i in range(cols):
                grid.columnconfigure(i, weight=1, uniform="bed_col")

            for idx, bed in enumerate(bed_list):
                r = idx // cols
                c = idx % cols
                bed_widget = self._create_bed_card(grid, bed)
                bed_widget.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

    def _create_bed_card(self, parent, bed):
        st = bed["status"]
        if st == "Occupied":
            bg_col = "#fef2f2"
            border_col = "#f87171"
            st_col = Theme.DANGER_TEXT
            st_badge_bg = Theme.DANGER_LIGHT
            icon = "🔴"
        elif st == "Available":
            bg_col = "#f0fdf4"
            border_col = "#4ade80"
            st_col = Theme.SUCCESS_TEXT
            st_badge_bg = Theme.SUCCESS_LIGHT
            icon = "🟢"
        else: # Maintenance
            bg_col = "#fffbeb"
            border_col = "#facc15"
            st_col = Theme.WARNING_TEXT
            st_badge_bg = Theme.WARNING_LIGHT
            icon = "🟡"

        card = tk.Frame(
            parent,
            bg=bg_col,
            highlightbackground=border_col,
            highlightthickness=1,
            padx=10,
            pady=10
        )

        top_row = tk.Frame(card, bg=bg_col)
        top_row.pack(fill="x")

        bed_lbl = tk.Label(
            top_row,
            text=f"🛏 {bed['bed_number']}",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=bg_col
        )
        bed_lbl.pack(side="left")

        st_lbl = tk.Label(
            top_row,
            text=f" {icon} {st} ",
            font=Theme.FONT_CAPTION,
            fg=st_col,
            bg=st_badge_bg,
            padx=5,
            pady=2,
            highlightbackground=border_col,
            highlightthickness=1
        )
        st_lbl.pack(side="right")

        pt_name = bed["patient_name"] if st == "Occupied" else ("Vacant & Ready" if st == "Available" else "🛠 Sanitizing / Prep")
        pt_font = Theme.FONT_BODY_BOLD if st == "Occupied" else Theme.FONT_BODY
        pt_fg = Theme.TEXT_PRIMARY if st == "Occupied" else Theme.TEXT_MUTED

        name_lbl = tk.Label(
            card,
            text=pt_name,
            font=pt_font,
            fg=pt_fg,
            bg=bg_col,
            anchor="w"
        )
        name_lbl.pack(fill="x", pady=(6, 4))

        # ACTION BUTTONS BASED ON STATE
        btn_row = tk.Frame(card, bg=bg_col)
        btn_row.pack(fill="x")

        if st == "Available":
            # Assign Patient Button + Set Maintenance Button
            ModernButton(
                btn_row,
                text="Assign",
                style="primary",
                font=Theme.FONT_BODY_BOLD,
                padx=6,
                pady=4,
                command=lambda b=bed: self._open_assign_modal(b)
            ).pack(side="left", fill="x", expand=True, padx=(0, 3))

            ModernButton(
                btn_row,
                text="Prep 🛠",
                style="secondary",
                font=Theme.FONT_BODY_BOLD,
                padx=5,
                pady=4,
                command=lambda b=bed: self._set_bed_maintenance(b)
            ).pack(side="right", padx=(3, 0))

        elif st == "Occupied":
            # Release Bed button + Discharge to Maintenance button
            ModernButton(
                btn_row,
                text="Release",
                style="danger",
                font=Theme.FONT_BODY_BOLD,
                padx=6,
                pady=4,
                command=lambda b=bed: self._release_bed(b)
            ).pack(side="left", fill="x", expand=True, padx=(0, 3))

            ModernButton(
                btn_row,
                text="Prep 🛠",
                style="secondary",
                font=Theme.FONT_BODY_BOLD,
                padx=5,
                pady=4,
                command=lambda b=bed: self._discharge_to_maintenance(b)
            ).pack(side="right", padx=(3, 0))

        else: # Maintenance
            # Mark Available / Ready Button
            ModernButton(
                btn_row,
                text="✔ Mark Ready (Available)",
                style="success",
                font=Theme.FONT_BODY_BOLD,
                padx=6,
                pady=4,
                command=lambda b=bed: self._mark_bed_ready(b)
            ).pack(fill="x")

        return card

    def _set_bed_maintenance(self, bed):
        """Puts a vacant bed into maintenance for sanitization or repairs."""
        b_num = bed["bed_number"]
        confirm = messagebox.askyesno(
            "Set Bed to Maintenance",
            f"Put bed {b_num} into Maintenance mode for sanitization / repairs?\nBed will be marked as unavailable until prepped."
        )
        if confirm:
            database.update_bed(b_num, "Maintenance", None)
            self.refresh_wards()
            messagebox.showinfo("Maintenance Mode Active", f"Bed {b_num} is now under maintenance.")

    def _discharge_to_maintenance(self, bed):
        """Discharges patient and immediately marks the bed for sanitization."""
        b_num = bed["bed_number"]
        confirm = messagebox.askyesno(
            "Discharge to Maintenance",
            f"Discharge patient ({bed['patient_name']}) and immediately put bed {b_num} into Sanitization / Maintenance?"
        )
        if confirm:
            database.update_bed(b_num, "Maintenance", None)
            self.refresh_wards()
            messagebox.showinfo("Bed Discharged & Under Prep", f"Bed {b_num} is now in sanitization.")

    def _mark_bed_ready(self, bed):
        """Completes maintenance and sets bed back to Available."""
        b_num = bed["bed_number"]
        database.update_bed(b_num, "Available", None)
        self.refresh_wards()
        messagebox.showinfo("Prep Complete", f"Bed {b_num} sanitization complete! Now Vacant & Ready for admission.")

    def _release_bed(self, bed):
        b_num = bed["bed_number"]
        confirm = messagebox.askyesno(
            "Release Bed",
            f"Release bed {b_num} (assigned to {bed['patient_name']})?\nThis marks the bed as Available."
        )
        if confirm:
            database.update_bed(b_num, "Available", None)
            self.refresh_wards()
            messagebox.showinfo("Bed Released", f"Bed {b_num} is now available.")

    def _open_assign_modal(self, bed):
        AssignBedModal(self, bed_number=bed["bed_number"], on_save=self.refresh_wards)


class AssignBedModal(tk.Toplevel):
    """Modal for assigning an admitted patient to a vacant bed."""
    def __init__(self, parent, bed_number, on_save=None):
        super().__init__(parent)
        self.title(f"Assign Bed {bed_number} • Medicare HMS")
        self.geometry("460x300")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.bed_number = bed_number
        self.on_save = on_save

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 460) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"+{x}+{y}")

        self._build_dialog()

    def _build_dialog(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=18, pady=14)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"🛏 Assign Bed: {self.bed_number}",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        body = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Select Registered Patient for Inpatient Admission:",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD
        ).pack(anchor="w", pady=(0, 6))

        patients = database.get_all_patients()
        patient_options = [p["full_name"] for p in patients]
        if not patient_options:
            patient_options = ["Eleanor Vance", "James Robinson", "Sophia Martinez"]

        self.patient_var = tk.StringVar(value=patient_options[0])
        combo = ttk.Combobox(body, textvariable=self.patient_var, values=patient_options, state="readonly")
        combo.pack(fill="x", ipady=3, pady=(0, 14))

        btn_bar = tk.Frame(self, bg=Theme.BG_CARD_ALT, padx=18, pady=12, highlightbackground=Theme.BORDER, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        ModernButton(
            btn_bar,
            text="Cancel",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=12,
            pady=5,
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Confirm Assignment",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=5,
            command=self._confirm
        ).pack(side="right")

    def _confirm(self):
        pname = self.patient_var.get()
        database.update_bed(self.bed_number, "Occupied", pname)
        messagebox.showinfo("Bed Assigned", f"Bed {self.bed_number} assigned to {pname}.", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()
