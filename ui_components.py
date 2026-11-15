"""
Anti-Clipping, Retina-Calibrated Reusable UI Components for Medicare Plus HMS.
Eliminates text truncation, provides flexible header layouts, and crisp high-contrast controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from styles import Theme
import database


class LiveVitalsTicker(tk.Frame):
    """Mission-control live hospital broadcast ticker with anti-overflow layout."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#090d16", padx=16, pady=5, **kwargs)

        self.canvas_pulse = tk.Canvas(self, width=12, height=12, bg="#090d16", highlightthickness=0)
        self.canvas_pulse.pack(side="left", padx=(0, 6))
        self.pulse_circle = self.canvas_pulse.create_oval(2, 2, 10, 10, fill="#10b981", outline="")

        self.lbl_title = tk.Label(
            self,
            text="LIVE STATUS:",
            font=(Theme.FONT_FAMILY, 8, "bold"),
            fg="#38bdf8",
            bg="#090d16"
        )
        self.lbl_title.pack(side="left", padx=(0, 8))

        self.lbl_ticker = tk.Label(
            self,
            text="Trauma Center: Ready  •  ICU Vitals: 100% Normal  •  OT-1: Active  •  Ambulance: Fleet Ready",
            font=(Theme.FONT_FAMILY, 9),
            fg="#94a3b8",
            bg="#090d16"
        )
        self.lbl_ticker.pack(side="left", fill="x", expand=True)

        self._blink_state = True
        self._pulse_animation()

    def _pulse_animation(self):
        col = "#10b981" if self._blink_state else "#059669"
        self.canvas_pulse.itemconfig(self.pulse_circle, fill=col)
        self._blink_state = not self._blink_state
        self.after(1200, self._pulse_animation)


class ModernButton(tk.Frame):
    """
    High-contrast, cross-platform button that solves macOS Tkinter
    button color bugs. Supports hover states, icons, and distinct styles.
    """
    STYLES = {
        "primary": {
            "bg": Theme.PRIMARY,
            "hover": Theme.PRIMARY_HOVER,
            "fg": Theme.TEXT_LIGHT,
            "border": Theme.PRIMARY_HOVER,
            "bd": 0
        },
        "success": {
            "bg": Theme.SUCCESS,
            "hover": Theme.SUCCESS_HOVER,
            "fg": Theme.TEXT_LIGHT,
            "border": Theme.SUCCESS_HOVER,
            "bd": 0
        },
        "danger": {
            "bg": Theme.DANGER,
            "hover": Theme.DANGER_HOVER,
            "fg": Theme.TEXT_LIGHT,
            "border": Theme.DANGER_HOVER,
            "bd": 0
        },
        "secondary": {
            "bg": "#ffffff",
            "hover": "#f1f5f9",
            "fg": Theme.TEXT_PRIMARY,
            "border": Theme.BORDER_DARK,
            "bd": 1
        },
        "subtle": {
            "bg": Theme.PRIMARY_LIGHT,
            "hover": "#bae6fd",
            "fg": Theme.PRIMARY_HOVER,
            "border": Theme.PRIMARY_BORDER,
            "bd": 1
        },
        "ghost": {
            "bg": "#ffffff",
            "hover": "#f0f9ff",
            "fg": Theme.PRIMARY,
            "border": "#ffffff",
            "bd": 0
        }
    }

    def __init__(
        self,
        parent,
        text="",
        command=None,
        icon=None,
        style="primary",
        font=None,
        padx=12,
        pady=6,
        width=None,
        **kwargs
    ):
        self.cfg = self.STYLES.get(style, self.STYLES["primary"])
        super().__init__(
            parent,
            bg=self.cfg["bg"],
            highlightbackground=self.cfg["border"],
            highlightthickness=self.cfg["bd"],
            cursor="pointinghand",
            **kwargs
        )
        self.command = command
        self.btn_style = style
        self.font = font or Theme.FONT_BODY_BOLD

        display_text = f"{icon}  {text}" if icon else text

        self.label = tk.Label(
            self,
            text=display_text,
            font=self.font,
            fg=self.cfg["fg"],
            bg=self.cfg["bg"],
            padx=padx,
            pady=pady,
            cursor="pointinghand"
        )
        if width:
            self.label.config(width=width)
        self.label.pack(fill="both", expand=True)

        for w in (self, self.label):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event=None):
        self.config(bg=self.cfg["hover"])
        self.label.config(bg=self.cfg["hover"])

    def _on_leave(self, event=None):
        self.config(bg=self.cfg["bg"])
        self.label.config(bg=self.cfg["bg"])

    def set_text(self, new_text, icon=None):
        txt = f"{icon}  {new_text}" if icon else new_text
        self.label.config(text=txt)


class CardFrame(tk.Frame):
    """Clean white card with subtle border and anti-overflow header."""
    def __init__(self, parent, title=None, subtitle=None, action_button=None, **kwargs):
        super().__init__(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs
        )
        
        if title or action_button:
            header_frame = tk.Frame(self, bg=Theme.BG_CARD)
            header_frame.pack(fill="x", pady=(0, 8))
            
            titles_col = tk.Frame(header_frame, bg=Theme.BG_CARD)
            titles_col.pack(side="left", fill="x", expand=True)
            
            if title:
                t_lbl = tk.Label(
                    titles_col,
                    text=title,
                    font=Theme.FONT_TITLE,
                    fg=Theme.TEXT_PRIMARY,
                    bg=Theme.BG_CARD
                )
                t_lbl.pack(anchor="w")
                
            if subtitle:
                s_lbl = tk.Label(
                    titles_col,
                    text=subtitle,
                    font=Theme.FONT_BODY_SMALL,
                    fg=Theme.TEXT_MUTED,
                    bg=Theme.BG_CARD
                )
                s_lbl.pack(anchor="w", pady=(1, 0))
                
            if action_button:
                btn_widget = action_button(header_frame)
                btn_widget.pack(side="right")

            sep = tk.Frame(self, bg=Theme.BORDER, height=1)
            sep.pack(fill="x", pady=(0, 8))


class StatCard(tk.Frame):
    """
    High-contrast KPI Metric Card with anti-clipping title,
    prominent number, and trend pill.
    """
    def __init__(
        self,
        parent,
        title,
        value,
        subtitle,
        icon="📊",
        accent_color=Theme.PRIMARY,
        accent_bg=Theme.PRIMARY_LIGHT,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            cursor="pointinghand",
            **kwargs
        )
        self.accent_color = accent_color
        self.accent_bg = accent_bg

        # Top Colored Accent Stripe (3px)
        self.top_stripe = tk.Frame(self, bg=accent_color, height=3)
        self.top_stripe.pack(fill="x")

        # Inner container
        self.inner = tk.Frame(self, bg=Theme.BG_CARD, padx=14, pady=12)
        self.inner.pack(fill="both", expand=True)

        # Top row: Title + Icon Badge
        top_row = tk.Frame(self.inner, bg=Theme.BG_CARD)
        top_row.pack(fill="x")

        title_lbl = tk.Label(
            top_row,
            text=title.upper(),
            font=Theme.FONT_CAPTION,
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_CARD,
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Icon bubble (compact 36x36 to prevent crowding)
        icon_box = tk.Canvas(top_row, width=36, height=36, bg=Theme.BG_CARD, highlightthickness=0)
        icon_box.pack(side="right")
        icon_box.create_oval(2, 2, 34, 34, fill=accent_bg, outline=accent_color, width=1)
        icon_box.create_text(18, 18, text=icon, font=(Theme.FONT_FAMILY, 15))

        # Big metric number
        self.val_lbl = tk.Label(
            self.inner,
            text=str(value),
            font=Theme.FONT_STAT_NUMBER,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD,
            anchor="w"
        )
        self.val_lbl.pack(fill="x", pady=(2, 4))

        # Bottom trend pill container
        self.sub_frame = tk.Frame(self.inner, bg=Theme.BG_CARD)
        self.sub_frame.pack(fill="x", anchor="w")

        self.sub_pill = tk.Label(
            self.sub_frame,
            text=f" {subtitle} ",
            font=Theme.FONT_BODY_SMALL,
            fg=accent_color,
            bg=accent_bg,
            padx=6,
            pady=2
        )
        self.sub_pill.pack(side="left")

    def update_value(self, new_val, new_sub=None):
        self.val_lbl.config(text=str(new_val))
        if new_sub:
            self.sub_pill.config(text=f" {new_sub} ")


class ModernHeader(tk.Frame):
    """
    Clean, responsive top header bar calibrated to prevent text crowding.
    """
    def __init__(self, parent, on_quick_action=None, **kwargs):
        super().__init__(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=18,
            pady=10,
            **kwargs
        )
        
        # Left side: slim brand accent + view title hierarchy
        accent = tk.Frame(self, bg=Theme.PRIMARY, width=4)
        accent.pack(side="left", fill="y", padx=(0, 13))
        self.left_box = tk.Frame(self, bg=Theme.BG_CARD)
        self.left_box.pack(side="left", fill="y")
        
        self.title_label = tk.Label(
            self.left_box,
            text="Dashboard Overview",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.left_box,
            text="Medicare Central Campus • Real-time clinical analytics",
            font=Theme.FONT_BODY_SMALL,
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_CARD
        )
        self.subtitle_label.pack(anchor="w", pady=(1, 0))

        # Right side: Clock + Primary CTA
        right_box = tk.Frame(self, bg=Theme.BG_CARD)
        right_box.pack(side="right", fill="y")

        # Clock Box
        clock_box = tk.Frame(right_box, bg=Theme.BG_CARD_ALT, padx=8, pady=4, highlightbackground=Theme.BORDER, highlightthickness=1)
        clock_box.pack(side="left", padx=(0, 10))

        self.time_label = tk.Label(
            clock_box,
            text="",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD_ALT
        )
        self.time_label.pack()

        # HIGH-CONTRAST Primary Action Button
        if on_quick_action:
            self.cta_btn = ModernButton(
                right_box,
                text="New Admission",
                icon="+",
                style="primary",
                font=Theme.FONT_BODY_BOLD,
                padx=14,
                pady=6,
                command=on_quick_action
            )
            self.cta_btn.pack(side="right")

        self._tick_clock()

    def set_view_title(self, title, subtitle=None):
        self.title_label.config(text=title)
        if subtitle:
            self.subtitle_label.config(text=subtitle)

    def _tick_clock(self):
        now_str = datetime.now().strftime("%a, %b %d • %I:%M %p")
        self.time_label.config(text=f"🗓  {now_str}")
        self.after(1000, self._tick_clock)


class ModernSidebar(tk.Frame):
    """
    Sleek Dark Slate Sidebar with anti-truncation layout,
    live chief profile display, edit chief profile modal, and logout action.
    """
    def __init__(self, parent, on_navigate, on_edit_profile=None, on_logout=None, **kwargs):
        super().__init__(
            parent,
            bg=Theme.SECONDARY,
            width=246,
            **kwargs
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.on_edit_profile = on_edit_profile
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.active_tab = None

        # Brand / Logo Header
        brand_frame = tk.Frame(self, bg=Theme.SECONDARY, padx=17, pady=19)
        brand_frame.pack(fill="x")

        logo_row = tk.Frame(brand_frame, bg=Theme.SECONDARY)
        logo_row.pack(anchor="w")

        logo_box = tk.Canvas(logo_row, width=34, height=34, bg=Theme.SECONDARY, highlightthickness=0)
        logo_box.pack(side="left", padx=(0, 8))
        logo_box.create_oval(2, 2, 32, 32, fill="#0369a1", outline=Theme.PRIMARY, width=1.5)
        logo_box.create_text(17, 17, text="✚", font=(Theme.FONT_FAMILY, 14, "bold"), fill="#ffffff")

        brand_text_box = tk.Frame(logo_row, bg=Theme.SECONDARY)
        brand_text_box.pack(side="left")

        brand_title = tk.Label(
            brand_text_box,
            text="MEDICARE PLUS",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg=Theme.TEXT_LIGHT,
            bg=Theme.SECONDARY
        )
        brand_title.pack(anchor="w")

        brand_sub = tk.Label(
            brand_text_box,
            text="CARE OPERATIONS  •  DESKTOP",
            font=Theme.FONT_CAPTION,
            fg=Theme.PRIMARY_BORDER,
            bg=Theme.SECONDARY
        )
        brand_sub.pack(anchor="w")

        sep = tk.Frame(self, bg=Theme.SECONDARY_MUTED, height=1)
        sep.pack(fill="x", padx=12, pady=(4, 10))

        # Navigation Items
        self.nav_container = tk.Frame(self, bg=Theme.SECONDARY)
        self.nav_container.pack(fill="both", expand=True)

        nav_items = [
            ("dashboard", "Dashboard", "📊"),
            ("patients", "Patients", "👥"),
            ("doctors", "Doctors & Staff", "👨‍⚕️"),
            ("appointments", "Appointments", "📅"),
            ("wards", "Wards & Beds", "🛏️"),
            ("billing", "Billing & Invoices", "💳")
        ]

        for tab_id, label, icon in nav_items:
            self._create_nav_item(tab_id, label, icon)

        # Bottom Profile Box with Edit and Logout actions
        self._create_user_profile()

    def _create_nav_item(self, tab_id, label, icon):
        item_btn = tk.Frame(
            self.nav_container,
            bg=Theme.SECONDARY,
            cursor="pointinghand"
        )
        item_btn.pack(fill="x", pady=3, padx=9)

        indicator = tk.Frame(item_btn, bg=Theme.SECONDARY, width=4)
        indicator.pack(side="left", fill="y")

        content_box = tk.Frame(item_btn, bg=Theme.SECONDARY, padx=11, pady=9)
        content_box.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(
            content_box,
            text=icon,
            font=(Theme.FONT_FAMILY, 12),
            fg=Theme.TEXT_LIGHT_MUTED,
            bg=Theme.SECONDARY
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        text_lbl = tk.Label(
            content_box,
            text=label,
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_LIGHT_MUTED,
            bg=Theme.SECONDARY
        )
        text_lbl.pack(side="left")

        elements = [item_btn, indicator, content_box, icon_lbl, text_lbl]

        for elem in elements:
            elem.bind("<Button-1>", lambda e, tid=tab_id: self.select_tab(tid))
            elem.bind("<Enter>", lambda e, b=item_btn, i=icon_lbl, t=text_lbl, tid=tab_id: self._on_hover(b, i, t, tid, True))
            elem.bind("<Leave>", lambda e, b=item_btn, i=icon_lbl, t=text_lbl, tid=tab_id: self._on_hover(b, i, t, tid, False))

        self.nav_buttons[tab_id] = {
            "frame": item_btn,
            "indicator": indicator,
            "content": content_box,
            "icon": icon_lbl,
            "text": text_lbl
        }

    def _create_user_profile(self):
        self.prof_frame = tk.Frame(self, bg=Theme.SECONDARY_HOVER, padx=10, pady=10, highlightbackground=Theme.SECONDARY_MUTED, highlightthickness=1)
        self.prof_frame.pack(side="bottom", fill="x", padx=8, pady=10)

        # Avatar with initial circle
        self.avatar_canvas = tk.Canvas(self.prof_frame, width=32, height=32, bg=Theme.SECONDARY_HOVER, highlightthickness=0)
        self.avatar_canvas.pack(side="left", padx=(0, 8))
        self.avatar_circle = self.avatar_canvas.create_oval(1, 1, 31, 31, fill=Theme.PRIMARY, outline=Theme.PRIMARY_BORDER, width=1)
        self.avatar_text = self.avatar_canvas.create_text(16, 16, text="AS", font=(Theme.FONT_FAMILY, 10, "bold"), fill="#ffffff")

        # Info Box
        info_box = tk.Frame(self.prof_frame, bg=Theme.SECONDARY_HOVER)
        info_box.pack(side="left", fill="both", expand=True)

        self.prof_name_lbl = tk.Label(
            info_box,
            text="Dr. Abhijeet Singh",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.SECONDARY_HOVER,
            anchor="w"
        )
        self.prof_name_lbl.pack(fill="x")

        self.prof_role_lbl = tk.Label(
            info_box,
            text="● Online • Chief",
            font=Theme.FONT_CAPTION,
            fg=Theme.SUCCESS_BORDER,
            bg=Theme.SECONDARY_HOVER,
            anchor="w"
        )
        self.prof_role_lbl.pack(fill="x")

        # Actions Row: Edit Chief Profile button + Logout button
        actions_col = tk.Frame(self.prof_frame, bg=Theme.SECONDARY_HOVER)
        actions_col.pack(side="right")

        edit_btn = tk.Label(
            actions_col,
            text="✏️",
            font=(Theme.FONT_FAMILY, 10),
            bg=Theme.SECONDARY_HOVER,
            fg=Theme.TEXT_LIGHT_MUTED,
            cursor="pointinghand"
        )
        edit_btn.pack(side="top", pady=(0, 2))
        edit_btn.bind("<Button-1>", lambda e: self.open_edit_chief_modal())

        logout_btn = tk.Label(
            actions_col,
            text="🚪",
            font=(Theme.FONT_FAMILY, 10),
            bg=Theme.SECONDARY_HOVER,
            fg=Theme.DANGER_BORDER,
            cursor="pointinghand"
        )
        logout_btn.pack(side="top")
        logout_btn.bind("<Button-1>", lambda e: self._on_logout_click())

        # Clicking the profile card also opens the editor
        for w in (self.prof_frame, self.prof_name_lbl, self.prof_role_lbl, self.avatar_canvas):
            w.bind("<Button-1>", lambda e: self.open_edit_chief_modal())

    def update_profile_display(self, user):
        """Updates the sidebar profile widget with new user info."""
        name = user.get("full_name", "Dr. Abhijeet Singh")
        role = user.get("role", "Chief Medical Officer")
        initials = user.get("initials", "AS")
        st = user.get("status", "Online")

        self.prof_name_lbl.config(text=name)
        self.prof_role_lbl.config(text=f"● {st} • {role.split()[0]}")
        self.avatar_canvas.itemconfig(self.avatar_text, text=initials)

    def open_edit_chief_modal(self):
        """Opens modal to edit Chief Medical Officer details."""
        EditChiefProfileModal(self, on_save=self.update_profile_display)

    def _on_logout_click(self):
        if self.on_logout:
            self.on_logout()

    def _on_hover(self, frame, icon, text, tab_id, is_hover):
        if self.active_tab == tab_id:
            return
        bg_col = Theme.SECONDARY_HOVER if is_hover else Theme.SECONDARY
        fg_col = Theme.TEXT_LIGHT if is_hover else Theme.TEXT_LIGHT_MUTED
        frame.config(bg=bg_col)
        icon.config(bg=bg_col, fg=fg_col)
        text.config(bg=bg_col, fg=fg_col)
        self.nav_buttons[tab_id]["content"].config(bg=bg_col)

    def select_tab(self, tab_id):
        if self.active_tab and self.active_tab in self.nav_buttons:
            old = self.nav_buttons[self.active_tab]
            old["frame"].config(bg=Theme.SECONDARY)
            old["content"].config(bg=Theme.SECONDARY)
            old["indicator"].config(bg=Theme.SECONDARY)
            old["icon"].config(bg=Theme.SECONDARY, fg=Theme.TEXT_LIGHT_MUTED)
            old["text"].config(bg=Theme.SECONDARY, fg=Theme.TEXT_LIGHT_MUTED)

        self.active_tab = tab_id
        if tab_id in self.nav_buttons:
            cur = self.nav_buttons[tab_id]
            cur["frame"].config(bg=Theme.SECONDARY_ACTIVE)
            cur["content"].config(bg=Theme.SECONDARY_ACTIVE)
            cur["indicator"].config(bg=Theme.PRIMARY)
            cur["icon"].config(bg=Theme.SECONDARY_ACTIVE, fg=Theme.PRIMARY_BORDER)
            cur["text"].config(bg=Theme.SECONDARY_ACTIVE, fg=Theme.TEXT_LIGHT)

        if self.on_navigate:
            self.on_navigate(tab_id)


class SearchBar(tk.Frame):
    """Sleek search input with instant callback on keystroke."""
    def __init__(self, parent, placeholder="Search...", on_search=None, **kwargs):
        super().__init__(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_DARK,
            highlightthickness=1,
            padx=8,
            pady=5,
            **kwargs
        )
        self.on_search = on_search
        self.placeholder = placeholder

        icon_lbl = tk.Label(self, text="🔍", font=(Theme.FONT_FAMILY, 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        icon_lbl.pack(side="left", padx=(2, 6))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.entry_var,
            font=Theme.FONT_BODY,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.entry.pack(side="left", fill="both", expand=True)

        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=Theme.TEXT_MUTED)
        self.is_placeholder = True

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry_var.trace_add("write", self._on_text_change)

        clear_btn = tk.Label(self, text="✕", font=(Theme.FONT_FAMILY, 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, cursor="pointinghand")
        clear_btn.pack(side="right", padx=(3, 2))
        clear_btn.bind("<Button-1>", lambda e: self.clear())

    def _on_focus_in(self, event):
        if self.is_placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=Theme.TEXT_PRIMARY)
            self.is_placeholder = False

    def _on_focus_out(self, event):
        if not self.entry.get().strip():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=Theme.TEXT_MUTED)
            self.is_placeholder = True

    def _on_text_change(self, *args):
        if not self.is_placeholder and self.on_search:
            self.on_search(self.entry.get().strip())

    def clear(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=Theme.TEXT_MUTED)
        self.is_placeholder = True
        if self.on_search:
            self.on_search("")

    def get_query(self):
        return "" if self.is_placeholder else self.entry.get().strip()


class EditChiefProfileModal(tk.Toplevel):
    """Modal dialog for editing Chief Medical Officer profile information."""
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Edit Chief Profile • Medicare HMS")
        self.geometry("480x360")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save
        self.profile = database.get_chief_profile()

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 360) // 2
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="👨‍⚕️ Edit Chief Physician Profile",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Update display name, hospital title, and active duty status",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        form = tk.Frame(self, bg=Theme.BG_CARD, padx=24, pady=16)
        form.pack(fill="both", expand=True)

        # Full Name
        tk.Label(form, text="Full Name (with Dr. prefix) *", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        self.entry_name = tk.Entry(form, font=Theme.FONT_BODY, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0)
        self.entry_name.pack(fill="x", ipady=4, pady=(0, 10))
        self.entry_name.insert(0, self.profile.get("full_name", "Dr. Abhijeet Singh"))

        # Role / Designation
        tk.Label(form, text="Hospital Role / Designation *", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        self.entry_role = tk.Entry(form, font=Theme.FONT_BODY, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0)
        self.entry_role.pack(fill="x", ipady=4, pady=(0, 10))
        self.entry_role.insert(0, self.profile.get("role", "Chief Medical Officer"))

        # Active Status
        tk.Label(form, text="Active Duty Status *", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        statuses = ["Online", "In Surgery", "On Clinical Rounds", "In Conference", "Off Duty"]
        current_status = self.profile.get("status", "Online")
        self.status_var = tk.StringVar(value=current_status if current_status in statuses else "Online")
        combo = ttk.Combobox(form, textvariable=self.status_var, values=statuses, state="readonly", font=Theme.FONT_BODY)
        combo.pack(fill="x", ipady=3, pady=(0, 12))

        # Bottom Buttons
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
            text="Save Profile",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=16,
            pady=6,
            command=self._save_profile
        ).pack(side="right")

    def _save_profile(self):
        name = self.entry_name.get().strip()
        role = self.entry_role.get().strip()
        st = self.status_var.get()

        if not name or not role:
            messagebox.showwarning("Validation Error", "Full Name and Role are required.", parent=self)
            return

        updated = database.update_chief_profile(name, role, st)
        messagebox.showinfo("Profile Updated", f"Chief profile updated successfully:\n{name} ({role})", parent=self)
        if self.on_save:
            self.on_save(updated)
        self.destroy()

