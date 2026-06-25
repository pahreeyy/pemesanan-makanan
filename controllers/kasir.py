# controllers/kasir.py
# Kasir — the business-logic controller for cashier operations.
#
# Bridges the Kasir UI view with the data handlers and domain models,
# keeping order creation, payment processing, and receipt generation
# cleanly separated from the presentation layer.

from __future__ import annotations
import os
from typing import List, Optional

from data_handlers.menu_handler import MenuHandler
from data_handlers.paket_handler import PaketHandler
from data_handlers.transaksi_handler import TransaksiHandler

from models.menu import Menu
from models.paket import Paket
from models.pelanggan import Pelanggan
from models.keranjang import Keranjang
from models.item_pesanan import ItemPesanan
from models.pesanan import Pesanan, StatusPesanan
from models.transaksi import Transaksi, MetodePembayaran
from models.nota_pesanan import NotaPesanan

_DATA_DIR       = os.path.join(os.path.dirname(__file__), "..", "data")
_MENU_FILE      = os.path.abspath(os.path.join(_DATA_DIR, "menu.json"))
_PAKET_FILE     = os.path.abspath(os.path.join(_DATA_DIR, "paket.json"))
_TRANSAKSI_FILE = os.path.abspath(os.path.join(_DATA_DIR, "transaksi.json"))


class Kasir:
    """
    Business-logic controller for cashier (Kasir) operations.

    Responsibilities:
    - Load available menu items and packages.
    - Manage the current customer session (Pelanggan + Keranjang).
    - Drive payment processing (Transaksi).
    - Persist completed transactions via TransaksiHandler.
    - Generate and return receipt text (NotaPesanan).

    Attributes:
        menu_handler      (MenuHandler)      : Read gateway for catalog menus.
        paket_handler     (PaketHandler)     : Read gateway for catalog pakets.
        transaksi_handler (TransaksiHandler) : Write gateway for transactions.
        sesi_pelanggan    (Pelanggan | None) : Active customer session.
        sesi_pesanan      (Pesanan | None)   : Active kitchen order tracker.
    """

    def __init__(self) -> None:
        self.menu_handler      = MenuHandler(_MENU_FILE)
        self.paket_handler     = PaketHandler(_PAKET_FILE)
        self.transaksi_handler = TransaksiHandler(_TRANSAKSI_FILE)

        self.sesi_pelanggan: Optional[Pelanggan] = None
        self.sesi_pesanan:   Optional[Pesanan]   = None

    # ==================================================================
    # Session Management
    # ==================================================================

    def mulai_sesi(self, nama_pelanggan: str, nomor_meja: int) -> Pelanggan:
        """
        Start a new order session for a walk-in customer.

        Args:
            nama_pelanggan (str) : Customer name or alias.
            nomor_meja     (int) : Assigned table number.

        Returns:
            Pelanggan: Newly created customer session object.
        """
        self.sesi_pelanggan = Pelanggan(nama=nama_pelanggan, nomor_meja=nomor_meja)
        return self.sesi_pelanggan

    def akhiri_sesi(self) -> None:
        """Clear the current customer session and cart."""
        self.sesi_pelanggan = None
        self.sesi_pesanan   = None

    # ==================================================================
    # Cart Operations (delegates to Pelanggan's Keranjang)
    # ==================================================================

    def tambah_ke_keranjang(self, produk, jumlah: int = 1) -> None:
        """
        Add a Menu or Paket item to the active customer's cart.

        Args:
            produk : A Menu or Paket domain object.
            jumlah : Quantity to add (default 1).

        Raises:
            RuntimeError: If no customer session is active.
        """
        self._cek_sesi_aktif()
        item = ItemPesanan(produk=produk, jumlah=jumlah)
        self.sesi_pelanggan.keranjang.tambah_item(item)

    def hapus_dari_keranjang(self, id_produk: str) -> bool:
        """
        Remove an item from the active cart by product ID.

        Returns:
            True if removed, False if not found.
        """
        self._cek_sesi_aktif()
        return self.sesi_pelanggan.keranjang.hapus_item(id_produk)

    def lihat_keranjang(self) -> List[ItemPesanan]:
        """Return all items currently in the active cart."""
        self._cek_sesi_aktif()
        return self.sesi_pelanggan.keranjang.items

    def hitung_total_keranjang(self) -> float:
        """Return the current cart grand total."""
        self._cek_sesi_aktif()
        return self.sesi_pelanggan.keranjang.hitung_total()

    # ==================================================================
    # Payment
    # ==================================================================

    def proses_pembayaran(
        self,
        jumlah_bayar: float,
        metode: MetodePembayaran = MetodePembayaran.TUNAI,
    ) -> Transaksi:
        """
        Process payment for the active session's cart.

        Constructs a Transaksi, processes the payment, persists it to
        transaksi.json, and clears the session.

        Args:
            jumlah_bayar (float)           : Amount tendered by the customer.
            metode       (MetodePembayaran): TUNAI or NON_TUNAI.

        Returns:
            Transaksi: The completed, paid transaction object.

        Raises:
            RuntimeError : If no active session.
            ValueError   : If cart is empty or payment is insufficient.
        """
        self._cek_sesi_aktif()
        pelanggan = self.sesi_pelanggan
        items     = pelanggan.keranjang.items

        if not items:
            raise ValueError("Keranjang kosong. Tambahkan item sebelum memproses pembayaran.")

        transaksi = Transaksi(
            pelanggan=pelanggan,
            items=items,
            metode_pembayaran=metode,
        )
        transaksi.proses_pembayaran(jumlah_bayar)

        # Persist
        self.transaksi_handler.tambah(transaksi)

        return transaksi

    def cetak_struk(self, transaksi: Transaksi) -> str:
        """
        Generate a printable receipt string for the given transaction.

        Args:
            transaksi (Transaksi): A completed (Lunas) transaction.

        Returns:
            str: Multi-line formatted receipt text.
        """
        nota = NotaPesanan(transaksi)
        return nota.format_nota()

    # ==================================================================
    # Catalog Reads
    # ==================================================================

    def lihat_menu_tersedia(self) -> List[Menu]:
        """Return only the menu items currently marked as tersedia=True."""
        return [m for m in self.menu_handler.baca_semua() if m.tersedia]

    def lihat_semua_paket(self) -> List[Paket]:
        """Return all available meal packages."""
        return self.paket_handler.baca_semua()

    # ==================================================================
    # Internal helpers
    # ==================================================================

    def _cek_sesi_aktif(self) -> None:
        if self.sesi_pelanggan is None:
            raise RuntimeError(
                "Tidak ada sesi pelanggan aktif. Panggil mulai_sesi() terlebih dahulu."
            )
