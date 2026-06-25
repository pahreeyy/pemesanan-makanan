# models/item_pesanan.py
# Represents a single line-item inside a customer's shopping cart.

from __future__ import annotations
from typing import Union
from models.menu import Menu
from models.paket import Paket


class ItemPesanan:
    """
    Represents one ordered item — either a single Menu or a Paket bundle.

    Attributes:
        produk  (Menu | Paket) : The referenced menu item or package.
        jumlah  (int)          : Quantity ordered (must be >= 1).

    Derived:
        sub_total (float)      : Computed as unit_price × jumlah.
    """

    def __init__(self, produk: Union[Menu, Paket], jumlah: int = 1) -> None:
        if jumlah < 1:
            raise ValueError("Jumlah item harus minimal 1.")
        self.produk: Union[Menu, Paket] = produk
        self.jumlah: int = jumlah

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def hitung_sub_total(self) -> float:
        """Return the line-item total: unit_price × jumlah."""
        if isinstance(self.produk, Menu):
            return self.produk.harga * self.jumlah
        elif isinstance(self.produk, Paket):
            return self.produk.harga_paket * self.jumlah
        return 0.0

    @property
    def nama_produk(self) -> str:
        """Convenience accessor for the product's display name."""
        if isinstance(self.produk, Menu):
            return self.produk.nama_menu
        elif isinstance(self.produk, Paket):
            return self.produk.nama_paket
        return "-"

    @property
    def harga_satuan(self) -> float:
        """Convenience accessor for the product's unit price."""
        if isinstance(self.produk, Menu):
            return self.produk.harga
        elif isinstance(self.produk, Paket):
            return self.produk.harga_paket
        return 0.0

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary for JSON storage inside a Transaksi."""
        tipe = "menu" if isinstance(self.produk, Menu) else "paket"
        id_produk = (
            self.produk.id_menu
            if isinstance(self.produk, Menu)
            else self.produk.id_paket
        )
        return {
            "tipe": tipe,
            "id_produk": id_produk,
            "nama_produk": self.nama_produk,
            "harga_satuan": self.harga_satuan,
            "jumlah": self.jumlah,
            "sub_total": self.hitung_sub_total(),
        }

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ItemPesanan({self.nama_produk!r}, "
            f"jumlah={self.jumlah}, sub_total=Rp{self.hitung_sub_total():,.0f})"
        )
