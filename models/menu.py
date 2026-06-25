# models/menu.py
# Represents a single food/beverage item available in the restaurant catalog.


class Menu:
    """
    Represents a single menu item (food or beverage).

    Attributes:
        id_menu   (str)   : Unique identifier, e.g. "MKN001".
        nama_menu (str)   : Display name of the menu item.
        harga     (float) : Unit price in Rupiah.
        kategori  (str)   : Category label, e.g. "Makanan", "Minuman", "Dessert".
        tersedia  (bool)  : Whether the item is currently available for ordering.
    """

    def __init__(
        self,
        id_menu: str,
        nama_menu: str,
        harga: float,
        kategori: str,
        tersedia: bool = True,
    ) -> None:
        self.id_menu: str = id_menu
        self.nama_menu: str = nama_menu
        self.harga: float = float(harga)
        self.kategori: str = kategori
        self.tersedia: bool = tersedia

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize this Menu instance to a plain dictionary for JSON storage."""
        return {
            "id_menu": self.id_menu,
            "nama_menu": self.nama_menu,
            "harga": self.harga,
            "kategori": self.kategori,
            "tersedia": self.tersedia,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Menu":
        """Deserialize a Menu instance from a plain dictionary (loaded from JSON)."""
        return cls(
            id_menu=data["id_menu"],
            nama_menu=data["nama_menu"],
            harga=float(data["harga"]),
            kategori=data["kategori"],
            tersedia=data.get("tersedia", True),
        )

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        status = "✓" if self.tersedia else "✗"
        return (
            f"Menu({self.id_menu!r}, {self.nama_menu!r}, "
            f"Rp{self.harga:,.0f}, {self.kategori!r}, tersedia={status})"
        )
