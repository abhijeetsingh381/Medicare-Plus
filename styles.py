"""
Clean, High-Legibility Typography and Theme Definitions for Hospital Management System.
Balanced font scales calibrated for macOS Retina displays to prevent text truncation.
"""

import tkinter as tk
from tkinter import ttk

class Theme:
    """Unified premium clinical dashboard palette with selectable accents."""
    ACTIVE_THEME = "Midnight Emerald"
    PALETTES = {
        "Midnight Emerald": {
            "PRIMARY": "#059669", "PRIMARY_HOVER": "#047857", "PRIMARY_ACTIVE": "#065F46",
            "PRIMARY_LIGHT": "#D1FAE5", "PRIMARY_BORDER": "#6EE7B7", "BORDER_FOCUS": "#34D399",
        },
        "Cyber Violet": {
            "PRIMARY": "#9333EA", "PRIMARY_HOVER": "#7E22CE", "PRIMARY_ACTIVE": "#6B21A8",
            "PRIMARY_LIGHT": "#F3E8FF", "PRIMARY_BORDER": "#D8B4FE", "BORDER_FOCUS": "#C084FC",
        },
        "Solaris Gold": {
            "PRIMARY": "#D99A00", "PRIMARY_HOVER": "#B77900", "PRIMARY_ACTIVE": "#925F00",
            "PRIMARY_LIGHT": "#FEF3C7", "PRIMARY_BORDER": "#FCD34D", "BORDER_FOCUS": "#FBBF24",
        },
    }

    @classmethod
    def set_palette(cls, name):
        """Switch the shared accent palette before constructing/rebuilding views."""
        if name not in cls.PALETTES:
            return
        cls.ACTIVE_THEME = name
        for key, value in cls.PALETTES[name].items():
            setattr(cls, key, value)

    # Teal is used as the clinical brand accent; navy anchors navigation.
    PRIMARY = "#0F766E"
    PRIMARY_HOVER = "#115E59"
    PRIMARY_ACTIVE = "#134E4A"
    PRIMARY_LIGHT = "#CCFBF1"
    PRIMARY_BORDER = "#5EEAD4"

    SECONDARY = "#101B2D"
    SECONDARY_HOVER = "#1B2A40"
    SECONDARY_ACTIVE = "#233A52"
    SECONDARY_MUTED = "#30445B"

    BG_MAIN = "#F3F6FA"
    BG_CARD = "#FFFFFF"
    BG_CARD_ALT = "#F8FAFC"
    BG_HOVER = "#EEF5F5"

    BORDER = "#E4EAF0"
    BORDER_DARK = "#CBD5E1"
    BORDER_FOCUS = "#2DD4BF"

    TEXT_PRIMARY = "#142235"
    TEXT_SECONDARY = "#42536A"
    TEXT_MUTED = "#718096"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_LIGHT_MUTED = "#A9B8CA"

    SUCCESS = "#0F9F78"
    SUCCESS_HOVER = "#087F61"
    SUCCESS_LIGHT = "#D1FAE5"
    SUCCESS_BORDER = "#6EE7B7"
    SUCCESS_TEXT = "#065F46"

    WARNING = "#D97706"
    WARNING_HOVER = "#B45309"
    WARNING_LIGHT = "#FEF3C7"
    WARNING_BORDER = "#FCD34D"
    WARNING_TEXT = "#78350F"

    DANGER = "#DC5252"
    DANGER_HOVER = "#B93838"
    DANGER_LIGHT = "#FEE2E2"
    DANGER_BORDER = "#FCA5A5"
    DANGER_TEXT = "#7F1D1D"

    INFO = "#2563EB"
    INFO_HOVER = "#1D4ED8"
    INFO_LIGHT = "#DBEAFE"
    INFO_BORDER = "#93C5FD"
    INFO_TEXT = "#1E3A8A"

    PURPLE = "#7C5CE7"
    PURPLE_HOVER = "#6845D2"
    PURPLE_LIGHT = "#EDE9FE"
    PURPLE_BORDER = "#C4B5FD"
    PURPLE_TEXT = "#4C1D95"

    FONT_FAMILY = "Avenir Next"
    FONT_TITLE_HERO = (FONT_FAMILY, 21, "bold")
    FONT_TITLE_LARGE = (FONT_FAMILY, 16, "bold")
    FONT_TITLE = (FONT_FAMILY, 13, "bold")
    FONT_HEADING = (FONT_FAMILY, 12, "bold")
    FONT_SUBHEADING = (FONT_FAMILY, 11, "bold")
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_SMALL = (FONT_FAMILY, 9)
    FONT_CAPTION = (FONT_FAMILY, 8, "bold")
    FONT_STAT_NUMBER = (FONT_FAMILY, 26, "bold")


def setup_ttk_styles(root):
    """Apply the shared premium theme to native ttk widgets."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure("TFrame", background=Theme.BG_MAIN)
    style.configure("Card.TFrame", background=Theme.BG_CARD)
    style.configure("Sidebar.TFrame", background=Theme.SECONDARY)

    style.configure(
        "Treeview", background=Theme.BG_CARD, foreground=Theme.TEXT_PRIMARY,
        fieldbackground=Theme.BG_CARD, font=Theme.FONT_BODY, rowheight=36,
        borderwidth=0, relief="flat"
    )
    style.map("Treeview",
        background=[("selected", Theme.PRIMARY_LIGHT)],
        foreground=[("selected", Theme.PRIMARY_ACTIVE)])
    style.configure("Treeview.Heading", background="#EAF0F4",
        foreground=Theme.TEXT_SECONDARY, font=Theme.FONT_CAPTION,
        padding=(10, 10), borderwidth=0, relief="flat")
    style.map("Treeview.Heading", background=[("active", "#DDE8EC")])

    style.configure("TEntry", fieldbackground=Theme.BG_CARD,
        foreground=Theme.TEXT_PRIMARY, padding=(9, 7), borderwidth=1,
        relief="solid", insertcolor=Theme.PRIMARY)
    style.map("TEntry", bordercolor=[("focus", Theme.PRIMARY_BORDER)])
    style.configure("TCombobox", background=Theme.BG_CARD,
        foreground=Theme.TEXT_PRIMARY, fieldbackground=Theme.BG_CARD,
        padding=(8, 7), arrowsize=14)
    style.map("TCombobox", fieldbackground=[("readonly", Theme.BG_CARD)],
        selectbackground=[("readonly", Theme.PRIMARY_LIGHT)],
        selectforeground=[("readonly", Theme.TEXT_PRIMARY)])
    style.configure("Vertical.TScrollbar", background="#CBD5E1",
        troughcolor=Theme.BG_MAIN, borderwidth=0, arrowsize=11)
    style.configure("Horizontal.TScrollbar", background="#CBD5E1",
        troughcolor=Theme.BG_MAIN, borderwidth=0, arrowsize=11)
    style.configure("TSeparator", background=Theme.BORDER)
    return style
