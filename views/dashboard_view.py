"""
Anti-Clipping Dashboard View for Medicare Plus Hospital Management System.
Features responsive Pillow charts, flexible Treeview column stretching,
and compact, crisp KPI metrics that never cut off text.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import Theme
from ui_components import StatCard, CardFrame, ModernButton
import graphics
from datetime import datetime


class DashboardView(tk.Frame):
    def __init__(self, parent, on_navigate=None, on_view_patient=None, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, **kwargs)
        self.on_navigate = on_navigate
        self.on_view_patient = on_view_patient

        self._donut_img = None
        self._trend_img = None

        self.canvas = tk.Canvas(self, bg=Theme.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content_frame = tk.Frame(self.canvas, bg=Theme.BG_MAIN, padx=16, pady=12)

        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.bind("<Configure>", self._on_resize)

        self._build_welcome_banner()
        self._build_kpi_row()
        self._build_charts_and_tables()
        self.refresh_data()

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width - 20)

    def _build_welcome_banner(self):
        """High-impact welcome panel that gives the dashboard a clear visual start."""
        banner = tk.Frame(self.content_frame, bg="#14283B", padx=22, pady=17,
                          highlightbackground="#203B50", highlightthickness=1)
        banner.pack(fill="x", pady=(0, 14))

        left = tk.Frame(banner, bg="#14283B")
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="HOSPITAL OPERATIONS CENTER", bg="#14283B",
                 fg="#5EEAD4", font=(Theme.FONT_FAMILY, 8, "bold")).pack(anchor="w")
        tk.Label(left, text="A clearer view of better care.", bg="#14283B",
                 fg="#FFFFFF", font=(Theme.FONT_FAMILY, 19, "bold")).pack(anchor="w", pady=(3, 2))
        tk.Label(left, text="Monitor patients, clinical teams, appointments and bed capacity from one workspace.",
                 bg="#14283B", fg="#B7C7D8", font=Theme.FONT_BODY_SMALL).pack(anchor="w")

        right = tk.Frame(banner, bg="#1D3A4C", padx=13, pady=9,
                         highlightbackground="#31566A", highlightthickness=1)
        right.pack(side="right", padx=(12, 0))
        tk.Label(right, text="TODAY", bg="#1D3A4C", fg="#8FAFC0",
                 font=(Theme.FONT_FAMILY, 8, "bold")).pack(anchor="e")
        tk.Label(right, text=datetime.now().strftime("%d %b %Y"), bg="#1D3A4C",
                 fg="#FFFFFF", font=(Theme.FONT_FAMILY, 13, "bold")).pack(anchor="e", pady=(3, 0))

    def _build_kpi_row(self):
        """Top row of 4 KPI cards with concise titles that never clip."""
        self.kpi_container = tk.Frame(self.content_frame, bg=Theme.BG_MAIN)
        self.kpi_container.pack(fill="x", pady=(0, 12))

        for i in range(4):
            self.kpi_container.columnconfigure(i, weight=1, uniform="kpi")

        self.card_patients = StatCard(
            self.kpi_container,
            title="Total Patients",
            value="0",
            subtitle="▲ +14% Month",
            icon="👥",
            accent_color=Theme.PRIMARY,
            accent_bg=Theme.PRIMARY_LIGHT
        )
        self.card_patients.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_admissions = StatCard(
            self.kpi_container,
            title="Inpatients",
            value="0",
            subtitle="🏥 In Wards / ICU",
            icon="🛏️",
            accent_color=Theme.PURPLE,
            accent_bg=Theme.PURPLE_LIGHT
        )
        self.card_admissions.grid(row=0, column=1, sticky="nsew", padx=6)

        self.card_doctors = StatCard(
            self.kpi_container,
            title="Doctors On Duty",
            value="0",
            subtitle="● 4 Active Shifts",
            icon="👨‍⚕️",
            accent_color=Theme.SUCCESS,
            accent_bg=Theme.SUCCESS_LIGHT
        )
        self.card_doctors.grid(row=0, column=2, sticky="nsew", padx=6)

        self.card_occupancy = StatCard(
            self.kpi_container,
            title="Bed Occupancy",
            value="0%",
            subtitle="Calculating...",
            icon="🏨",
            accent_color=Theme.WARNING,
            accent_bg=Theme.WARNING_LIGHT
        )
        self.card_occupancy.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

    def _build_charts_and_tables(self):
        body_grid = tk.Frame(self.content_frame, bg=Theme.BG_MAIN)
        body_grid.pack(fill="both", expand=True)

        body_grid.columnconfigure(0, weight=6)
        body_grid.columnconfigure(1, weight=4)

        # LEFT COLUMN
        left_col = tk.Frame(body_grid, bg=Theme.BG_MAIN)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # 1. 7-Day Trend Chart Card
        trend_card = CardFrame(
            left_col,
            title="📈 7-Day Admissions Curve",
            subtitle="Weekly outpatient & emergency admission volume"
        )
        trend_card.pack(fill="x", pady=(0, 12))

        trend_inner = tk.Frame(trend_card, bg=Theme.BG_CARD)
        trend_inner.pack(fill="x")

        self.trend_canvas = tk.Label(trend_inner, bg=Theme.BG_CARD)
        self.trend_canvas.pack(fill="x", pady=(2, 4))

        days_row = tk.Frame(trend_inner, bg=Theme.BG_CARD)
        days_row.pack(fill="x", padx=10)
        days = ["Mon (14)", "Tue (21)", "Wed (18)", "Thu (29)", "Fri (24)", "Sat (34)", "Sun (31)"]
        for d in days:
            tk.Label(days_row, text=d, font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD).pack(side="left", expand=True)

        # 2. Recent Patient Admissions
        def make_nav_btn(p):
            return ModernButton(
                p,
                text="View All",
                icon="👥",
                style="subtle",
                font=Theme.FONT_BODY_BOLD,
                padx=10,
                pady=4,
                command=lambda: self.on_navigate("patients") if self.on_navigate else None
            )

        recent_card = CardFrame(
            left_col,
            title="Recent Admissions",
            subtitle="Latest registered patients and triage status",
            action_button=make_nav_btn
        )
        recent_card.pack(fill="both", expand=True)

        table_frame = tk.Frame(recent_card, bg=Theme.BG_CARD)
        table_frame.pack(fill="both", expand=True, pady=(2, 0))

        columns = ("id", "name", "dept", "doctor", "condition", "status")
        self.tree_recent = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        # Clean, non-overflowing headings
        self.tree_recent.heading("id", text="ID", anchor="w")
        self.tree_recent.heading("name", text="PATIENT NAME", anchor="w")
        self.tree_recent.heading("dept", text="DEPARTMENT", anchor="w")
        self.tree_recent.heading("doctor", text="PHYSICIAN", anchor="w")
        self.tree_recent.heading("condition", text="CONDITION", anchor="center")
        self.tree_recent.heading("status", text="STATUS", anchor="center")

        # Proportional widths with stretch=True
        self.tree_recent.column("id", width=95, minwidth=85, stretch=True)
        self.tree_recent.column("name", width=130, minwidth=110, stretch=True)
        self.tree_recent.column("dept", width=110, minwidth=95, stretch=True)
        self.tree_recent.column("doctor", width=135, minwidth=110, stretch=True)
        self.tree_recent.column("condition", width=95, minwidth=80, stretch=True)
        self.tree_recent.column("status", width=90, minwidth=75, stretch=True)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_recent.yview)
        self.tree_recent.configure(yscrollcommand=scroll_y.set)

        self.tree_recent.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree_recent.tag_configure("even", background="#ffffff")
        self.tree_recent.tag_configure("odd", background="#f8fafc")

        self.tree_recent.bind("<Double-1>", self._on_recent_row_double_click)

        # Footer Tip
        footer = tk.Frame(recent_card, bg=Theme.BG_CARD_ALT, padx=8, pady=6, highlightbackground=Theme.BORDER, highlightthickness=1)
        footer.pack(fill="x", pady=(6, 0))

        tk.Label(
            footer,
            text="💡 Tip: Double-click any row to view complete patient dossier.",
            font=Theme.FONT_BODY_SMALL,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD_ALT
        ).pack(side="left")

        # RIGHT COLUMN
        right_col = tk.Frame(body_grid, bg=Theme.BG_MAIN)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # 1. Donut Bed Capacity Gauge Card
        def make_ward_btn(p):
            return ModernButton(
                p,
                text="Ward Grid",
                icon="🛏️",
                style="subtle",
                font=Theme.FONT_BODY_BOLD,
                padx=10,
                pady=4,
                command=lambda: self.on_navigate("wards") if self.on_navigate else None
            )

        donut_card = CardFrame(
            right_col,
            title="Bed Occupancy",
            subtitle="Capacity across hospital wings",
            action_button=make_ward_btn
        )
        donut_card.pack(fill="x", pady=(0, 12))

        donut_box = tk.Frame(donut_card, bg=Theme.BG_CARD)
        donut_box.pack(fill="x", pady=2)

        gauge_col = tk.Frame(donut_box, bg=Theme.BG_CARD)
        gauge_col.pack(side="left", padx=(6, 12))

        self.donut_label = tk.Label(gauge_col, bg=Theme.BG_CARD)
        self.donut_label.pack()

        self.donut_center_lbl = tk.Label(gauge_col, text="41% Occupied", font=Theme.FONT_BODY_BOLD, fg=Theme.PRIMARY_HOVER, bg=Theme.BG_CARD)
        self.donut_center_lbl.pack(pady=(2, 0))

        legend_col = tk.Frame(donut_box, bg=Theme.BG_CARD)
        legend_col.pack(side="left", fill="both", expand=True)

        self.leg_occupied = self._make_legend_item(legend_col, "🔴 Occupied Beds", "5 Inpatients", Theme.DANGER_TEXT)
        self.leg_available = self._make_legend_item(legend_col, "🟢 Vacant & Ready", "6 Beds Free", Theme.SUCCESS_TEXT)
        self.leg_maint = self._make_legend_item(legend_col, "🟡 Sanitizing / Prep", "1 Bed In Prep", Theme.WARNING_TEXT)

        # 2. Doctors on duty Card
        def make_doc_btn(p):
            return ModernButton(
                p,
                text="View All",
                icon="👨‍⚕️",
                style="subtle",
                font=Theme.FONT_BODY_BOLD,
                padx=10,
                pady=4,
                command=lambda: self.on_navigate("doctors") if self.on_navigate else None
            )

        doc_card = CardFrame(
            right_col,
            title="Doctors On Duty",
            subtitle="Current shifts and consultation chambers",
            action_button=make_doc_btn
        )
        doc_card.pack(fill="both", expand=True)

        self.doc_container = tk.Frame(doc_card, bg=Theme.BG_CARD)
        self.doc_container.pack(fill="both", expand=True, pady=(2, 0))

    def _make_legend_item(self, parent, title, val, color):
        frame = tk.Frame(parent, bg=Theme.BG_CARD_ALT, padx=8, pady=5, highlightbackground=Theme.BORDER, highlightthickness=1)
        frame.pack(fill="x", pady=2)

        tk.Label(frame, text=title, font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD_ALT).pack(anchor="w")
        lbl = tk.Label(frame, text=val, font=Theme.FONT_BODY_BOLD, fg=color, bg=Theme.BG_CARD_ALT)
        lbl.pack(anchor="w")
        return lbl

    def _on_recent_row_double_click(self, event):
        item = self.tree_recent.selection()
        if not item:
            return
        values = self.tree_recent.item(item[0], "values")
        if values and self.on_view_patient:
            self.on_view_patient(values[0])

    def refresh_data(self):
        metrics = database.get_dashboard_metrics()
        self.card_patients.update_value(metrics["total_patients"], "▲ +14% Month")
        self.card_admissions.update_value(metrics["active_admissions"], f"🏥 {metrics['active_admissions']} Admitted")
        self.card_doctors.update_value(metrics["active_doctors"], "● Ready for OPD")
        self.card_occupancy.update_value(
            f"{metrics['occupancy_pct']}%",
            f"🏨 {metrics['occupied_beds']}/{metrics['total_beds']} Beds"
        )

        # Render Donut Gauge
        pct = metrics["occupancy_pct"]
        bar_color = Theme.DANGER if pct >= 75 else (Theme.WARNING if pct >= 40 else Theme.PRIMARY)
        self._donut_img = graphics.render_donut_chart(size=115, percentage=pct, color=bar_color, bg_track="#e2e8f0", thickness=11)
        self.donut_label.config(image=self._donut_img)
        self.donut_center_lbl.config(text=f"{pct}% Occupied", fg=bar_color)

        wards = database.get_all_wards()
        occupied = sum(1 for b in wards if b["status"] == "Occupied")
        available = sum(1 for b in wards if b["status"] == "Available")
        maint = sum(1 for b in wards if b["status"] == "Maintenance")

        self.leg_occupied.config(text=f"{occupied} Inpatients")
        self.leg_available.config(text=f"{available} Beds Free")
        self.leg_maint.config(text=f"{maint} Bed In Prep")

        # Render Trend Chart (Responsive 480px width)
        self._trend_img = graphics.render_trend_chart(width=480, height=75, values=[14, 21, 18, 29, 24, 34, 31], line_color=Theme.PRIMARY, fill_color="#CCFBF1")
        self.trend_canvas.config(image=self._trend_img)

        # Refresh recent admissions table
        for r in self.tree_recent.get_children():
            self.tree_recent.delete(r)

        patients = database.get_all_patients()
        for idx, p in enumerate(patients[:8]):
            tag = "even" if idx % 2 == 0 else "odd"
            
            cond = p["condition"]
            cond_display = f"● {cond}"
            if cond == "Critical":
                cond_display = "⚠️ Critical"
            elif cond == "Stable":
                cond_display = "✔ Stable"

            st_display = f"● {p['status']}"

            self.tree_recent.insert(
                "",
                "end",
                values=(
                    p["patient_id"],
                    p["full_name"],
                    p["department"],
                    p["doctor_name"],
                    cond_display,
                    st_display
                ),
                tags=(tag,)
            )

        # Refresh Doctors List
        for w in self.doc_container.winfo_children():
            w.destroy()

        doctors = database.get_all_doctors()[:4]
        for d in doctors:
            item = tk.Frame(self.doc_container, bg=Theme.BG_CARD_ALT, padx=10, pady=8, highlightbackground=Theme.BORDER, highlightthickness=1)
            item.pack(fill="x", pady=2)

            initials = "".join([part[0] for part in d["full_name"].replace("Dr. ", "").split()[:2]]).upper()
            avatar = tk.Canvas(item, width=30, height=30, bg=Theme.BG_CARD_ALT, highlightthickness=0)
            avatar.pack(side="left", padx=(0, 8))
            avatar.create_oval(1, 1, 29, 29, fill=Theme.PRIMARY_LIGHT, outline=Theme.PRIMARY_BORDER, width=1)
            avatar.create_text(15, 15, text=initials, font=(Theme.FONT_FAMILY, 9, "bold"), fill=Theme.PRIMARY_HOVER)

            left = tk.Frame(item, bg=Theme.BG_CARD_ALT)
            left.pack(side="left", fill="both", expand=True)

            d_name = tk.Label(
                left,
                text=d["full_name"],
                font=Theme.FONT_BODY_BOLD,
                fg=Theme.TEXT_PRIMARY,
                bg=Theme.BG_CARD_ALT
            )
            d_name.pack(anchor="w")

            d_sub = tk.Label(
                left,
                text=f"{d['specialization']} • {d['room_no']}",
                font=Theme.FONT_CAPTION,
                fg=Theme.TEXT_MUTED,
                bg=Theme.BG_CARD_ALT
            )
            d_sub.pack(anchor="w")

            st = d["availability"]
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
                item,
                text=f"{icon} {st}",
                font=Theme.FONT_CAPTION,
                fg=st_color,
                bg=st_bg,
                padx=6,
                pady=2,
                highlightbackground=Theme.BORDER,
                highlightthickness=1
            )
            pill.pack(side="right")
