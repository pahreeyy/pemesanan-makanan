# models/keranjang.py
# Represents the customer's shopping cart (order basket).

from __future__ import annotations
from typing import List, Optional
from models.item_pesanan import ItemPesanan
from models.menu import Menu
from models.paket import Paket


class Keranjang:
    """
    The customer's order basket; holds a list of ItemPesanan objects.

    Methods:
        tambah_item   : Add a new item or increment quantity of an existing one.
        hapus_item    : Remove an item by its product id.
        ubah_jumlah   : Update the quantity of an existing item.
        hitung_total  : Return the sum of all item sub-totals.
        kosongkan     : Clear all items from the cart.
    """

    def __init__(self) -> None:
        # Agregasi (Aggregation): Keranjang menampung kumpulan ItemPesanan
        self._items: List[ItemPesanan] = []

    # ------------------------------------------------------------------
    # Item management
    # ------------------------------------------------------------------

    def tambah_item(self, item: ItemPesanan) -> None:
        """
        Add an ItemPesanan to the cart.
        If the same product already exists, increments its quantity instead
        of adding a duplicate line.
        """
        existing = self._cari_item(self._get_id(item.produk))
        if existing:
            existing.jumlah += item.jumlah
        else:
            self._items.append(item)

    def hapus_item(self, id_produk: str) -> bool:
        """
        Remove an item from the cart by its product id_menu / id_paket.

        Returns:
            True  if the item was found and removed.
            False if no matching item was found.
        """
        for idx, item in enumerate(self._items):
            if self._get_id(item.produk) == id_produk:
                self._items.pop(idx)
                return True
        return False

    def ubah_jumlah(self, id_produk: str, jumlah_baru: int) -> bool:
        """
        Update the quantity of an item.

        Args:
            id_produk   : The id_menu or id_paket of the target item.
            jumlah_baru : New quantity; must be >= 1.

        Returns:
            True if updated, False if item not found.

        Raises:
            ValueError if jumlah_baru < 1.
        """
        if jumlah_baru < 1:
            raise ValueError("Jumlah harus minimal 1. Gunakan hapus_item() untuk menghapus.")
        item = self._cari_item(id_produk)
        if item:
            item.jumlah = jumlah_baru
            return True
        return False

    def kosongkan(self) -> None:
        """Remove all items from the cart."""
        self._items.clear()

    # ------------------------------------------------------------------
    # Calculations
    # ------------------------------------------------------------------

    def hitung_total(self) -> float:
        """Return the grand total of all items in the cart."""
        return sum(item.hitung_sub_total() for item in self._items)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def items(self) -> List[ItemPesanan]:
        """Read-only view of all items currently in the cart."""
        return list(self._items)

    def is_kosong(self) -> bool:
        """Return True when the cart contains no items."""
        return len(self._items) == 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cari_item(self, id_produk: str) -> Optional[ItemPesanan]:
        """Find an item by its product id."""
        for item in self._items:
            if self._get_id(item.produk) == id_produk:
                return item
        return None

    @staticmethod
    def _get_id(produk) -> str:
        """Extract the correct id field from a Menu or Paket object."""
        if isinstance(produk, Menu):
            return produk.id_menu
        elif isinstance(produk, Paket):
            return produk.id_paket
        return ""

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_list(self) -> list:
        """Serialize the cart items to a list of dicts for JSON embedding."""
        return [item.to_dict() for item in self._items]

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Keranjang({len(self._items)} item(s), "
            f"total=Rp{self.hitung_total():,.0f})"
        )
