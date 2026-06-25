# controllers/admin_restoran.py
# AdminRestoran — the business-logic controller for the Management side.
#
# This class acts as the service layer between the Admin UI views and the
# underlying data handlers.  The UI calls methods here rather than
# touching data files directly, keeping business logic decoupled from
# the presentation layer.

from __future__ import annotations
import os
from typing import List, Optional

from data_handlers.menu_handler import MenuHandler
from data_handlers.paket_handler import PaketHandler
from data_handlers.transaksi_handler import TransaksiHandler
from models.menu import Menu
from models.paket import Paket
from models.laporan_penjualan import LaporanPenjualan

import datetime

_DATA_DIR       = os.path.join(os.path.dirname(__file__), "..", "data")
_MENU_FILE      = os.path.abspath(os.path.join(_DATA_DIR, "menu.json"))
_PAKET_FILE     = os.path.abspath(os.path.join(_DATA_DIR, "paket.json"))
_TRANSAKSI_FILE = os.path.abspath(os.path.join(_DATA_DIR, "transaksi.json"))


class AdminRestoran:
    """
    Business logic controller for the Admin / Manager role.

    Encapsulates all CRUD operations for Menu and Paket, and provides
    aggregated reporting via LaporanPenjualan.

    Attributes:
        menu_handler      (MenuHandler)      : CRUD gateway for menu.json.
        paket_handler     (PaketHandler)     : CRUD gateway for paket.json.
        transaksi_handler (TransaksiHandler) : Read/aggregate gateway for transaksi.json.
    """

    def __init__(self) -> None:
        self.menu_handler      = MenuHandler(_MENU_FILE)
        self.paket_handler     = PaketHandler(_PAKET_FILE)
        self.transaksi_handler = TransaksiHandler(_TRANSAKSI_FILE)

    # ==================================================================
    # Menu CRUD
    # ==================================================================

    def tambah_menu(self, menu: Menu) -> None:
        """
        Create: Add a new menu item to the catalog.

        Args:
            menu (Menu): Fully constructed Menu object.

        Raises:
            ValueError: If a menu with the same id_menu already exists.
        """
        self.menu_handler.tambah(menu)

    def lihat_semua_menu(self) -> List[Menu]:
        """Read All: Return the complete list of menu items."""
        return self.menu_handler.baca_semua()

    def lihat_menu_by_id(self, id_menu: str) -> Optional[Menu]:
        """Read One: Return a single Menu by its ID, or None if not found."""
        return self.menu_handler.baca_by_id(id_menu)

    def perbarui_menu(self, menu: Menu) -> bool:
        """
        Update: Replace the stored record for the given id_menu.

        Returns:
            True if the menu was found and updated, False otherwise.
        """
        return self.menu_handler.perbarui(menu)

    def hapus_menu(self, id_menu: str) -> bool:
        """
        Delete: Remove a menu item from the catalog by its ID.

        Returns:
            True if deleted, False if not found.
        """
        return self.menu_handler.hapus(id_menu)

    def ubah_ketersediaan_menu(self, id_menu: str, tersedia: bool) -> bool:
        """
        Toggle a menu item's availability without a full record replacement.

        Returns:
            True if updated, False if ID not found.
        """
        return self.menu_handler.ubah_ketersediaan(id_menu, tersedia)

    # ==================================================================
    # Paket CRUD
    # ==================================================================

    def tambah_paket(self, paket: Paket) -> None:
        """Create: Add a new meal package."""
        self.paket_handler.tambah(paket)

    def lihat_semua_paket(self) -> List[Paket]:
        """Read All: Return all defined meal packages."""
        return self.paket_handler.baca_semua()

    def perbarui_paket(self, paket: Paket) -> bool:
        """Update: Replace the stored record for the given id_paket."""
        return self.paket_handler.perbarui(paket)

    def hapus_paket(self, id_paket: str) -> bool:
        """Delete: Remove a meal package by its ID."""
        return self.paket_handler.hapus(id_paket)

    # ==================================================================
    # Reporting
    # ==================================================================

    def buat_laporan(
        self,
        tanggal_mulai: Optional[datetime.date] = None,
        tanggal_akhir: Optional[datetime.date] = None,
    ) -> LaporanPenjualan:
        """
        Build and return a LaporanPenjualan for the given date range.

        Args:
            tanggal_mulai : Start date filter (inclusive). None = no lower bound.
            tanggal_akhir : End date filter (inclusive). None = no upper bound.

        Returns:
            LaporanPenjualan: Instance ready for aggregation queries.
        """
        semua_trx = self.transaksi_handler.baca_semua()
        return LaporanPenjualan(semua_trx, tanggal_mulai, tanggal_akhir)
