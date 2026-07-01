# data_handlers/paket_handler.py
# Concrete DataHandler for CRUD operations on paket.json.

from __future__ import annotations
from typing import List, Optional

from data_handlers.base_handler import BaseHandler
from models.paket import Paket


# Pewarisan (Inheritance): PaketHandler mewarisi fungsi CRUD dasar dari BaseHandler
class PaketHandler(BaseHandler):
    """
    Manages all CRUD operations for Paket objects backed by paket.json.

    Inherits:
        BaseHandler: Provides _baca_semua() / _tulis_semua() JSON I/O.
    """

    _ID_KEY = "id_paket"

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def tambah(self, item: Paket) -> None:
        """
        Persist a new Paket to paket.json.

        Args:
            item (Paket): The Paket object to add.

        Raises:
            ValueError: If a paket with the same id_paket already exists.
        """
        data = self._baca_semua()
        if any(r[self._ID_KEY] == item.id_paket for r in data):
            raise ValueError(
                f"Paket dengan ID '{item.id_paket}' sudah ada."
            )
        data.append(item.to_dict())
        self._tulis_semua(data)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def baca_semua(self) -> List[Paket]:
        """Load all paket records and return them as a list of Paket objects."""
        return [Paket.from_dict(r) for r in self._baca_semua()]

    def baca_by_id(self, id_paket: str) -> Optional[Paket]:
        """
        Find and return a single Paket object by its id_paket.

        Returns:
            Paket if found, otherwise None.
        """
        for record in self._baca_semua():
            if record[self._ID_KEY] == id_paket:
                return Paket.from_dict(record)
        return None

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def perbarui(self, item: Paket) -> bool:
        """
        Replace the stored record for the given id_paket with updated data.

        Returns:
            True if the record was found and updated, False otherwise.
        """
        data = self._baca_semua()
        for idx, record in enumerate(data):
            if record[self._ID_KEY] == item.id_paket:
                data[idx] = item.to_dict()
                self._tulis_semua(data)
                return True
        return False

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def hapus(self, id_paket: str) -> bool:
        """
        Remove the paket record with the given id_paket from paket.json.

        Returns:
            True if found and deleted, False otherwise.
        """
        data = self._baca_semua()
        new_data = [r for r in data if r[self._ID_KEY] != id_paket]
        if len(new_data) == len(data):
            return False
        self._tulis_semua(new_data)
        return True
