"""
Login & Authentication View for Medicare Plus Hospital Management System.
Features role-based quick demo buttons, credential validation,
HIPAA compliance badge, and seamless transition to dashboard.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import Theme
from ui_components import ModernButton


class LoginView(tk.Frame):
    """
    State-of-the-art Healthcare Authentication Screen with dual-panel layout.
    """
    def __init__(self, parent, on_login_success=None, on_theme_change=None, **kwargs):
        super().__init__(parent, bg=Theme.SECONDARY, **kwargs)
        self.on_login_success = on_login_success
        self.on_theme_change = on_theme_change
        self._animation_tick = 0
        self._animation_items = {}

        self._build_ui()

    def _build_ui(self):
        # Two-panel layout: Left Hero Branding + Right Sign-In Card
        container = tk.Frame(self, bg=Theme.SECONDARY)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ================= LEFT HERO PANEL =================
        left_panel = tk.Frame(container, bg="#0d1527", padx=40, pady=44, highlightbackground="#1e293b", highlightthickness=1)
        left_panel.pack(side="left", fill="both")

        # Glowing Hospital Emblem
        logo_canvas = tk.Canvas(left_panel, width=54, height=54, bg="#0d1527", highlightthickness=0)
        self.logo_canvas = logo_canvas
        logo_canvas.pack(anchor="w", pady=(0, 14))
        logo_canvas.create_oval(2, 2, 52, 52, fill=Theme.PRIMARY, outline=Theme.PRIMARY_BORDER, width=2)
        logo_canvas.create_text(27, 27, text="✚", font=(Theme.FONT_FAMILY, 24, "bold"), fill="#ffffff")

        brand_lbl = tk.Label(
            left_panel,
            text="MEDICARE PLUS",
            font=(Theme.FONT_FAMILY, 20, "bold"),
            fg="#ffffff",
            bg="#0d1527"
        )
        brand_lbl.pack(anchor="w")

        brand_sub = tk.Label(
            left_panel,
            text="ENTERPRISE HOSPITAL OPERATING SYSTEM",
            font=(Theme.FONT_FAMILY, 9, "bold"),
            fg="#38bdf8",
            bg="#0d1527"
        )
        brand_sub.pack(anchor="w", pady=(2, 14))

        # ================= COLOR THEME SELECTOR =================
        theme_box = tk.Frame(left_panel, bg="#101B22", padx=12, pady=9,
                             highlightbackground="#263B43", highlightthickness=1)
        theme_box.pack(fill="x", pady=(0, 14))
        tk.Label(theme_box, text="COLOR THEME", font=(Theme.FONT_FAMILY, 8, "bold"),
                 fg="#9AB9B0", bg="#101B22").pack(anchor="w", pady=(0, 5))
        theme_row = tk.Frame(theme_box, bg="#101B22")
        theme_row.pack(fill="x")
        theme_options = [
            ("Midnight Emerald", "#00F5A0"),
            ("Cyber Violet", "#B45CFF"),
            ("Solaris Gold", "#FFB800"),
        ]
        self.theme_buttons = {}
        for theme_name, swatch in theme_options:
            b = tk.Button(theme_row, text=f"●  {theme_name}", anchor="w",
                          font=(Theme.FONT_FAMILY, 9, "bold"), fg=swatch,
                          bg="#101B22", activebackground="#1B3037",
                          activeforeground=swatch, relief="flat", bd=0,
                          padx=7, pady=3, cursor="hand2",
                          command=lambda name=theme_name: self._select_theme(name))
            b.pack(side="left", padx=(0, 4))
            self.theme_buttons[theme_name] = b

        # Highlights Bullet Points
        points = [
            ("🏥", "Central Clinical Inpatient & OPD Operations"),
            ("🛏️", "Live Ward & Bed Allocation Matrix with Prep Tracking"),
            ("👨‍⚕️", "Physician Shifts & Real-Time Availability Roster"),
            ("💳", "Integrated Accounts, Billing & Receipt Generation")
        ]

        for icon, desc in points:
            p_row = tk.Frame(left_panel, bg="#0d1527")
            p_row.pack(anchor="w", pady=6)
            tk.Label(p_row, text=icon, font=(Theme.FONT_FAMILY, 12), bg="#0d1527").pack(side="left", padx=(0, 10))
            tk.Label(p_row, text=desc, font=Theme.FONT_BODY, fg="#94a3b8", bg="#0d1527").pack(side="left")

        # Animated clinical illustration: floating bubbles, ECG pulse and moving ambulance.
        self.medical_canvas = tk.Canvas(left_panel, width=470, height=112,
                                        bg="#0d1527", highlightthickness=0)
        self.medical_canvas.pack(fill="x", pady=(12, 2))
        self._draw_medical_scene()
        self._animate_medical_scene()

        # Security Badge at bottom
        sec_box = tk.Frame(left_panel, bg="#131e33", padx=12, pady=8, highlightbackground="#1e293b", highlightthickness=1)
        sec_box.pack(fill="x", pady=(32, 0))

        tk.Label(
            sec_box,
            text="🔒  HIPAA Certified • 256-Bit Encrypted Healthcare Architecture",
            font=(Theme.FONT_FAMILY, 8, "bold"),
            fg="#64748b",
            bg="#131e33"
        ).pack(anchor="w")

        # ================= RIGHT SIGN-IN CARD =================
        right_panel = tk.Frame(container, bg="#ffffff", padx=38, pady=40, highlightbackground=Theme.BORDER, highlightthickness=1)
        right_panel.pack(side="left", fill="both")

        tk.Label(
            right_panel,
            text="Staff Sign In",
            font=(Theme.FONT_FAMILY, 18, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg="#ffffff"
        ).pack(anchor="w")

        tk.Label(
            right_panel,
            text="Access Medicare clinical management portal",
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_MUTED,
            bg="#ffffff"
        ).pack(anchor="w", pady=(2, 16))

        # Demo Role Quick Selector
        role_label = tk.Label(
            right_panel,
            text="DEMO ROLE FAST-LOGIN:",
            font=(Theme.FONT_FAMILY, 8, "bold"),
            fg=Theme.TEXT_MUTED,
            bg="#ffffff"
        )
        role_label.pack(anchor="w", pady=(0, 6))

        role_buttons_row = tk.Frame(right_panel, bg="#ffffff")
        role_buttons_row.pack(fill="x", pady=(0, 16))

        roles = [
            ("Admin / Chief", "admin", "admin123", Theme.PRIMARY),
            ("Physician", "doctor", "doctor123", Theme.SUCCESS),
            ("Receptionist", "reception", "reception123", Theme.PURPLE)
        ]

        for r_name, u_name, p_word, col in roles:
            btn = tk.Button(
                role_buttons_row,
                text=r_name,
                font=(Theme.FONT_FAMILY, 8, "bold"),
                bg="#f1f5f9",
                fg=col,
                activebackground="#e2e8f0",
                relief="solid",
                bd=1,
                padx=8,
                pady=4,
                cursor="pointinghand",
                command=lambda u=u_name, p=p_word: self._fill_credentials(u, p)
            )
            btn.pack(side="left", padx=(0, 6))

        # Username Field
        tk.Label(right_panel, text="Username / Staff ID *", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg="#ffffff").pack(anchor="w", pady=(0, 3))
        self.entry_user = tk.Entry(right_panel, font=Theme.FONT_BODY, bg="#ffffff", fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0, width=32)
        self.entry_user.pack(fill="x", ipady=5, pady=(0, 12))
        self.entry_user.insert(0, "admin")

        # Password Field
        tk.Label(right_panel, text="Password *", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg="#ffffff").pack(anchor="w", pady=(0, 3))
        
        pwd_box = tk.Frame(right_panel, bg="#ffffff", highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        pwd_box.pack(fill="x", pady=(0, 14))

        self.entry_pwd = tk.Entry(pwd_box, font=Theme.FONT_BODY, bg="#ffffff", fg=Theme.TEXT_PRIMARY, relief="flat", bd=0, show="•", highlightthickness=0)
        self.entry_pwd.pack(side="left", fill="both", expand=True, ipady=4, padx=6)
        self.entry_pwd.insert(0, "admin123")

        self.show_pwd = False
        self.toggle_pwd_btn = tk.Label(pwd_box, text="👁", font=(Theme.FONT_FAMILY, 9), bg="#ffffff", fg=Theme.TEXT_MUTED, cursor="pointinghand", padx=6)
        self.toggle_pwd_btn.pack(side="right")
        self.toggle_pwd_btn.bind("<Button-1>", lambda e: self._toggle_show_pwd())

        # Error notification label
        self.lbl_error = tk.Label(right_panel, text="", font=Theme.FONT_BODY_SMALL, fg=Theme.DANGER, bg="#ffffff")
        self.lbl_error.pack(anchor="w", pady=(0, 10))

        # Sign In Button
        self.btn_signin = ModernButton(
            right_panel,
            text="Sign In to Dashboard",
            icon="➔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=20,
            pady=8,
            command=self._attempt_login
        )
        self.btn_signin.pack(fill="x", pady=(0, 14))

        # Bind Enter key to submit
        self.entry_user.bind("<Return>", lambda e: self._attempt_login())
        self.entry_pwd.bind("<Return>", lambda e: self._attempt_login())

        # Demo Credentials Hint
        hint_box = tk.Frame(right_panel, bg="#f8fafc", padx=10, pady=8, highlightbackground=Theme.BORDER, highlightthickness=1)
        hint_box.pack(fill="x")

        tk.Label(
            hint_box,
            text="Default Admin: admin / admin123\nDefault Doctor: doctor / doctor123",
            font=Theme.FONT_CAPTION,
            fg=Theme.TEXT_MUTED,
            bg="#f8fafc",
            justify="left"
        ).pack(anchor="w")

    def _select_theme(self, theme_name):
        """Apply the selected accent palette throughout newly rendered screens."""
        Theme.set_palette(theme_name)
        self.logo_canvas.itemconfig(1, fill=Theme.PRIMARY, outline=Theme.PRIMARY_BORDER)
        for name, button in self.theme_buttons.items():
            button.config(relief="solid" if name == theme_name else "flat",
                          bd=1 if name == theme_name else 0)
        # Update the hero emblem and animated scene accent immediately.
        self._draw_medical_scene()
        if self.on_theme_change:
            self.on_theme_change(theme_name)

    def _draw_medical_scene(self):
        c = self.medical_canvas
        c.delete("all")
        accent = Theme.PRIMARY
        c.create_text(8, 10, anchor="nw", text="CARE IN MOTION  •  CONNECTED CLINICAL WORKFLOW",
                      fill="#8FA9B8", font=(Theme.FONT_FAMILY, 8, "bold"))
        # Soft floating medical bubbles
        bubbles = [(42, 52, 9), (104, 82, 5), (185, 48, 7), (270, 77, 6), (390, 40, 8), (440, 83, 5)]
        for x, y, r in bubbles:
            c.create_oval(x-r, y-r, x+r, y+r, outline="#315064", width=1, tags="bubble")
            c.create_text(x, y, text="+", fill=accent, font=("Arial", max(8, r+5), "bold"))
        # ECG line and moving arrow
        ecg = [(8, 88), (72, 88), (82, 82), (91, 96), (103, 65), (115, 91), (130, 88), (462, 88)]
        c.create_line(*[v for point in ecg for v in point], fill=accent, width=2, smooth=True)
        c.create_text(320, 56, text="⚕", fill="#A9C7D3", font=("Arial", 22), tags="medical_tool")
        # Ambulance body; all parts share a tag so they move together.
        c.create_rectangle(205, 57, 258, 82, fill="#EAF5F7", outline=accent, width=2, tags="ambulance")
        c.create_rectangle(244, 63, 267, 82, fill="#D7EAF0", outline=accent, width=2, tags="ambulance")
        c.create_rectangle(249, 66, 261, 73, fill="#7DD3FC", outline="", tags="ambulance")
        c.create_text(230, 69, text="+", fill=accent, font=("Arial", 17, "bold"), tags="ambulance")
        c.create_oval(214, 77, 226, 89, fill="#172B3A", outline="#9FB5C3", width=2, tags="ambulance")
        c.create_oval(249, 77, 261, 89, fill="#172B3A", outline="#9FB5C3", width=2, tags="ambulance")
        c.create_line(275, 70, 295, 70, fill=accent, width=2, arrow="last", tags="moving_arrow")
        c.create_text(8, 107, anchor="sw", text="PATIENT-FIRST  /  SMARTER HOSPITAL OPERATIONS",
                      fill="#6F8998", font=(Theme.FONT_FAMILY, 7, "bold"))

    def _animate_medical_scene(self):
        """Subtle looping motion; no external assets or extra dependencies."""
        if not self.winfo_exists():
            return
        self._animation_tick += 1
        dx = 1 if (self._animation_tick // 24) % 2 == 0 else -1
        self.medical_canvas.move("ambulance", dx, 0)
        self.medical_canvas.move("moving_arrow", 2, 0)
        arrow_coords = self.medical_canvas.coords("moving_arrow")
        if arrow_coords and arrow_coords[2] > 460:
            self.medical_canvas.move("moving_arrow", -190, 0)
        # Gentle bubble drift, reset after they leave their lane.
        for item in self.medical_canvas.find_withtag("bubble"):
            self.medical_canvas.move(item, 0, -0.35)
            if self.medical_canvas.coords(item)[1] < 24:
                self.medical_canvas.move(item, 0, 62)
        self.after(55, self._animate_medical_scene)

    def _fill_credentials(self, username, password):
        self.entry_user.delete(0, "end")
        self.entry_user.insert(0, username)
        self.entry_pwd.delete(0, "end")
        self.entry_pwd.insert(0, password)
        self.lbl_error.config(text="")

    def _toggle_show_pwd(self):
        self.show_pwd = not self.show_pwd
        self.entry_pwd.config(show="" if self.show_pwd else "•")

    def _attempt_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pwd.get().strip()

        if not username or not password:
            self.lbl_error.config(text="⚠️ Please enter both username and password.")
            return

        user = database.authenticate_user(username, password)
        if user:
            self.lbl_error.config(text="")
            if self.on_login_success:
                self.on_login_success(user)
        else:
            self.lbl_error.config(text="❌ Invalid credentials. Please check demo logins.")
