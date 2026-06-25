# views/components.py
# Reusable CTk widget components shared across multiple views.
# Keeps individual view files focused on layout and business logic only.

from __future__ import annotations
import customtkinter as ctk
from typing import Callable, Optional
from views import theme as th


# ── Stat Card ───────────────────────────────────────────────────────────────

class StatCard(ctk.CTkFrame):
    """
    A summary metric card used in dashboard headers.

    Displays a label, a large numeric value, and an optional icon emoji.

    Args:
        parent      : The parent widget.
        label (str) : Caption text beneath the value.
        value (str) : The primary metric value to display.
        icon  (str) : Optional emoji/symbol prefix (default "📊").
        accent(str) : Accent color for the icon row (default ACCENT_PRIMARY).
    """

    def __init__(
        self,
        parent,
        label: str,
        value: str,
        icon: str = "📊",
        accent: str = th.ACCENT_PRIMARY,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", th.BG_MEDIUM)
        kwargs.setdefault("corner_radius", th.RADIUS_LG)
        super().__init__(parent, **kwargs)

        self._icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=(th.FONT_FAMILY, 22),
            text_color=accent,
        )
        self._icon_label.pack(anchor="w", padx=th.PAD_MD, pady=(th.PAD_MD, 0))

        self._value_label = ctk.CTkLabel(
            self,
            text=value,
            font=th.FONT_HEADING_LG,
            text_color=th.TEXT_PRIMARY,
        )
        self._value_label.pack(anchor="w", padx=th.PAD_MD)

        self._caption = ctk.CTkLabel(
            self,
            text=label,
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
        )
        self._caption.pack(anchor="w", padx=th.PAD_MD, pady=(0, th.PAD_MD))

    def update_value(self, new_value: str) -> None:
        """Dynamically update the displayed metric value."""
        self._value_label.configure(text=new_value)


# ── Section Header ───────────────────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    """
    A styled section title bar with an optional action button.

    Args:
        parent          : Parent widget.
        title    (str)  : Section heading text.
        btn_text (str)  : Label for the optional right-aligned button.
        btn_cmd  (callable): Callback for the optional button.
        accent   (str)  : Left-border accent color.
    """

    def __init__(
        self,
        parent,
        title: str,
        btn_text: Optional[str] = None,
        btn_cmd: Optional[Callable] = None,
        accent: str = th.ACCENT_PRIMARY,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)

        # Left accent strip + title
        accent_bar = ctk.CTkFrame(self, fg_color=accent, width=4, corner_radius=2)
        accent_bar.grid(row=0, column=0, sticky="ns", padx=(0, th.PAD_SM), pady=4)

        title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=th.FONT_HEADING_MD,
            text_color=th.TEXT_PRIMARY,
        )
        title_lbl.grid(row=0, column=0, sticky="w", padx=(th.PAD_SM + 4, 0))

        if btn_text and btn_cmd:
            action_btn = ctk.CTkButton(
                self,
                text=btn_text,
                command=btn_cmd,
                **th.btn_primary(height=32, width=140),
            )
            action_btn.grid(row=0, column=1, sticky="e", padx=th.PAD_SM)

        self.grid_columnconfigure(1, weight=0)


# ── Menu Item Card (Kasir order panel) ──────────────────────────────────────

class MenuItemCard(ctk.CTkFrame):
    """
    A clickable card representing a single menu item in the catalog grid.

    Displays the menu name, category badge, and price.
    Triggers on_click(menu_obj) when pressed.

    Args:
        parent     : Parent widget.
        menu_obj   : The Menu domain object to represent.
        on_click   : Callback receiving the Menu object when the card is clicked.
    """

    def __init__(self, parent, menu_obj, on_click: Callable, **kwargs) -> None:
        kwargs.setdefault("fg_color", th.BG_DARK)
        kwargs.setdefault("corner_radius", th.RADIUS_MD)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", th.BG_LIGHT)
        super().__init__(parent, **kwargs)

        self._menu = menu_obj
        self._on_click = on_click

        # ── Category badge ─────────────────────────────────────────────
        cat_colors = {
            "Makanan":  th.ACCENT_PRIMARY,
            "Minuman":  th.ACCENT_SECONDARY,
            "Dessert":  "#A855F7",
        }
        badge_color = cat_colors.get(menu_obj.kategori, th.BG_LIGHT)
        badge = ctk.CTkLabel(
            self,
            text=f"  {menu_obj.kategori}  ",
            font=th.FONT_BODY_SM,
            fg_color=badge_color,
            corner_radius=4,
            text_color="#FFFFFF",
        )
        badge.pack(anchor="w", padx=th.PAD_SM, pady=(th.PAD_SM, 2))

        # ── Menu name ──────────────────────────────────────────────────
        name_lbl = ctk.CTkLabel(
            self,
            text=menu_obj.nama_menu,
            font=th.FONT_LABEL,
            text_color=th.TEXT_PRIMARY,
            wraplength=160,
            justify="left",
        )
        name_lbl.pack(anchor="w", padx=th.PAD_SM)

        # ── Price ──────────────────────────────────────────────────────
        price_lbl = ctk.CTkLabel(
            self,
            text=f"Rp {menu_obj.harga:,.0f}",
            font=(th.FONT_FAMILY, 13, "bold"),
            text_color=th.ACCENT_PRIMARY,
        )
        price_lbl.pack(anchor="w", padx=th.PAD_SM, pady=(2, th.PAD_SM))

        # ── Availability overlay ───────────────────────────────────────
        if not menu_obj.tersedia:
            unavail = ctk.CTkLabel(
                self,
                text="Tidak Tersedia",
                font=th.FONT_BODY_SM,
                text_color=th.TEXT_DISABLED,
            )
            unavail.pack()

        # Bind click to all child widgets
        self._bind_all_children(self)

    def _bind_all_children(self, widget) -> None:
        widget.bind("<Button-1>", self._handle_click)
        widget.bind("<Enter>", lambda e: self.configure(fg_color=th.BG_LIGHT))
        widget.bind("<Leave>", lambda e: self.configure(fg_color=th.BG_DARK))
        for child in widget.winfo_children():
            self._bind_all_children(child)

    def _handle_click(self, event) -> None:
        if self._menu.tersedia:
            self._on_click(self._menu)


# ── Order Line Row (Keranjang display) ──────────────────────────────────────

class OrderLineRow(ctk.CTkFrame):
    """
    One row in the order-summary panel inside DashboardKasirView.

    Shows: item name | qty spinner | subtotal | delete button.

    Args:
        parent       : Parent frame.
        item         : ItemPesanan domain object.
        on_qty_change: Callback(id_produk, new_qty) to update Keranjang.
        on_delete    : Callback(id_produk) to remove the item.
    """

    def __init__(
        self,
        parent,
        item,
        on_qty_change: Callable,
        on_delete: Callable,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", th.BG_DARK)
        kwargs.setdefault("corner_radius", th.RADIUS_SM)
        super().__init__(parent, **kwargs)

        from models.menu import Menu
        from models.paket import Paket
        self._item = item
        self._on_qty_change = on_qty_change
        self._on_delete = on_delete

        produk = item.produk
        id_produk = produk.id_menu if isinstance(produk, Menu) else produk.id_paket

        self.columnconfigure(0, weight=1)

        # Name
        ctk.CTkLabel(
            self,
            text=item.nama_produk,
            font=th.FONT_BODY,
            text_color=th.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=th.PAD_SM, pady=th.PAD_XS)

        # Qty controls
        qty_frame = ctk.CTkFrame(self, fg_color="transparent")
        qty_frame.grid(row=0, column=1, padx=th.PAD_XS)

        minus_btn = ctk.CTkButton(
            qty_frame,
            text="−",
            width=28,
            height=28,
            fg_color=th.BG_LIGHT,
            hover_color=th.ACCENT_DANGER,
            text_color=th.TEXT_PRIMARY,
            corner_radius=6,
            command=lambda: on_qty_change(id_produk, item.jumlah - 1),
        )
        minus_btn.pack(side="left")

        self._qty_lbl = ctk.CTkLabel(
            qty_frame,
            text=str(item.jumlah),
            width=30,
            font=th.FONT_LABEL,
            text_color=th.TEXT_PRIMARY,
        )
        self._qty_lbl.pack(side="left")

        plus_btn = ctk.CTkButton(
            qty_frame,
            text="+",
            width=28,
            height=28,
            fg_color=th.BG_LIGHT,
            hover_color=th.ACCENT_SUCCESS,
            text_color=th.TEXT_PRIMARY,
            corner_radius=6,
            command=lambda: on_qty_change(id_produk, item.jumlah + 1),
        )
        plus_btn.pack(side="left")

        # Subtotal
        ctk.CTkLabel(
            self,
            text=f"Rp{item.hitung_sub_total():>10,.0f}",
            font=th.FONT_LABEL,
            text_color=th.ACCENT_PRIMARY,
            width=110,
        ).grid(row=0, column=2, padx=th.PAD_SM)

        # Delete
        ctk.CTkButton(
            self,
            text="✕",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=th.ACCENT_DANGER,
            text_color=th.ACCENT_DANGER,
            corner_radius=6,
            command=lambda: on_delete(id_produk),
        ).grid(row=0, column=3, padx=(0, th.PAD_SM))


# ── Toast Notification ───────────────────────────────────────────────────────

class Toast(ctk.CTkFrame):
    """
    A brief, auto-dismissing notification that appears at the bottom of the
    screen and fades after a configurable duration.

    Args:
        parent      : The root window or a top-level container.
        message     : The text to display.
        kind        : "success" | "error" | "info"
        duration_ms : How long (ms) to display before auto-destroy.
    """

    def __init__(
        self,
        parent,
        message: str,
        kind: str = "info",
        duration_ms: int = 2800,
    ) -> None:
        color_map = {
            "success": th.ACCENT_SUCCESS,
            "error":   th.ACCENT_DANGER,
            "info":    th.ACCENT_SECONDARY,
        }
        icon_map = {
            "success": "✓",
            "error":   "✗",
            "info":    "ℹ",
        }
        bg = color_map.get(kind, th.ACCENT_SECONDARY)
        icon = icon_map.get(kind, "ℹ")

        super().__init__(parent, fg_color=bg, corner_radius=th.RADIUS_MD)

        ctk.CTkLabel(
            self,
            text=f"  {icon}  {message}  ",
            font=th.FONT_BODY,
            text_color="#FFFFFF",
        ).pack(padx=th.PAD_MD, pady=th.PAD_SM)

        self.place(relx=0.5, rely=0.96, anchor="s")
        self.after(duration_ms, self.destroy)
