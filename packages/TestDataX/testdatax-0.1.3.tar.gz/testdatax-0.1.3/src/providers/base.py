from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class DataProvider(ABC):
    """Abstract base class for data providers that generate test data values."""

    @abstractmethod
    def generate_string(self, **kwargs: str) -> str:
        """Generate a string value."""
        pass

    @abstractmethod
    def generate_text(self, **kwargs: str) -> str:
        """Generate a text value."""
        pass

    @abstractmethod
    def generate_integer(self, min_value: int = 0, max_value: int = 100) -> int:
        """Generate an integer value."""
        pass

    @abstractmethod
    def generate_decimal(self, **kwargs: Decimal) -> Decimal:
        """Generate a decimal value."""
        pass

    @abstractmethod
    def generate_boolean(self) -> bool:
        """Generate a boolean value."""
        pass

    @abstractmethod
    def generate_date(self) -> date:
        """Generate a date value."""
        pass

    @abstractmethod
    def generate_datetime(self) -> datetime:
        """Generate a datetime value."""
        pass

    @abstractmethod
    def generate_binary(self, length: int = 64) -> bytes:
        """Generate binary data."""
        pass

    @abstractmethod
    def generate_uuid(self) -> UUID:
        """Generate a UUID."""
        pass

    @abstractmethod
    def generate_enum(self, values: list[str]) -> str:
        """Generate an enum value from the given choices."""
        pass
