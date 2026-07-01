# data_handlers/transaksi_handler.py
# Concrete DataHandler for persisting and querying Transaksi records
# in transaksi.json.

from __future__ import annotations
import datetime
from typing import List, Optional

from data_handlers.base_handler import BaseHandler
from models.transaksi import Transaksi


# Pewarisan (Inheritance): TransaksiHandler mewarisi fungsi CRUD dasar dari BaseHandler
class TransaksiHandler(BaseHandler):
    """
    Manages all CRUD operations for Transaksi records backed by transaksi.json.

    Note on Update/Delete:
        Transactions are generally immutable once created (financial audit trail).
        The perbarui() and hapus() methods exist to satisfy the BaseHandler
        contract but should be used with caution.

    Inherits:
        BaseHandler: Provides _baca_semua() / _tulis_semua() JSON I/O.
    """

    _ID_KEY = "id_transaksi"

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def tambah(self, item: Transaksi) -> None:
        """
        Append a completed Transaksi record to transaksi.json.

        Args:
            item (Transaksi): The transaction object to persist.

        Raises:
            ValueError: If a transaction with the same id_transaksi already exists.
        """
        data = self._baca_semua()
        if any(r[self._ID_KEY] == item.id_transaksi for r in data):
            raise ValueError(
                f"Transaksi '{item.id_transaksi}' sudah tersimpan."
            )
        data.append(item.to_dict())
        self._tulis_semua(data)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def baca_semua(self) -> List[dict]:
        """
        Load all transaction records from transaksi.json.

        Returns:
            List[dict]: Raw dictionaries (not domain objects, since
                        reconstructing Transaksi requires Menu/Pelanggan refs).
        """
        return self._baca_semua()

    def baca_by_id(self, id_transaksi: str) -> Optional[dict]:
        """
        Find and return a single raw transaction dictionary by its ID.

        Returns:
            dict if found, otherwise None.
        """
        for record in self._baca_semua():
            if record[self._ID_KEY] == id_transaksi:
                return record
        return None

    def baca_by_tanggal(
        self,
        tanggal_mulai: datetime.date,
        tanggal_akhir: Optional[datetime.date] = None,
    ) -> List[dict]:
        """
        Filter transactions within a date range.

        Args:
            tanggal_mulai  : Start date (inclusive).
            tanggal_akhir  : End date (inclusive). Defaults to today if None.

        Returns:
            List[dict]: Matching transaction dictionaries.
        """
        if tanggal_akhir is None:
            tanggal_akhir = datetime.date.today()

        result = []
        for record in self._baca_semua():
            try:
                waktu = datetime.datetime.fromisoformat(record["waktu_transaksi"])
                trx_date = waktu.date()
            except (KeyError, ValueError):
                continue
            if tanggal_mulai <= trx_date <= tanggal_akhir:
                result.append(record)
        return result

    def baca_hari_ini(self) -> List[dict]:
        """Return all transactions recorded today."""
        today = datetime.date.today()
        return self.baca_by_tanggal(today, today)

    # ------------------------------------------------------------------
    # Update  (use with care — financial data should be immutable)
    # ------------------------------------------------------------------

    def perbarui(self, item: dict) -> bool:
        """
        Replace a stored transaction record with an updated dict.

        Args:
            item (dict): Updated transaction dictionary (must contain id_transaksi).

        Returns:
            True if found and replaced, False otherwise.
        """
        data = self._baca_semua()
        id_target = item.get(self._ID_KEY, "")
        for idx, record in enumerate(data):
            if record[self._ID_KEY] == id_target:
                data[idx] = item
                self._tulis_semua(data)
                return True
        return False

    # ------------------------------------------------------------------
    # Delete  (use with care — audit trail)
    # ------------------------------------------------------------------

    def hapus(self, id_transaksi: str) -> bool:
        """
        Remove a transaction record by its ID.

        Returns:
            True if found and deleted, False otherwise.
        """
        data = self._baca_semua()
        new_data = [r for r in data if r[self._ID_KEY] != id_transaksi]
        if len(new_data) == len(data):
            return False
        self._tulis_semua(new_data)
        return True

    # ------------------------------------------------------------------
    # Aggregation helpers (used by LaporanPenjualan)
    # ------------------------------------------------------------------

    def total_pendapatan(
        self,
        tanggal_mulai: Optional[datetime.date] = None,
        tanggal_akhir: Optional[datetime.date] = None,
    ) -> float:
        """Compute total revenue across optionally filtered transaction records."""
        if tanggal_mulai:
            records = self.baca_by_tanggal(tanggal_mulai, tanggal_akhir)
        else:
            records = self.baca_semua()
        return sum(
            r.get("total", 0.0)
            for r in records
            if r.get("status_pembayaran") == "Lunas"
        )
