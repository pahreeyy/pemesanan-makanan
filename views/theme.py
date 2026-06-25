# views/theme.py
# Centralized design tokens for the entire application UI.
# All colors, fonts, sizes, and spacing are defined here so that
# changes to the visual design only need to be made in one place.

import customtkinter as ctk

# ── Appearance ──────────────────────────────────────────────────────────────
APP_THEME   = "dark"          # "dark" | "light" | "system"
COLOR_THEME = "blue"          # CustomTkinter built-in theme

# ── Color Palette (Dark Mode) ───────────────────────────────────────────────
# Background layers
BG_DARKEST   = "#0D1117"   # Outermost background / root window
BG_DARK      = "#161B22"   # Primary panel / frame background
BG_MEDIUM    = "#21262D"   # Card / widget background
BG_LIGHT     = "#30363D"   # Hover / active states

# Accent colors
ACCENT_PRIMARY    = "#F97316"   # Warm orange — brand / call-to-action
ACCENT_PRIMARY_HV = "#EA6B0C"   # Darker orange for hover state
ACCENT_SECONDARY  = "#3B82F6"   # Cool blue — secondary actions
ACCENT_SUCCESS    = "#22C55E"   # Green — confirmations / paid status
ACCENT_DANGER     = "#EF4444"   # Red — delete / error states
ACCENT_WARNING    = "#EAB308"   # Yellow — warnings

# Text
TEXT_PRIMARY   = "#F0F6FC"   # Main readable text
TEXT_SECONDARY = "#8B949E"   # Muted / caption text
TEXT_DISABLED  = "#484F58"   # Placeholder / disabled fields

# Sidebar
SIDEBAR_BG      = "#0D1117"
SIDEBAR_WIDTH   = 220

# ── Typography ──────────────────────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI"          # Falls back gracefully on Windows

FONT_HEADING_XL = (FONT_FAMILY, 28, "bold")
FONT_HEADING_LG = (FONT_FAMILY, 20, "bold")
FONT_HEADING_MD = (FONT_FAMILY, 16, "bold")
FONT_BODY       = (FONT_FAMILY, 13)
FONT_BODY_SM    = (FONT_FAMILY, 11)
FONT_LABEL      = (FONT_FAMILY, 12, "bold")
FONT_MONO       = ("Consolas", 11)   # Receipt / ID displays

# ── Spacing ─────────────────────────────────────────────────────────────────
PAD_XS  = 4
PAD_SM  = 8
PAD_MD  = 16
PAD_LG  = 24
PAD_XL  = 40

# ── Corner Radii ────────────────────────────────────────────────────────────
RADIUS_SM  = 6
RADIUS_MD  = 10
RADIUS_LG  = 16

# ── Widget defaults (passed to CTk constructors) ─────────────────────────────

def frame_defaults(bg: str = BG_MEDIUM) -> dict:
    return {"fg_color": bg, "corner_radius": RADIUS_MD}


def card_defaults() -> dict:
    return {"fg_color": BG_MEDIUM, "corner_radius": RADIUS_LG}


def btn_primary(**extra) -> dict:
    defaults = {
        "fg_color": ACCENT_PRIMARY,
        "hover_color": ACCENT_PRIMARY_HV,
        "text_color": "#FFFFFF",
        "font": FONT_LABEL,
        "corner_radius": RADIUS_MD,
        "height": 38,
    }
    defaults.update(extra)
    return defaults


def btn_secondary(**extra) -> dict:
    defaults = {
        "fg_color": ACCENT_SECONDARY,
        "hover_color": "#2563EB",
        "text_color": "#FFFFFF",
        "font": FONT_LABEL,
        "corner_radius": RADIUS_MD,
        "height": 38,
    }
    defaults.update(extra)
    return defaults


def btn_danger(**extra) -> dict:
    defaults = {
        "fg_color": ACCENT_DANGER,
        "hover_color": "#DC2626",
        "text_color": "#FFFFFF",
        "font": FONT_LABEL,
        "corner_radius": RADIUS_MD,
        "height": 38,
    }
    defaults.update(extra)
    return defaults


def btn_ghost(**extra) -> dict:
    defaults = {
        "fg_color": "transparent",
        "hover_color": BG_LIGHT,
        "text_color": TEXT_PRIMARY,
        "font": FONT_BODY,
        "corner_radius": RADIUS_MD,
        "height": 38,
        "border_width": 1,
        "border_color": BG_LIGHT,
    }
    defaults.update(extra)
    return defaults


def entry_defaults(**extra) -> dict:
    defaults = {
        "fg_color": BG_DARK,
        "border_color": BG_LIGHT,
        "text_color": TEXT_PRIMARY,
        "placeholder_text_color": TEXT_DISABLED,
        "font": FONT_BODY,
        "corner_radius": RADIUS_MD,
        "height": 38,
        "border_width": 1,
    }
    defaults.update(extra)
    return defaults


def apply_theme() -> None:
    """Initialize CustomTkinter appearance settings. Call once at startup."""
    ctk.set_appearance_mode(APP_THEME)
    ctk.set_default_color_theme(COLOR_THEME)
