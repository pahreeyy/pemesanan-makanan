# views/dashboard_admin_view.py
# The Admin / Manager dashboard.
#
# Layout (tab-based):
#   ┌──────────────────────────────────────────────────────────────┐
#   │  Topbar: Brand  |  Nav Tabs  |  Back btn                     │
#   ├──────────────────────────────────────────────────────────────┤
#   │  TAB: Katalog Menu (CRUD)                                    │
#   │    - Form: Add / Edit menu item                              │
#   │    - Table: All menu items with Edit & Delete buttons        │
#   ├──────────────────────────────────────────────────────────────┤
#   │  TAB: Laporan Penjualan                                      │
#   │    - Summary stat cards                                      │
#   │    - Date range filter                                       │
#   │    - Top-selling menu table                                  │
#   │    - Transaction history table                               │
#   └──────────────────────────────────────────────────────────────┘

from __future__ import annotations
import uuid
import datetime
import customtkinter as ctk
from typing import Callable, Optional

from views import theme as th
from views.components import StatCard, Toast

from data_handlers.menu_handler import MenuHandler
from data_handlers.transaksi_handler import TransaksiHandler

from models.menu import Menu
from models.laporan_penjualan import LaporanPenjualan

import os

_DATA_DIR       = os.path.join(os.path.dirname(__file__), "..", "data")
_MENU_FILE      = os.path.join(_DATA_DIR, "menu.json")
_TRANSAKSI_FILE = os.path.join(_DATA_DIR, "transaksi.json")


class DashboardAdminView(ctk.CTkFrame):
    """
    Full Admin / Manager dashboard providing:
    - Katalog Menu CRUD (Create, Read, Update, Delete) via menu.json
    - Laporan Penjualan with revenue summary and history from transaksi.json
    """

    def __init__(self, parent, on_logout: Callable) -> None:
        super().__init__(parent, fg_color=th.BG_DARKEST)
        self.on_logout = on_logout

        self._menu_handler      = MenuHandler(os.path.abspath(_MENU_FILE))
        self._transaksi_handler = TransaksiHandler(os.path.abspath(_TRANSAKSI_FILE))

        # Edit state
        self._editing_menu: Optional[Menu] = None

        self._build_ui()

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        self.pack(fill="both", expand=True)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()

        # Tab view
        self._tabs = ctk.CTkTabview(
            self,
            fg_color=th.BG_DARK,
            segmented_button_fg_color=th.BG_DARKEST,
            segmented_button_selected_color=th.ACCENT_PRIMARY,
            segmented_button_selected_hover_color=th.ACCENT_PRIMARY_HV,
            segmented_button_unselected_color=th.BG_DARKEST,
            segmented_button_unselected_hover_color=th.BG_LIGHT,
            text_color=th.TEXT_PRIMARY,
            corner_radius=th.RADIUS_MD,
        )
        self._tabs.grid(row=1, column=0, sticky="nsew",
                        padx=th.PAD_MD, pady=(0, th.PAD_MD))

        self._tabs.add("📋  Katalog Menu")
        self._tabs.add("📊  Laporan Penjualan")

        self._build_tab_katalog(self._tabs.tab("📋  Katalog Menu"))
        self._build_tab_laporan(self._tabs.tab("📊  Laporan Penjualan"))

    # ── Topbar ───────────────────────────────────────────────────────

    def _build_topbar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=th.BG_DARK, height=64, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(
            bar,
            text="🍽️  RESTO POS  |  Admin / Manajer",
            font=th.FONT_HEADING_MD,
            text_color=th.ACCENT_PRIMARY,
        ).grid(row=0, column=0, padx=th.PAD_LG, pady=th.PAD_MD, sticky="w")

        ctk.CTkButton(
            bar,
            text="← Keluar",
            command=self.on_logout,
            **th.btn_ghost(width=110, height=36),
        ).grid(row=0, column=2, padx=th.PAD_LG)

    # ==================================================================
    # TAB 1 — Katalog Menu (CRUD)
    # ==================================================================

    def _build_tab_katalog(self, tab) -> None:
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)

        # ── LEFT: Form panel ──────────────────────────────────────────
        form_panel = ctk.CTkFrame(tab, fg_color=th.BG_MEDIUM,
                                   corner_radius=th.RADIUS_LG, width=320)
        form_panel.grid(row=0, column=0, sticky="nsew",
                        padx=(0, th.PAD_SM), pady=th.PAD_SM)
        form_panel.grid_propagate(False)

        self._form_title_lbl = ctk.CTkLabel(
            form_panel, text="➕  Tambah Menu Baru",
            font=th.FONT_HEADING_MD, text_color=th.TEXT_PRIMARY,
        )
        self._form_title_lbl.pack(anchor="w", padx=th.PAD_MD, pady=th.PAD_MD)

        def lbl(parent, text):
            ctk.CTkLabel(parent, text=text, font=th.FONT_LABEL,
                         text_color=th.TEXT_SECONDARY).pack(anchor="w",
                                                             padx=th.PAD_MD,
                                                             pady=(th.PAD_SM, 2))

        lbl(form_panel, "ID Menu *")
        self._f_id = ctk.CTkEntry(form_panel, placeholder_text="e.g. MKN010",
                                   **th.entry_defaults())
        self._f_id.pack(fill="x", padx=th.PAD_MD)

        lbl(form_panel, "Nama Menu *")
        self._f_nama = ctk.CTkEntry(form_panel, placeholder_text="e.g. Soto Ayam",
                                     **th.entry_defaults())
        self._f_nama.pack(fill="x", padx=th.PAD_MD)

        lbl(form_panel, "Harga (Rp) *")
        self._f_harga = ctk.CTkEntry(form_panel, placeholder_text="e.g. 25000",
                                      **th.entry_defaults())
        self._f_harga.pack(fill="x", padx=th.PAD_MD)

        lbl(form_panel, "Kategori *")
        self._f_kategori = ctk.CTkEntry(form_panel, placeholder_text="e.g. Makanan",
                                         **th.entry_defaults())
        self._f_kategori.pack(fill="x", padx=th.PAD_MD)

        lbl(form_panel, "Tersedia")
        self._f_tersedia_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            form_panel,
            text="Tersedia untuk dipesan",
            variable=self._f_tersedia_var,
            onvalue=True,
            offvalue=False,
            progress_color=th.ACCENT_SUCCESS,
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_PRIMARY,
        ).pack(anchor="w", padx=th.PAD_MD, pady=th.PAD_SM)

        # Form buttons
        btn_row = ctk.CTkFrame(form_panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=th.PAD_MD, pady=th.PAD_MD)

        ctk.CTkButton(
            btn_row, text="Simpan Menu",
            command=self._simpan_menu,
            **th.btn_primary(height=40),
        ).pack(side="left", fill="x", expand=True, padx=(0, th.PAD_XS))

        self._reset_btn = ctk.CTkButton(
            btn_row, text="Reset",
            command=self._reset_form,
            **th.btn_ghost(height=40, width=80),
        )
        self._reset_btn.pack(side="left")

        # ── RIGHT: Menu list table ────────────────────────────────────
        list_panel = ctk.CTkFrame(tab, fg_color=th.BG_MEDIUM, corner_radius=th.RADIUS_LG)
        list_panel.grid(row=0, column=1, sticky="nsew", pady=th.PAD_SM)
        list_panel.rowconfigure(1, weight=1)
        list_panel.columnconfigure(0, weight=1)

        # Table header
        header = ctk.CTkFrame(list_panel, fg_color=th.BG_DARK, corner_radius=th.RADIUS_SM)
        header.grid(row=0, column=0, sticky="ew", padx=th.PAD_SM, pady=th.PAD_SM)
        header.columnconfigure(1, weight=1)

        for col_idx, (txt, w) in enumerate([
            ("ID", 90), ("Nama Menu", 0), ("Kategori", 100),
            ("Harga", 100), ("Status", 80), ("Aksi", 120),
        ]):
            ctk.CTkLabel(
                header, text=txt,
                font=th.FONT_LABEL, text_color=th.TEXT_SECONDARY,
                width=w if w else 0, anchor="w",
            ).grid(row=0, column=col_idx, padx=th.PAD_SM, pady=th.PAD_XS, sticky="w")

        # Scrollable table body
        self._menu_table_frame = ctk.CTkScrollableFrame(
            list_panel, fg_color="transparent", scrollbar_button_color=th.BG_LIGHT
        )
        self._menu_table_frame.grid(row=1, column=0, sticky="nsew",
                                     padx=th.PAD_SM, pady=(0, th.PAD_SM))
        self._menu_table_frame.columnconfigure(1, weight=1)

        self._refresh_menu_table()

    def _refresh_menu_table(self) -> None:
        """Clear and re-render the menu list table."""
        for w in self._menu_table_frame.winfo_children():
            w.destroy()

        menus = self._menu_handler.baca_semua()
        if not menus:
            ctk.CTkLabel(
                self._menu_table_frame,
                text="Belum ada data menu.",
                font=th.FONT_BODY_SM,
                text_color=th.TEXT_DISABLED,
            ).pack(pady=th.PAD_LG)
            return

        for row_idx, menu in enumerate(menus):
            row_bg = th.BG_DARK if row_idx % 2 == 0 else th.BG_MEDIUM
            row_frame = ctk.CTkFrame(
                self._menu_table_frame, fg_color=row_bg, corner_radius=th.RADIUS_SM
            )
            row_frame.pack(fill="x", pady=1)
            row_frame.columnconfigure(1, weight=1)

            # ID
            ctk.CTkLabel(row_frame, text=menu.id_menu, font=th.FONT_MONO,
                         text_color=th.TEXT_SECONDARY, width=90, anchor="w",
                         ).grid(row=0, column=0, padx=th.PAD_SM, pady=th.PAD_XS, sticky="w")
            # Nama
            ctk.CTkLabel(row_frame, text=menu.nama_menu, font=th.FONT_BODY,
                         text_color=th.TEXT_PRIMARY, anchor="w",
                         ).grid(row=0, column=1, padx=th.PAD_SM, sticky="w")
            # Kategori
            ctk.CTkLabel(row_frame, text=menu.kategori, font=th.FONT_BODY_SM,
                         text_color=th.TEXT_SECONDARY, width=100, anchor="w",
                         ).grid(row=0, column=2, padx=th.PAD_SM, sticky="w")
            # Harga
            ctk.CTkLabel(row_frame, text=f"Rp{menu.harga:,.0f}", font=th.FONT_LABEL,
                         text_color=th.ACCENT_PRIMARY, width=100, anchor="e",
                         ).grid(row=0, column=3, padx=th.PAD_SM, sticky="e")
            # Status
            status_color = th.ACCENT_SUCCESS if menu.tersedia else th.ACCENT_DANGER
            status_text  = "✓ Ada" if menu.tersedia else "✗ Habis"
            ctk.CTkLabel(row_frame, text=status_text, font=th.FONT_BODY_SM,
                         text_color=status_color, width=80,
                         ).grid(row=0, column=4, padx=th.PAD_SM)
            # Action buttons
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=5, padx=th.PAD_SM)

            ctk.CTkButton(
                action_frame, text="Edit", width=52, height=28,
                fg_color=th.ACCENT_SECONDARY, hover_color="#2563EB",
                text_color="#FFFFFF", corner_radius=th.RADIUS_SM, font=th.FONT_BODY_SM,
                command=lambda m=menu: self._edit_menu(m),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                action_frame, text="Hapus", width=52, height=28,
                fg_color=th.ACCENT_DANGER, hover_color="#DC2626",
                text_color="#FFFFFF", corner_radius=th.RADIUS_SM, font=th.FONT_BODY_SM,
                command=lambda m=menu: self._hapus_menu(m),
            ).pack(side="left", padx=2)

    # ── CRUD helpers ─────────────────────────────────────────────────

    def _simpan_menu(self) -> None:
        """Create or Update a menu item from form inputs."""
        id_menu   = self._f_id.get().strip()
        nama      = self._f_nama.get().strip()
        harga_str = self._f_harga.get().strip()
        kategori  = self._f_kategori.get().strip()
        tersedia  = self._f_tersedia_var.get()

        # Validation
        if not all([id_menu, nama, harga_str, kategori]):
            Toast(self, "Semua field wajib diisi!", kind="error")
            return
        try:
            harga = float(harga_str.replace(",", ""))
            if harga <= 0:
                raise ValueError
        except ValueError:
            Toast(self, "Harga harus berupa angka positif.", kind="error")
            return

        menu_obj = Menu(id_menu=id_menu, nama_menu=nama, harga=harga,
                        kategori=kategori, tersedia=tersedia)

        if self._editing_menu is not None:
            # UPDATE path
            success = self._menu_handler.perbarui(menu_obj)
            if success:
                Toast(self, f"Menu '{nama}' berhasil diperbarui.", kind="success")
            else:
                Toast(self, "Gagal memperbarui menu.", kind="error")
        else:
            # CREATE path
            try:
                self._menu_handler.tambah(menu_obj)
                Toast(self, f"Menu '{nama}' berhasil ditambahkan.", kind="success")
            except ValueError as e:
                Toast(self, str(e), kind="error")
                return

        self._reset_form()
        self._refresh_menu_table()

    def _edit_menu(self, menu: Menu) -> None:
        """Populate the form with an existing menu item for editing."""
        self._editing_menu = menu
        self._form_title_lbl.configure(text=f"✏️  Edit Menu: {menu.id_menu}")

        # Populate fields
        def _set_entry(entry: ctk.CTkEntry, val: str) -> None:
            entry.delete(0, "end")
            entry.insert(0, val)

        _set_entry(self._f_id,       menu.id_menu)
        _set_entry(self._f_nama,     menu.nama_menu)
        _set_entry(self._f_harga,    str(menu.harga))
        _set_entry(self._f_kategori, menu.kategori)
        self._f_tersedia_var.set(menu.tersedia)
        self._f_id.configure(state="disabled")  # Don't allow ID change on edit

    def _hapus_menu(self, menu: Menu) -> None:
        """Confirm and delete a menu item."""
        dialog = ctk.CTkInputDialog(
            text=f"Ketik 'HAPUS' untuk menghapus\nmenu '{menu.nama_menu}':",
            title="Konfirmasi Hapus",
        )
        confirm = dialog.get_input()
        if confirm and confirm.strip().upper() == "HAPUS":
            success = self._menu_handler.hapus(menu.id_menu)
            if success:
                Toast(self, f"Menu '{menu.nama_menu}' dihapus.", kind="success")
                self._refresh_menu_table()
            else:
                Toast(self, "Gagal menghapus menu.", kind="error")

    def _reset_form(self) -> None:
        """Clear the form and exit edit mode."""
        self._editing_menu = None
        self._form_title_lbl.configure(text="➕  Tambah Menu Baru")
        for entry in [self._f_id, self._f_nama, self._f_harga, self._f_kategori]:
            entry.configure(state="normal")
            entry.delete(0, "end")
        self._f_tersedia_var.set(True)

    # ==================================================================
    # TAB 2 — Laporan Penjualan
    # ==================================================================

    def _build_tab_laporan(self, tab) -> None:
        tab.rowconfigure(2, weight=1)
        tab.columnconfigure(0, weight=1)

        # ── Stat cards row ────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(tab, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(th.PAD_SM, 0))
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)

        self._stat_pendapatan = StatCard(
            cards_frame, label="Total Pendapatan (Hari Ini)",
            value="Rp 0", icon="💰", accent=th.ACCENT_PRIMARY,
        )
        self._stat_pendapatan.grid(row=0, column=0, sticky="ew", padx=th.PAD_SM, pady=th.PAD_SM)

        self._stat_transaksi = StatCard(
            cards_frame, label="Jumlah Transaksi (Hari Ini)",
            value="0", icon="🧾", accent=th.ACCENT_SECONDARY,
        )
        self._stat_transaksi.grid(row=0, column=1, sticky="ew", padx=th.PAD_SM, pady=th.PAD_SM)

        self._stat_rata = StatCard(
            cards_frame, label="Rata-rata Transaksi (Hari Ini)",
            value="Rp 0", icon="📈", accent=th.ACCENT_SUCCESS,
        )
        self._stat_rata.grid(row=0, column=2, sticky="ew", padx=th.PAD_SM, pady=th.PAD_SM)

        # ── Filter bar ────────────────────────────────────────────────
        filter_frame = ctk.CTkFrame(tab, fg_color=th.BG_MEDIUM, corner_radius=th.RADIUS_MD)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=th.PAD_SM, pady=th.PAD_SM)

        ctk.CTkLabel(filter_frame, text="Filter Tanggal:", font=th.FONT_LABEL,
                     text_color=th.TEXT_SECONDARY).pack(side="left", padx=th.PAD_MD)

        today_str = datetime.date.today().strftime("%Y-%m-%d")

        ctk.CTkLabel(filter_frame, text="Dari:", font=th.FONT_BODY_SM,
                     text_color=th.TEXT_SECONDARY).pack(side="left")
        self._dari_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD",
                                         **th.entry_defaults(width=130))
        self._dari_entry.pack(side="left", padx=(4, th.PAD_SM))
        self._dari_entry.insert(0, today_str)

        ctk.CTkLabel(filter_frame, text="Sampai:", font=th.FONT_BODY_SM,
                     text_color=th.TEXT_SECONDARY).pack(side="left")
        self._sampai_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD",
                                           **th.entry_defaults(width=130))
        self._sampai_entry.pack(side="left", padx=(4, th.PAD_SM))
        self._sampai_entry.insert(0, today_str)

        ctk.CTkButton(
            filter_frame, text="🔍  Tampilkan Laporan",
            command=self._refresh_laporan,
            **th.btn_primary(height=36, width=180),
        ).pack(side="left", padx=th.PAD_SM, pady=th.PAD_SM)

        ctk.CTkButton(
            filter_frame, text="Semua Data",
            command=self._laporan_semua,
            **th.btn_ghost(height=36, width=110),
        ).pack(side="left", padx=(0, th.PAD_SM), pady=th.PAD_SM)

        # ── Bottom split: top sellers | transaction history ───────────
        bottom = ctk.CTkFrame(tab, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=th.PAD_SM, pady=(0, th.PAD_SM))
        bottom.rowconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=2)

        # Top sellers
        sellers_panel = ctk.CTkFrame(bottom, fg_color=th.BG_MEDIUM, corner_radius=th.RADIUS_LG)
        sellers_panel.grid(row=0, column=0, sticky="nsew", padx=(0, th.PAD_SM))
        sellers_panel.rowconfigure(1, weight=1)
        sellers_panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(sellers_panel, text="🏆  Menu Terlaris", font=th.FONT_HEADING_MD,
                     text_color=th.TEXT_PRIMARY).grid(row=0, column=0, sticky="w",
                                                       padx=th.PAD_MD, pady=th.PAD_MD)
        self._sellers_frame = ctk.CTkScrollableFrame(
            sellers_panel, fg_color="transparent", scrollbar_button_color=th.BG_LIGHT
        )
        self._sellers_frame.grid(row=1, column=0, sticky="nsew",
                                  padx=th.PAD_SM, pady=(0, th.PAD_SM))
        self._sellers_frame.columnconfigure(0, weight=1)

        # Transaction history
        history_panel = ctk.CTkFrame(bottom, fg_color=th.BG_MEDIUM, corner_radius=th.RADIUS_LG)
        history_panel.grid(row=0, column=1, sticky="nsew")
        history_panel.rowconfigure(1, weight=1)
        history_panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(history_panel, text="🧾  Riwayat Transaksi", font=th.FONT_HEADING_MD,
                     text_color=th.TEXT_PRIMARY).grid(row=0, column=0, sticky="w",
                                                       padx=th.PAD_MD, pady=th.PAD_MD)
        self._history_frame = ctk.CTkScrollableFrame(
            history_panel, fg_color="transparent", scrollbar_button_color=th.BG_LIGHT
        )
        self._history_frame.grid(row=1, column=0, sticky="nsew",
                                  padx=th.PAD_SM, pady=(0, th.PAD_SM))
        self._history_frame.columnconfigure(0, weight=1)

        # Initial load
        self._refresh_laporan()

    # ── Report helpers ────────────────────────────────────────────────

    def _refresh_laporan(self) -> None:
        """Load and display the sales report for the specified date range."""
        try:
            dari_str    = self._dari_entry.get().strip()
            sampai_str  = self._sampai_entry.get().strip()
            dari_date   = datetime.date.fromisoformat(dari_str) if dari_str else None
            sampai_date = datetime.date.fromisoformat(sampai_str) if sampai_str else None
        except ValueError:
            Toast(self, "Format tanggal tidak valid. Gunakan YYYY-MM-DD.", kind="error")
            return

        semua_trx = self._transaksi_handler.baca_semua()
        laporan = LaporanPenjualan(semua_trx, dari_date, sampai_date)
        ringkasan = laporan.ringkasan()

        # Update stat cards
        self._stat_pendapatan.update_value(f"Rp {ringkasan['total_pendapatan']:,.0f}")
        self._stat_transaksi.update_value(str(ringkasan['jumlah_transaksi']))
        self._stat_rata.update_value(f"Rp {ringkasan['rata_rata_transaksi']:,.0f}")

        # Re-render top sellers
        self._render_sellers(ringkasan["menu_terlaris"])

        # Re-render history using filtered range
        if dari_date:
            trx_filtered = self._transaksi_handler.baca_by_tanggal(dari_date, sampai_date)
        else:
            trx_filtered = semua_trx
        self._render_history(trx_filtered)

    def _laporan_semua(self) -> None:
        """Clear date filters and display the full transaction history."""
        self._dari_entry.delete(0, "end")
        self._sampai_entry.delete(0, "end")
        self._refresh_laporan()

    def _render_sellers(self, sellers: list) -> None:
        for w in self._sellers_frame.winfo_children():
            w.destroy()
        if not sellers:
            ctk.CTkLabel(self._sellers_frame, text="Belum ada data penjualan.",
                         font=th.FONT_BODY_SM, text_color=th.TEXT_DISABLED).pack(pady=th.PAD_LG)
            return
        for rank, item in enumerate(sellers[:10], start=1):
            row = ctk.CTkFrame(self._sellers_frame, fg_color=th.BG_DARK, corner_radius=th.RADIUS_SM)
            row.pack(fill="x", pady=2)
            row.columnconfigure(1, weight=1)

            # Rank badge
            rank_colors = {1: th.ACCENT_PRIMARY, 2: th.TEXT_SECONDARY, 3: "#CD7F32"}
            badge_color = rank_colors.get(rank, th.BG_LIGHT)
            ctk.CTkLabel(row, text=f"#{rank}", width=32, font=th.FONT_LABEL,
                         fg_color=badge_color, corner_radius=th.RADIUS_SM,
                         text_color="#FFFFFF").grid(row=0, column=0, padx=th.PAD_SM,
                                                    pady=th.PAD_XS, sticky="w")
            ctk.CTkLabel(row, text=item["nama_produk"], font=th.FONT_BODY,
                         text_color=th.TEXT_PRIMARY, anchor="w"
                         ).grid(row=0, column=1, padx=th.PAD_XS, sticky="w")
            ctk.CTkLabel(row, text=f"{item['total_terjual']} pcs", font=th.FONT_LABEL,
                         text_color=th.ACCENT_PRIMARY
                         ).grid(row=0, column=2, padx=th.PAD_SM)

    def _render_history(self, transactions: list) -> None:
        for w in self._history_frame.winfo_children():
            w.destroy()
        if not transactions:
            ctk.CTkLabel(self._history_frame, text="Belum ada riwayat transaksi.",
                         font=th.FONT_BODY_SM, text_color=th.TEXT_DISABLED).pack(pady=th.PAD_LG)
            return

        # Header row
        header = ctk.CTkFrame(self._history_frame, fg_color=th.BG_DARKEST,
                               corner_radius=th.RADIUS_SM)
        header.pack(fill="x", pady=(0, 2))
        header.columnconfigure(1, weight=1)
        for col, (txt, w) in enumerate([
            ("ID Transaksi", 110), ("Pelanggan", 0), ("Meja", 50),
            ("Total", 100), ("Metode", 90), ("Status", 80), ("Waktu", 130),
        ]):
            ctk.CTkLabel(header, text=txt, font=th.FONT_LABEL,
                         text_color=th.TEXT_SECONDARY, width=w if w else 0,
                         anchor="w").grid(row=0, column=col, padx=th.PAD_SM,
                                          pady=th.PAD_XS, sticky="w")

        for idx, trx in enumerate(reversed(transactions)):
            bg = th.BG_DARK if idx % 2 == 0 else th.BG_MEDIUM
            row = ctk.CTkFrame(self._history_frame, fg_color=bg, corner_radius=th.RADIUS_SM)
            row.pack(fill="x", pady=1)
            row.columnconfigure(1, weight=1)

            pelanggan = trx.get("pelanggan", {})
            waktu_raw = trx.get("waktu_transaksi", "")
            try:
                waktu_fmt = datetime.datetime.fromisoformat(waktu_raw).strftime("%d/%m %H:%M")
            except ValueError:
                waktu_fmt = waktu_raw[:16]

            status = trx.get("status_pembayaran", "-")
            status_color = th.ACCENT_SUCCESS if status == "Lunas" else th.ACCENT_DANGER

            cells = [
                (trx.get("id_transaksi", "-")[:12], th.FONT_MONO, th.TEXT_SECONDARY, 110),
                (pelanggan.get("nama", "-"), th.FONT_BODY, th.TEXT_PRIMARY, 0),
                (str(pelanggan.get("nomor_meja", "-")), th.FONT_BODY_SM, th.TEXT_SECONDARY, 50),
                (f"Rp{trx.get('total', 0):,.0f}", th.FONT_LABEL, th.ACCENT_PRIMARY, 100),
                (trx.get("metode_pembayaran", "-"), th.FONT_BODY_SM, th.TEXT_SECONDARY, 90),
            ]
            for col, (text, font, color, width) in enumerate(cells):
                ctk.CTkLabel(row, text=text, font=font, text_color=color,
                             width=width if width else 0, anchor="w"
                             ).grid(row=0, column=col, padx=th.PAD_SM,
                                    pady=th.PAD_XS, sticky="w")
            ctk.CTkLabel(row, text=status, font=th.FONT_BODY_SM,
                         text_color=status_color, width=80
                         ).grid(row=0, column=5, padx=th.PAD_SM)
            ctk.CTkLabel(row, text=waktu_fmt, font=th.FONT_BODY_SM,
                         text_color=th.TEXT_SECONDARY, width=130
                         ).grid(row=0, column=6, padx=th.PAD_SM)
