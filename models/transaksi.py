# models/transaksi.py
# Represents a completed financial transaction for a customer visit.

from __future__ import annotations
import datetime
import uuid
from enum import Enum
from typing import List, Optional

from models.item_pesanan import ItemPesanan
from models.pelanggan import Pelanggan


# Pewarisan (Inheritance): Enum mewarisi sifat dari str dan Enum bawaan Python
class MetodePembayaran(str, Enum):
    """Accepted payment methods."""
    TUNAI    = "Tunai"
    NON_TUNAI = "Non-Tunai"


class StatusPembayaran(str, Enum):
    """Payment completion states."""
    BELUM_BAYAR = "Belum Bayar"
    LUNAS       = "Lunas"


class Transaksi:
    """
    Represents a single financial transaction for a customer visit.

    Attributes:
        id_transaksi      (str)               : Unique transaction ID (UUID-based).
        pelanggan         (Pelanggan)          : The customer linked to this transaction.
        items             (List[ItemPesanan])  : Ordered items included in the bill.
        metode_pembayaran (MetodePembayaran)   : Cash or non-cash.
        status_pembayaran (StatusPembayaran)   : Whether payment has been collected.
        waktu_transaksi   (datetime)           : Timestamp of the transaction.
        jumlah_bayar      (float)              : Amount tendered by the customer.
        kembalian         (float)              : Change returned (cash only).
    """

    def __init__(
        self,
        pelanggan: Pelanggan,
        items: List[ItemPesanan],
        metode_pembayaran: MetodePembayaran = MetodePembayaran.TUNAI,
        id_transaksi: Optional[str] = None,
        waktu_transaksi: Optional[datetime.datetime] = None,
    ) -> None:
        self.id_transaksi: str = id_transaksi or f"TRX-{uuid.uuid4().hex[:8].upper()}"
        # Asosiasi (Association): Transaksi mencatat referensi ke Pelanggan
        self.pelanggan: Pelanggan = pelanggan
        # Agregasi (Aggregation): Transaksi menampung kumpulan ItemPesanan
        self.items: List[ItemPesanan] = items
        self.metode_pembayaran: MetodePembayaran = metode_pembayaran
        self.status_pembayaran: StatusPembayaran = StatusPembayaran.BELUM_BAYAR
        self.waktu_transaksi: datetime.datetime = (
            waktu_transaksi if waktu_transaksi is not None else datetime.datetime.now()
        )
        self.jumlah_bayar: float = 0.0
        self.kembalian: float = 0.0

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def hitung_total(self) -> float:
        """Return the grand total of all items in this transaction."""
        return sum(item.hitung_sub_total() for item in self.items)

    def proses_pembayaran(self, jumlah_bayar: float) -> float:
        """
        Process the payment, compute change, and mark the transaction as paid.

        Args:
            jumlah_bayar (float): Amount tendered by the customer.

        Returns:
            float: Change to return to the customer (0 for non-cash).

        Raises:
            ValueError: If jumlah_bayar is less than the total (for cash).
            ValueError: If the transaction is already paid.
        """
        if self.status_pembayaran == StatusPembayaran.LUNAS:
            raise ValueError("Transaksi ini sudah lunas.")

        total = self.hitung_total()

        if self.metode_pembayaran == MetodePembayaran.TUNAI:
            if jumlah_bayar < total:
                raise ValueError(
                    f"Pembayaran kurang. Total: Rp{total:,.0f}, "
                    f"Diterima: Rp{jumlah_bayar:,.0f}"
                )
            self.kembalian = jumlah_bayar - total
        else:
            # Non-cash: exact amount assumed
            self.kembalian = 0.0

        self.jumlah_bayar = jumlah_bayar
        self.status_pembayaran = StatusPembayaran.LUNAS
        return self.kembalian

    def cetak_struk(self) -> str:
        """
        Generate a plain-text receipt string.
        Delegates to NotaPesanan for full formatting.
        """
        from models.nota_pesanan import NotaPesanan  # avoid circular import
        # Ketergantungan (Dependency): Transaksi memanggil NotaPesanan sementara untuk fungsi cetak
        nota = NotaPesanan(self)
        return nota.format_nota()

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the transaction to a plain dictionary for JSON storage."""
        return {
            "id_transaksi": self.id_transaksi,
            "pelanggan": self.pelanggan.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "total": self.hitung_total(),
            "metode_pembayaran": self.metode_pembayaran.value,
            "status_pembayaran": self.status_pembayaran.value,
            "jumlah_bayar": self.jumlah_bayar,
            "kembalian": self.kembalian,
            "waktu_transaksi": self.waktu_transaksi.isoformat(),
        }

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Transaksi(id={self.id_transaksi!r}, "
            f"total=Rp{self.hitung_total():,.0f}, "
            f"status={self.status_pembayaran.value!r})"
        )
