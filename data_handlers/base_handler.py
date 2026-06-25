# data_handlers/base_handler.py
# Abstract base class that enforces a consistent CRUD interface for all
# JSON-backed data handlers in this project.

from __future__ import annotations
import json
import os
from abc import ABC, abstractmethod
from typing import Any, List, Optional


class BaseHandler(ABC):
    """
    Abstract base class providing generic JSON file I/O operations.

    All concrete DataHandler subclasses (MenuHandler, TransaksiHandler, etc.)
    must inherit from this class and implement the abstract CRUD methods.

    Attributes:
        filepath (str): Absolute or relative path to the managed JSON file.
    """

    def __init__(self, filepath: str) -> None:
        self.filepath: str = filepath
        self._ensure_file_exists()

    # ------------------------------------------------------------------
    # Core JSON I/O
    # ------------------------------------------------------------------

    def _ensure_file_exists(self) -> None:
        """Create the JSON file (and parent directories) if they do not exist."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _baca_semua(self) -> List[dict]:
        """
        Load and return all records from the JSON file.

        Returns:
            List[dict]: Parsed list of record dictionaries. Returns empty list
                        on decode errors to prevent crashes.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _tulis_semua(self, data: List[dict]) -> None:
        """
        Overwrite the JSON file with the given list of record dictionaries.

        Args:
            data (List[dict]): The full dataset to persist.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Abstract CRUD interface — must be implemented by subclasses
    # ------------------------------------------------------------------

    @abstractmethod
    def tambah(self, item: Any) -> None:
        """Create: Persist a new domain object to the JSON file."""
        ...

    @abstractmethod
    def baca_semua(self) -> List[Any]:
        """Read All: Load all records and return as domain objects."""
        ...

    @abstractmethod
    def baca_by_id(self, id_item: str) -> Optional[Any]:
        """Read One: Find and return a single domain object by its ID."""
        ...

    @abstractmethod
    def perbarui(self, item: Any) -> bool:
        """Update: Find a matching record by ID and replace it with new data."""
        ...

    @abstractmethod
    def hapus(self, id_item: str) -> bool:
        """Delete: Remove the record with the given ID from the JSON file."""
        ...
