# data_handlers/menu_handler.py
# Concrete DataHandler for CRUD operations on menu.json.

from __future__ import annotations
from typing import List, Optional

from data_handlers.base_handler import BaseHandler
from models.menu import Menu


class MenuHandler(BaseHandler):
    """
    Manages all CRUD operations for Menu objects backed by menu.json.

    Inherits:
        BaseHandler: Provides _baca_semua() / _tulis_semua() JSON I/O.
    """

    # ── The ID field used to identify Menu records ──────────────────────
    _ID_KEY = "id_menu"

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def tambah(self, item: Menu) -> None:
        """
        Persist a new Menu item to menu.json.

        Args:
            item (Menu): The Menu object to add.

        Raises:
            ValueError: If a menu with the same id_menu already exists.
        """
        data = self._baca_semua()
        if any(r[self._ID_KEY] == item.id_menu for r in data):
            raise ValueError(
                f"Menu dengan ID '{item.id_menu}' sudah ada. "
                "Gunakan perbarui() untuk mengubah data yang ada."
            )
        data.append(item.to_dict())
        self._tulis_semua(data)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def baca_semua(self) -> List[Menu]:
        """Load all menu records and return them as a list of Menu objects."""
        return [Menu.from_dict(r) for r in self._baca_semua()]

    def baca_by_id(self, id_menu: str) -> Optional[Menu]:
        """
        Find and return a single Menu object by its id_menu.

        Returns:
            Menu if found, otherwise None.
        """
        for record in self._baca_semua():
            if record[self._ID_KEY] == id_menu:
                return Menu.from_dict(record)
        return None

    def baca_by_kategori(self, kategori: str) -> List[Menu]:
        """
        Return all Menu items belonging to a given category.

        Args:
            kategori (str): The category string to filter by.

        Returns:
            List[Menu]: Filtered list (may be empty).
        """
        return [
            Menu.from_dict(r)
            for r in self._baca_semua()
            if r.get("kategori", "").lower() == kategori.lower()
        ]

    def baca_kategori_unik(self) -> List[str]:
        """Return a sorted list of all unique category strings in the menu."""
        return sorted({r.get("kategori", "") for r in self._baca_semua()})

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def perbarui(self, item: Menu) -> bool:
        """
        Replace the stored record for the given id_menu with updated data.

        Args:
            item (Menu): Menu object containing updated values.

        Returns:
            True if the record was found and updated, False otherwise.
        """
        data = self._baca_semua()
        for idx, record in enumerate(data):
            if record[self._ID_KEY] == item.id_menu:
                data[idx] = item.to_dict()
                self._tulis_semua(data)
                return True
        return False

    def ubah_ketersediaan(self, id_menu: str, tersedia: bool) -> bool:
        """
        Toggle the availability flag of a menu item without replacing the
        entire record — a focused, lightweight update.

        Args:
            id_menu  (str)  : Target menu item ID.
            tersedia (bool) : New availability status.

        Returns:
            True if updated, False if ID not found.
        """
        data = self._baca_semua()
        for record in data:
            if record[self._ID_KEY] == id_menu:
                record["tersedia"] = tersedia
                self._tulis_semua(data)
                return True
        return False

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def hapus(self, id_menu: str) -> bool:
        """
        Remove the menu record with the given id_menu from menu.json.

        Args:
            id_menu (str): The ID of the menu item to delete.

        Returns:
            True if found and deleted, False otherwise.
        """
        data = self._baca_semua()
        new_data = [r for r in data if r[self._ID_KEY] != id_menu]
        if len(new_data) == len(data):
            return False  # Nothing was removed
        self._tulis_semua(new_data)
        return True
