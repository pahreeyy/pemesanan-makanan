# views/login_view.py
# The application entry screen — role selection (Kasir / Admin).

from __future__ import annotations
import customtkinter as ctk
from typing import Callable
from views import theme as th


class LoginView(ctk.CTkFrame):
    """
    Entry screen presented at application startup.

    The user selects their role (Kasir or Admin/Manajer) to proceed
    to the appropriate dashboard.  No password is required in this
    prototype — authentication can be added later.

    Attributes:
        on_login (Callable[[str], None]): Callback invoked with the chosen
                                          role string ("kasir" or "admin").
    """

    def __init__(self, parent, on_login: Callable[[str], None]) -> None:
        super().__init__(parent, fg_color=th.BG_DARKEST)
        self.on_login = on_login
        self._build_ui()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.pack(fill="both", expand=True)

        # ── Center column ────────────────────────────────────────────
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / restaurant name
        ctk.CTkLabel(
            center,
            text="🍽️",
            font=(th.FONT_FAMILY, 56),
        ).pack(pady=(0, th.PAD_SM))

        ctk.CTkLabel(
            center,
            text="RESTO POS",
            font=th.FONT_HEADING_XL,
            text_color=th.ACCENT_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            center,
            text="Sistem Informasi Point of Sales & Manajemen Pemesanan",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
        ).pack(pady=(0, th.PAD_XL))

        # Role selection prompt
        ctk.CTkLabel(
            center,
            text="Pilih Peran Anda",
            font=th.FONT_HEADING_MD,
            text_color=th.TEXT_PRIMARY,
        ).pack(pady=(0, th.PAD_MD))

        # ── Kasir button ─────────────────────────────────────────────
        ctk.CTkButton(
            center,
            text="🖥️   Masuk sebagai Kasir",
            command=lambda: self.on_login("kasir"),
            **th.btn_primary(width=320, height=52, font=(th.FONT_FAMILY, 15, "bold")),
        ).pack(pady=(0, th.PAD_SM))

        # ── Admin button ─────────────────────────────────────────────
        ctk.CTkButton(
            center,
            text="⚙️   Masuk sebagai Admin / Manajer",
            command=lambda: self.on_login("admin"),
            **th.btn_ghost(width=320, height=52, font=(th.FONT_FAMILY, 15, "bold")),
        ).pack()

        # Footer
        ctk.CTkLabel(
            center,
            text="v1.0.0  •  © 2026 Resto POS",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_DISABLED,
        ).pack(pady=(th.PAD_XL, 0))
