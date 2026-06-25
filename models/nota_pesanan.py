# models/nota_pesanan.py
# Formats a Transaksi into a printable receipt string.

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.transaksi import Transaksi

_LINE_WIDTH = 42  # Characters wide for a standard 80mm thermal receipt


class NotaPesanan:
    """
    Formats a completed Transaksi into a thermal-printer-style receipt.

    Attributes:
        transaksi (Transaksi): The transaction whose data is being formatted.
    """

    def __init__(self, transaksi: "Transaksi") -> None:
        self.transaksi = transaksi

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def format_nota(self) -> str:
        """
        Generate the full receipt text as a multi-line string.

        Returns:
            str: Formatted receipt ready for display or printing.
        """
        t = self.transaksi
        lines: list[str] = []

        lines.append(self._center("RESTORAN KAMI"))
        lines.append(self._center("Jl. Contoh No. 1, Kota Anda"))
        lines.append(self._center("Tel: (021) 123-4567"))
        lines.append(self._divider("="))

        lines.append(f"ID Transaksi : {t.id_transaksi}")
        lines.append(
            f"Waktu        : "
            f"{t.waktu_transaksi.strftime('%d/%m/%Y %H:%M:%S')}"
        )
        lines.append(f"Pelanggan    : {t.pelanggan.nama}")
        lines.append(f"No. Meja     : {t.pelanggan.nomor_meja}")
        lines.append(f"Pembayaran   : {t.metode_pembayaran.value}")
        lines.append(self._divider("-"))

        lines.append(self._row("Item", "Jml", "Subtotal"))
        lines.append(self._divider("-"))

        for item in t.items:
            lines.append(
                self._row(
                    item.nama_produk,
                    str(item.jumlah),
                    f"Rp{item.hitung_sub_total():>10,.0f}",
                )
            )
            lines.append(f"  @ Rp{item.harga_satuan:,.0f}")

        lines.append(self._divider("-"))
        lines.append(
            self._row("TOTAL", "", f"Rp{t.hitung_total():>10,.0f}")
        )
        lines.append(
            self._row("Dibayar", "", f"Rp{t.jumlah_bayar:>10,.0f}")
        )
        if t.kembalian > 0:
            lines.append(
                self._row("Kembalian", "", f"Rp{t.kembalian:>10,.0f}")
            )

        lines.append(self._divider("="))
        lines.append(self._center("Terima kasih atas kunjungan Anda!"))
        lines.append(self._center("Selamat menikmati hidangan Anda."))
        lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal formatting helpers
    # ------------------------------------------------------------------

    def _divider(self, char: str = "-") -> str:
        return char * _LINE_WIDTH

    def _center(self, text: str) -> str:
        return text.center(_LINE_WIDTH)

    def _row(self, left: str, mid: str, right: str) -> str:
        """Format a three-column row within LINE_WIDTH characters."""
        right_w = 16
        mid_w = 4
        left_w = _LINE_WIDTH - mid_w - right_w
        left_str = left[:left_w].ljust(left_w)
        mid_str = mid[:mid_w].center(mid_w)
        right_str = right[:right_w].rjust(right_w)
        return f"{left_str}{mid_str}{right_str}"
