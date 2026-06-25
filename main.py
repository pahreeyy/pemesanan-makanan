# main.py
# ─────────────────────────────────────────────────────────────────────────────
# Entry point for the Sistem Informasi POS & Manajemen Pemesanan Restoran.
#
# Responsibilities of this file:
#   1. Apply the global CustomTkinter theme (appearance + color scheme).
#   2. Create and configure the root application window.
#   3. Bootstrap the LoginView as the initial screen.
#   4. Implement the view-navigation router (login → kasir/admin → back).
#   5. Start the Tkinter main event loop.
#
# DO NOT put any business logic or data access here.
# All domain logic lives in /models, /controllers, and /data_handlers.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

# ── Ensure project root is in sys.path ───────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import customtkinter as ctk

from views.theme import apply_theme, BG_DARKEST
from views.login_view import LoginView
from views.dashboard_kasir_view import DashboardKasirView
from views.dashboard_admin_view import DashboardAdminView


# ─────────────────────────────────────────────────────────────────────────────
# Application Root Window
# ─────────────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    """
    The application's root CTk window.

    Acts as the top-level router: it creates and destroys view frames
    in response to user navigation events (login, logout, role selection).

    Attributes:
        _current_view (ctk.CTkFrame | None): The view frame currently displayed.
    """

    # ── Window configuration ──────────────────────────────────────────────────
    WINDOW_TITLE  = "Sistem Informasi POS — Restoran"
    WINDOW_MIN_W  = 1200
    WINDOW_MIN_H  = 700
    WINDOW_START  = "1280x760"

    def __init__(self) -> None:
        super().__init__()

        # Window setup
        self.title(self.WINDOW_TITLE)
        self.geometry(self.WINDOW_START)
        self.minsize(self.WINDOW_MIN_W, self.WINDOW_MIN_H)
        self.configure(fg_color=BG_DARKEST)

        # Center the window on screen at startup
        self._center_window()

        # State
        self._current_view: ctk.CTkFrame | None = None

        # Start at the login screen
        self._show_login()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _clear_view(self) -> None:
        """Destroy the currently displayed view frame, if any."""
        if self._current_view is not None:
            self._current_view.destroy()
            self._current_view = None

    def _show_login(self) -> None:
        """Display the LoginView (role selection screen)."""
        self._clear_view()
        self._current_view = LoginView(self, on_login=self._on_login)

    def _on_login(self, role: str) -> None:
        """
        Router callback triggered when the user selects a role on LoginView.

        Args:
            role (str): "kasir" or "admin"
        """
        self._clear_view()
        if role == "kasir":
            self._current_view = DashboardKasirView(
                self, on_logout=self._show_login
            )
        elif role == "admin":
            self._current_view = DashboardAdminView(
                self, on_logout=self._show_login
            )
        else:
            # Fallback — should never happen
            self._show_login()

    # ── Helper utilities ──────────────────────────────────────────────────────

    def _center_window(self) -> None:
        """Center the application window on the primary display."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Initialize the theme and launch the application."""
    apply_theme()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
