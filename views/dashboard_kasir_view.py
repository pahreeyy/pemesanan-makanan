# views/dashboard_kasir_view.py
# The Kasir (cashier) dashboard — the primary POS order-entry screen.
#
# Layout:
#   ┌─────────────────────────────────────────────────────────────┐
#   │  Topbar: App name  |  Pelanggan info fields  |  Back btn    │
#   ├──────────────────────────────┬──────────────────────────────┤
#   │  LEFT: Menu catalog grid     │  RIGHT: Order summary        │
#   │   ─ Category filter tabs     │   ─ Customer info recap      │
#   │   ─ Scrollable card grid     │   ─ Cart items (scrollable)  │
#   │                              │   ─ Total & payment section  │
#   └──────────────────────────────┴──────────────────────────────┘

from __future__ import annotations
import customtkinter as ctk
from typing import Callable, Optional

from views import theme as th
from views.components import MenuItemCard, OrderLineRow, Toast

from data_handlers.menu_handler import MenuHandler
from data_handlers.paket_handler import PaketHandler
from data_handlers.transaksi_handler import TransaksiHandler

from models.pelanggan import Pelanggan
from models.keranjang import Keranjang
from models.item_pesanan import ItemPesanan
from models.transaksi import Transaksi, MetodePembayaran
from models.nota_pesanan import NotaPesanan

import os

# Paths to JSON data files
_DATA_DIR        = os.path.join(os.path.dirname(__file__), "..", "data")
_MENU_FILE       = os.path.join(_DATA_DIR, "menu.json")
_PAKET_FILE      = os.path.join(_DATA_DIR, "paket.json")
_TRANSAKSI_FILE  = os.path.join(_DATA_DIR, "transaksi.json")


class DashboardKasirView(ctk.CTkFrame):
    """
    Full POS order-entry dashboard for the Kasir role.

    Responsibilities:
    - Display menu catalog in a scrollable, filterable grid.
    - Maintain an active Keranjang (shopping cart) for the current order.
    - Accept customer name and table number.
    - Process payment (Tunai / Non-Tunai) and persist Transaksi to JSON.
    - Display receipt (NotaPesanan) in a modal dialog.
    """

    def __init__(self, parent, on_logout: Callable) -> None:
        super().__init__(parent, fg_color=th.BG_DARKEST)
        self.on_logout = on_logout

        # ── Data handlers ─────────────────────────────────────────────
        self._menu_handler       = MenuHandler(os.path.abspath(_MENU_FILE))
        self._paket_handler      = PaketHandler(os.path.abspath(_PAKET_FILE))
        self._transaksi_handler  = TransaksiHandler(os.path.abspath(_TRANSAKSI_FILE))

        # ── Session state ─────────────────────────────────────────────
        self._keranjang: Keranjang = Keranjang()
        self._selected_kategori: str = "Semua"
        self._all_menus = self._menu_handler.baca_semua()
        self._all_pakets = self._paket_handler.baca_semua()
        self._kategori_list: list[str] = ["Semua"] + self._menu_handler.baca_kategori_unik()
        if self._all_pakets:
            self._kategori_list.append("Paket")

        self._build_ui()

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        self.pack(fill="both", expand=True)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()

        # Main body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=th.PAD_MD, pady=(0, th.PAD_MD))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        self._build_menu_panel(body)
        self._build_order_panel(body)

    # ── Top bar ──────────────────────────────────────────────────────

    def _build_topbar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=th.BG_DARK, height=64, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        # Brand
        ctk.CTkLabel(
            bar,
            text="🍽️  RESTO POS  |  Kasir",
            font=th.FONT_HEADING_MD,
            text_color=th.ACCENT_PRIMARY,
        ).grid(row=0, column=0, padx=th.PAD_LG, pady=th.PAD_MD)

        # Customer info in topbar
        info_frame = ctk.CTkFrame(bar, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=th.PAD_MD)

        ctk.CTkLabel(info_frame, text="Nama Pelanggan:", font=th.FONT_BODY_SM,
                     text_color=th.TEXT_SECONDARY).grid(row=0, column=0, padx=(0, 4))
        self._nama_entry = ctk.CTkEntry(info_frame, placeholder_text="e.g. Budi",
                                        **th.entry_defaults(width=160))
        self._nama_entry.grid(row=0, column=1, padx=(0, th.PAD_MD))

        ctk.CTkLabel(info_frame, text="No. Meja:", font=th.FONT_BODY_SM,
                     text_color=th.TEXT_SECONDARY).grid(row=0, column=2, padx=(0, 4))
        self._meja_entry = ctk.CTkEntry(info_frame, placeholder_text="1",
                                        **th.entry_defaults(width=60))
        self._meja_entry.grid(row=0, column=3)

        # Back button
        ctk.CTkButton(
            bar,
            text="← Keluar",
            command=self._handle_logout,
            **th.btn_ghost(width=110, height=36),
        ).grid(row=0, column=2, padx=th.PAD_LG)

    # ── Left: Menu catalog panel ──────────────────────────────────────

    def _build_menu_panel(self, parent) -> None:
        panel = ctk.CTkFrame(parent, **th.frame_defaults(th.BG_DARK))
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, th.PAD_SM))
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        # Category filter row
        cat_bar = ctk.CTkFrame(panel, fg_color="transparent")
        cat_bar.grid(row=0, column=0, sticky="ew", padx=th.PAD_MD, pady=th.PAD_SM)

        self._cat_buttons: dict[str, ctk.CTkButton] = {}
        for kat in self._kategori_list:
            btn = ctk.CTkButton(
                cat_bar,
                text=kat,
                command=lambda k=kat: self._filter_kategori(k),
                height=32,
                corner_radius=th.RADIUS_SM,
                fg_color=th.ACCENT_PRIMARY if kat == "Semua" else th.BG_MEDIUM,
                hover_color=th.ACCENT_PRIMARY_HV,
                text_color=th.TEXT_PRIMARY,
                font=th.FONT_BODY_SM,
            )
            btn.pack(side="left", padx=2)
            self._cat_buttons[kat] = btn

        # Scrollable menu grid
        self._menu_scroll = ctk.CTkScrollableFrame(
            panel, fg_color="transparent", scrollbar_button_color=th.BG_LIGHT
        )
        self._menu_scroll.grid(row=1, column=0, sticky="nsew",
                                padx=th.PAD_SM, pady=(0, th.PAD_SM))
        self._render_menu_grid()

    def _render_menu_grid(self) -> None:
        """Re-render the menu card grid according to the active category filter."""
        for w in self._menu_scroll.winfo_children():
            w.destroy()

        if self._selected_kategori == "Semua":
            menus_to_show = self._all_menus
            pakets_to_show = self._all_pakets
        elif self._selected_kategori == "Paket":
            menus_to_show = []
            pakets_to_show = self._all_pakets
        else:
            menus_to_show = [m for m in self._all_menus if m.kategori == self._selected_kategori]
            pakets_to_show = []

        COLS = 3
        col = 0
        row = 0

        for menu in menus_to_show:
            card = MenuItemCard(
                self._menu_scroll,
                menu_obj=menu,
                on_click=self._tambah_menu_ke_keranjang,
                width=170, height=110,
            )
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self._menu_scroll.columnconfigure(col, weight=1)
            col += 1
            if col >= COLS:
                col = 0
                row += 1

        # Paket cards
        for paket in pakets_to_show:
            card = ctk.CTkFrame(
                self._menu_scroll,
                fg_color=th.BG_DARK,
                corner_radius=th.RADIUS_MD,
                border_width=1,
                border_color=th.BG_LIGHT,
                width=170,
                height=110,
            )
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self._menu_scroll.columnconfigure(col, weight=1)

            ctk.CTkLabel(card, text="  Paket  ", font=th.FONT_BODY_SM,
                         fg_color="#A855F7", corner_radius=4,
                         text_color="#FFFFFF").pack(anchor="w", padx=th.PAD_SM,
                                                   pady=(th.PAD_SM, 2))
            ctk.CTkLabel(card, text=paket.nama_paket, font=th.FONT_LABEL,
                         text_color=th.TEXT_PRIMARY, wraplength=155, justify="left"
                         ).pack(anchor="w", padx=th.PAD_SM)
            ctk.CTkLabel(card, text=f"Rp {paket.harga_paket:,.0f}",
                         font=(th.FONT_FAMILY, 13, "bold"),
                         text_color=th.ACCENT_PRIMARY,
                         ).pack(anchor="w", padx=th.PAD_SM, pady=(2, th.PAD_SM))

            card.bind("<Button-1>", lambda e, p=paket: self._tambah_paket_ke_keranjang(p))
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=th.BG_LIGHT))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=th.BG_DARK))

            col += 1
            if col >= COLS:
                col = 0
                row += 1

    def _filter_kategori(self, kategori: str) -> None:
        self._selected_kategori = kategori
        for k, btn in self._cat_buttons.items():
            btn.configure(fg_color=th.ACCENT_PRIMARY if k == kategori else th.BG_MEDIUM)
        self._render_menu_grid()

    # ── Right: Order summary panel ────────────────────────────────────

    def _build_order_panel(self, parent) -> None:
        panel = ctk.CTkFrame(parent, **th.frame_defaults(th.BG_DARK))
        panel.grid(row=0, column=1, sticky="nsew")
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(
            panel,
            text="🛒  Pesanan Aktif",
            font=th.FONT_HEADING_MD,
            text_color=th.TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", padx=th.PAD_MD, pady=th.PAD_MD)

        # Clear cart button
        ctk.CTkButton(
            panel,
            text="Kosongkan",
            command=self._kosongkan_keranjang,
            **th.btn_ghost(width=110, height=30),
        ).grid(row=0, column=1, padx=th.PAD_MD)

        # Scrollable cart items
        self._cart_scroll = ctk.CTkScrollableFrame(
            panel, fg_color="transparent", scrollbar_button_color=th.BG_LIGHT
        )
        self._cart_scroll.grid(row=1, column=0, columnspan=2, sticky="nsew",
                                padx=th.PAD_SM, pady=(0, th.PAD_SM))
        self._cart_scroll.columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._cart_scroll,
            text="Belum ada item.\nKlik menu di kiri untuk menambahkan.",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_DISABLED,
            justify="center",
        )
        self._empty_label.pack(pady=th.PAD_XL)

        # ── Payment section ───────────────────────────────────────────
        pay_frame = ctk.CTkFrame(panel, fg_color=th.BG_MEDIUM, corner_radius=th.RADIUS_MD)
        pay_frame.grid(row=2, column=0, columnspan=2, sticky="ew",
                       padx=th.PAD_SM, pady=(0, th.PAD_SM))
        pay_frame.columnconfigure(1, weight=1)

        # Divider
        ctk.CTkFrame(pay_frame, height=1, fg_color=th.BG_LIGHT).pack(
            fill="x", padx=th.PAD_SM, pady=(th.PAD_SM, 0))

        # Total
        total_row = ctk.CTkFrame(pay_frame, fg_color="transparent")
        total_row.pack(fill="x", padx=th.PAD_MD, pady=th.PAD_SM)
        ctk.CTkLabel(total_row, text="TOTAL", font=th.FONT_HEADING_MD,
                     text_color=th.TEXT_SECONDARY).pack(side="left")
        self._total_label = ctk.CTkLabel(
            total_row, text="Rp 0",
            font=(th.FONT_FAMILY, 22, "bold"),
            text_color=th.ACCENT_PRIMARY,
        )
        self._total_label.pack(side="right")

        # Payment method
        method_row = ctk.CTkFrame(pay_frame, fg_color="transparent")
        method_row.pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_SM))
        ctk.CTkLabel(method_row, text="Metode:", font=th.FONT_BODY_SM,
                     text_color=th.TEXT_SECONDARY).pack(side="left", padx=(0, th.PAD_SM))
        self._metode_var = ctk.StringVar(value="Tunai")
        self._metode_menu = ctk.CTkOptionMenu(
            method_row,
            variable=self._metode_var,
            values=["Tunai", "Non-Tunai"],
            fg_color=th.BG_LIGHT,
            button_color=th.BG_LIGHT,
            button_hover_color=th.ACCENT_PRIMARY,
            text_color=th.TEXT_PRIMARY,
            font=th.FONT_BODY,
            command=self._on_metode_changed,
        )
        self._metode_menu.pack(side="left")

        # Cash tendered (visible only for Tunai)
        self._bayar_frame = ctk.CTkFrame(pay_frame, fg_color="transparent")
        self._bayar_frame.pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_SM))
        ctk.CTkLabel(self._bayar_frame, text="Jumlah Bayar (Rp):",
                     font=th.FONT_BODY_SM, text_color=th.TEXT_SECONDARY).pack(side="left")
        self._bayar_entry = ctk.CTkEntry(
            self._bayar_frame, placeholder_text="Masukkan nominal",
            **th.entry_defaults(width=170),
        )
        self._bayar_entry.pack(side="left", padx=(th.PAD_SM, 0))

        # QR placeholder for non-cash payment
        self._qr_frame = ctk.CTkFrame(
            pay_frame,
            fg_color=th.BG_LIGHT,
            corner_radius=th.RADIUS_MD,
            border_width=1,
            border_color=th.BG_MEDIUM,
        )
        self._qr_frame.pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_SM))
        self._qr_frame.pack_forget()

        ctk.CTkLabel(
            self._qr_frame,
            text="Scan QRIS Pembayaran",
            font=(th.FONT_FAMILY, 13, "bold"),
            text_color=th.TEXT_PRIMARY,
        ).pack(pady=(th.PAD_MD, th.PAD_SM))

        qr_canvas = ctk.CTkFrame(self._qr_frame, fg_color="white", corner_radius=8)
        qr_canvas.pack(padx=th.PAD_MD, pady=(0, th.PAD_SM))

        qr_matrix = [
            "1111111000000",
            "1000000111111",
            "1011111010101",
            "1011111010101",
            "1011111010101",
            "1000000010101",
            "1111111010101",
            "1000011101010",
            "1011101010101",
            "1010011010101",
            "1011111010101",
            "1111111111111",
            "0000000000000",
        ]

        for row in qr_matrix:
            row_frame = ctk.CTkFrame(qr_canvas, fg_color="white")
            row_frame.pack(anchor="center")
            for cell in row:
                color = "#000000" if cell == "1" else "#ffffff"
                ctk.CTkFrame(
                    row_frame,
                    width=8,
                    height=8,
                    fg_color=color,
                    corner_radius=0,
                    border_width=0,
                ).pack(side="left")

        self._qr_total_label = ctk.CTkLabel(
            self._qr_frame,
            text="Total: Rp 0\nID: PAY-001",
            font=(th.FONT_FAMILY, 11),
            text_color=th.TEXT_SECONDARY,
        )
        self._qr_total_label.pack(pady=(0, th.PAD_MD))

        # Process button
        ctk.CTkButton(
            pay_frame,
            text="💳  Proses Pembayaran",
            command=self._proses_pembayaran,
            **th.btn_primary(height=46, font=(th.FONT_FAMILY, 15, "bold")),
        ).pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_MD))

    # ==================================================================
    # Cart Logic
    # ==================================================================

    def _tambah_menu_ke_keranjang(self, menu) -> None:
        item = ItemPesanan(produk=menu, jumlah=1)
        self._keranjang.tambah_item(item)
        self._refresh_cart()
        Toast(self, f"+ {menu.nama_menu} ditambahkan", kind="success")

    def _tambah_paket_ke_keranjang(self, paket) -> None:
        item = ItemPesanan(produk=paket, jumlah=1)
        self._keranjang.tambah_item(item)
        self._refresh_cart()
        Toast(self, f"+ {paket.nama_paket} ditambahkan", kind="success")

    def _ubah_jumlah(self, id_produk: str, new_qty: int) -> None:
        if new_qty < 1:
            self._hapus_item(id_produk)
            return
        self._keranjang.ubah_jumlah(id_produk, new_qty)
        self._refresh_cart()

    def _hapus_item(self, id_produk: str) -> None:
        self._keranjang.hapus_item(id_produk)
        self._refresh_cart()

    def _kosongkan_keranjang(self) -> None:
        self._keranjang.kosongkan()
        self._refresh_cart()

    def _refresh_cart(self) -> None:
        """Re-render all order line rows and update the total label."""
        for w in self._cart_scroll.winfo_children():
            w.destroy()

        items = self._keranjang.items
        if not items:
            self._empty_label = ctk.CTkLabel(
                self._cart_scroll,
                text="Belum ada item.\nKlik menu di kiri untuk menambahkan.",
                font=th.FONT_BODY_SM,
                text_color=th.TEXT_DISABLED,
                justify="center",
            )
            self._empty_label.pack(pady=th.PAD_XL)
        else:
            for item in items:
                row = OrderLineRow(
                    self._cart_scroll,
                    item=item,
                    on_qty_change=self._ubah_jumlah,
                    on_delete=self._hapus_item,
                )
                row.pack(fill="x", padx=th.PAD_XS, pady=2)

        total = self._keranjang.hitung_total()
        self._total_label.configure(text=f"Rp {total:,.0f}")
        if hasattr(self, "_qr_total_label"):
            self._qr_total_label.configure(text=f"Total: Rp {total:,.0f}\nID: PAY-001")

    # ==================================================================
    # Payment
    # ==================================================================

    def _on_metode_changed(self, value: str) -> None:
        if value == "Non-Tunai":
            self._bayar_frame.pack_forget()
            self._qr_frame.pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_SM))
        else:
            self._bayar_frame.pack(fill="x", padx=th.PAD_MD, pady=(0, th.PAD_SM),
                                    before=self._metode_menu.master.master)
            self._qr_frame.pack_forget()

    def _proses_pembayaran(self) -> None:
        """Validate inputs, process the transaction, and show the receipt."""
        # Validation
        if self._keranjang.is_kosong():
            Toast(self, "Keranjang masih kosong!", kind="error")
            return

        nama = self._nama_entry.get().strip() or "Tamu"
        try:
            meja = int(self._meja_entry.get().strip() or "1")
            if meja < 1:
                raise ValueError
        except ValueError:
            Toast(self, "Nomor meja harus angka positif.", kind="error")
            return

        pelanggan = Pelanggan(nama=nama, nomor_meja=meja)
        metode_str = self._metode_var.get()
        metode = (MetodePembayaran.TUNAI if metode_str == "Tunai"
                  else MetodePembayaran.NON_TUNAI)

        items = self._keranjang.items
        transaksi = Transaksi(pelanggan=pelanggan, items=items, metode_pembayaran=metode)
        total = transaksi.hitung_total()

        if metode == MetodePembayaran.TUNAI:
            try:
                jumlah_bayar = float(self._bayar_entry.get().strip().replace(",", "") or "0")
            except ValueError:
                Toast(self, "Nominal bayar tidak valid.", kind="error")
                return
            try:
                kembalian = transaksi.proses_pembayaran(jumlah_bayar)
            except ValueError as e:
                Toast(self, str(e), kind="error")
                return
        else:
            transaksi.proses_pembayaran(total)

        # Persist
        self._transaksi_handler.tambah(transaksi)

        # Show receipt
        self._tampilkan_nota(transaksi)

        # Reset session
        self._keranjang.kosongkan()
        self._nama_entry.delete(0, "end")
        self._meja_entry.delete(0, "end")
        self._bayar_entry.delete(0, "end")
        self._refresh_cart()

    # ==================================================================
    # Receipt Modal
    # ==================================================================

    def _tampilkan_nota(self, transaksi: Transaksi) -> None:
        """Open a modal dialog displaying the formatted receipt."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Struk Pembayaran")
        dialog.geometry("480x640")
        dialog.configure(fg_color=th.BG_DARK)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="✅  Pembayaran Berhasil!",
            font=th.FONT_HEADING_MD,
            text_color=th.ACCENT_SUCCESS,
        ).pack(pady=th.PAD_MD)

        nota_text = transaksi.cetak_struk()
        receipt_box = ctk.CTkTextbox(
            dialog,
            fg_color=th.BG_DARKEST,
            text_color=th.TEXT_PRIMARY,
            font=th.FONT_MONO,
            corner_radius=th.RADIUS_MD,
        )
        receipt_box.pack(fill="both", expand=True, padx=th.PAD_MD, pady=(0, th.PAD_SM))
        receipt_box.insert("end", nota_text)
        receipt_box.configure(state="disabled")

        ctk.CTkButton(
            dialog,
            text="Tutup",
            command=dialog.destroy,
            **th.btn_primary(width=200),
        ).pack(pady=th.PAD_MD)

    # ==================================================================
    # Navigation
    # ==================================================================

    def _handle_logout(self) -> None:
        self.on_logout()
