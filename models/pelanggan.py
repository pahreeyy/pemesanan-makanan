# models/pelanggan.py
# Represents a restaurant guest / table customer.

from __future__ import annotations
from models.keranjang import Keranjang


class Pelanggan:
    """
    Represents a guest who is placing an order.

    Attributes:
        nama        (str)      : Customer name or alias (e.g. "Budi", "Meja 3").
        nomor_meja  (int)      : Table number assigned to this customer.
        keranjang   (Keranjang): The customer's personal order basket.
    """

    def __init__(self, nama: str, nomor_meja: int = 0) -> None:
        self.nama: str = nama
        self.nomor_meja: int = nomor_meja
        self.keranjang: Keranjang = Keranjang()

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def pilih_meja(self, no_meja: int) -> None:
        """
        Assign or change the table number for this customer.

        Args:
            no_meja (int): The table number to assign (must be > 0).

        Raises:
            ValueError: If no_meja is not a positive integer.
        """
        if no_meja < 1:
            raise ValueError("Nomor meja harus lebih dari 0.")
        self.nomor_meja = no_meja

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the customer's metadata to a plain dictionary."""
        return {
            "nama": self.nama,
            "nomor_meja": self.nomor_meja,
        }

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Pelanggan(nama={self.nama!r}, meja={self.nomor_meja}, "
            f"keranjang={self.keranjang})"
        )
