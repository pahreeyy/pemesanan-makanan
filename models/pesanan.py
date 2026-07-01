# models/pesanan.py
# Tracks the kitchen-side lifecycle of an order.

from __future__ import annotations
import datetime
from enum import Enum
from typing import List
from models.item_pesanan import ItemPesanan


# Pewarisan (Inheritance): Enum mewarisi sifat dari str dan Enum bawaan Python
class StatusPesanan(str, Enum):
    """Lifecycle states that an order can be in."""
    ANTRIAN  = "Antrian"    # Waiting to be prepared
    DIMASAK  = "Dimasak"    # Being prepared in the kitchen
    SELESAI  = "Selesai"    # Ready to be served / served


class Pesanan:
    """
    Represents a kitchen order that tracks which items are being prepared
    and the current preparation status.

    Attributes:
        id_pesanan  (str)             : Unique order reference.
        items       (List[ItemPesanan]): Ordered items tied to this order.
        status      (StatusPesanan)   : Current preparation status.
        waktu_pesan (datetime)        : Timestamp when the order was placed.
    """

    def __init__(
        self,
        id_pesanan: str,
        items: List[ItemPesanan] | None = None,
        status: StatusPesanan = StatusPesanan.ANTRIAN,
        waktu_pesan: datetime.datetime | None = None,
    ) -> None:
        self.id_pesanan: str = id_pesanan
        # Agregasi (Aggregation): Pesanan menampung list dari ItemPesanan
        self.items: List[ItemPesanan] = items if items is not None else []
        self.status: StatusPesanan = status
        self.waktu_pesan: datetime.datetime = (
            waktu_pesan if waktu_pesan is not None else datetime.datetime.now()
        )

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def mulai_masak(self) -> None:
        """Transition the order status from ANTRIAN to DIMASAK."""
        if self.status != StatusPesanan.ANTRIAN:
            raise ValueError(
                f"Pesanan tidak bisa dimulai dari status '{self.status.value}'."
            )
        self.status = StatusPesanan.DIMASAK

    def tandai_selesai(self) -> None:
        """Transition the order status from DIMASAK to SELESAI."""
        if self.status != StatusPesanan.DIMASAK:
            raise ValueError(
                f"Pesanan tidak bisa diselesaikan dari status '{self.status.value}'."
            )
        self.status = StatusPesanan.SELESAI

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary for JSON embedding."""
        return {
            "id_pesanan": self.id_pesanan,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "waktu_pesan": self.waktu_pesan.isoformat(),
        }

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Pesanan(id={self.id_pesanan!r}, "
            f"status={self.status.value!r}, "
            f"items={len(self.items)})"
        )
