# models/laporan_penjualan.py
# Aggregates completed Transaksi records into financial summary reports.

from __future__ import annotations
import datetime
from typing import List, Optional


class LaporanPenjualan:
    """
    Computes and presents financial summary data from a list of
    completed transaction dictionaries (loaded from transaksi.json).

    Attributes:
        transaksi_list (List[dict]): Raw transaction records from JSON storage.
        tanggal_mulai  (date | None): Optional filter — start date (inclusive).
        tanggal_akhir  (date | None): Optional filter — end date (inclusive).
    """

    def __init__(
        self,
        transaksi_list: List[dict],
        tanggal_mulai: Optional[datetime.date] = None,
        tanggal_akhir: Optional[datetime.date] = None,
    ) -> None:
        self.transaksi_list: List[dict] = transaksi_list
        self.tanggal_mulai: Optional[datetime.date] = tanggal_mulai
        self.tanggal_akhir: Optional[datetime.date] = tanggal_akhir

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _filtered(self) -> List[dict]:
        """Return the subset of transactions within the date range filter."""
        result = []
        for trx in self.transaksi_list:
            # Only include fully paid transactions
            if trx.get("status_pembayaran") != "Lunas":
                continue
            try:
                waktu = datetime.datetime.fromisoformat(trx["waktu_transaksi"])
                trx_date = waktu.date()
            except (KeyError, ValueError):
                continue

            if self.tanggal_mulai and trx_date < self.tanggal_mulai:
                continue
            if self.tanggal_akhir and trx_date > self.tanggal_akhir:
                continue
            result.append(trx)
        return result

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------

    def hitung_total_pendapatan(self) -> float:
        """Return the total revenue from all filtered, paid transactions."""
        return sum(trx.get("total", 0.0) for trx in self._filtered())

    def hitung_jumlah_transaksi(self) -> int:
        """Return the count of completed transactions in the filtered period."""
        return len(self._filtered())

    def hitung_rata_rata_transaksi(self) -> float:
        """Return the average transaction value in the filtered period."""
        filtered = self._filtered()
        if not filtered:
            return 0.0
        return sum(trx.get("total", 0.0) for trx in filtered) / len(filtered)

    def menu_terlaris(self) -> List[dict]:
        """
        Rank menu items by total units sold across filtered transactions.

        Returns:
            List[dict]: Sorted list of dicts with keys:
                        'nama_produk', 'total_terjual', 'total_pendapatan'.
        """
        penjualan: dict[str, dict] = {}
        for trx in self._filtered():
            for item in trx.get("items", []):
                nama = item.get("nama_produk", "?")
                qty = item.get("jumlah", 0)
                sub = item.get("sub_total", 0.0)
                if nama not in penjualan:
                    penjualan[nama] = {"nama_produk": nama, "total_terjual": 0, "total_pendapatan": 0.0}
                penjualan[nama]["total_terjual"] += qty
                penjualan[nama]["total_pendapatan"] += sub

        return sorted(penjualan.values(), key=lambda x: x["total_terjual"], reverse=True)

    def ringkasan(self) -> dict:
        """
        Return a summary dictionary suitable for display in the report UI.

        Returns:
            dict with keys: 'total_pendapatan', 'jumlah_transaksi',
                            'rata_rata_transaksi', 'menu_terlaris'.
        """
        return {
            "total_pendapatan": self.hitung_total_pendapatan(),
            "jumlah_transaksi": self.hitung_jumlah_transaksi(),
            "rata_rata_transaksi": self.hitung_rata_rata_transaksi(),
            "menu_terlaris": self.menu_terlaris(),
        }

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"LaporanPenjualan("
            f"periode={self.tanggal_mulai} s/d {self.tanggal_akhir}, "
            f"transaksi={self.hitung_jumlah_transaksi()}, "
            f"pendapatan=Rp{self.hitung_total_pendapatan():,.0f})"
        )
