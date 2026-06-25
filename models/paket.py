# models/paket.py
# Represents a bundled meal package composed of multiple Menu items.

from __future__ import annotations
from typing import List


class Paket:
    """
    Represents a bundled meal package (combo).

    Attributes:
        id_paket    (str)       : Unique identifier, e.g. "PKT001".
        nama_paket  (str)       : Display name of the package.
        harga_paket (float)     : Fixed bundle price in Rupiah.
        daftar_menu (List[str]) : List of Menu id_menu strings included in the bundle.
    """

    def __init__(
        self,
        id_paket: str,
        nama_paket: str,
        harga_paket: float,
        daftar_menu: List[str] | None = None,
    ) -> None:
        self.id_paket: str = id_paket
        self.nama_paket: str = nama_paket
        self.harga_paket: float = float(harga_paket)
        self.daftar_menu: List[str] = daftar_menu if daftar_menu is not None else []

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize this Paket instance to a plain dictionary for JSON storage."""
        return {
            "id_paket": self.id_paket,
            "nama_paket": self.nama_paket,
            "harga_paket": self.harga_paket,
            "daftar_menu": self.daftar_menu,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Paket":
        """Deserialize a Paket instance from a plain dictionary (loaded from JSON)."""
        return cls(
            id_paket=data["id_paket"],
            nama_paket=data["nama_paket"],
            harga_paket=float(data["harga_paket"]),
            daftar_menu=data.get("daftar_menu", []),
        )

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Paket({self.id_paket!r}, {self.nama_paket!r}, "
            f"Rp{self.harga_paket:,.0f}, items={len(self.daftar_menu)})"
        )
