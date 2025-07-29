import json
import uuid
from abc import abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import Any


class BaseFormatter:
    """Base class for handling data type formatting across exporters."""

    @staticmethod
    def format_none() -> str | None:
        """Format None values."""
        return None

    @staticmethod
    def format_datetime(value: datetime | date) -> str:
        """Format datetime and date values."""
        return value.isoformat()

    @staticmethod
    def format_uuid(value: uuid.UUID) -> str:
        """Format UUID values."""
        return str(value)

    @staticmethod
    def format_bytes(value: bytes) -> str:
        """Format bytes values."""
        return value.hex()

    @staticmethod
    def format_decimal(value: Decimal) -> float:
        """Format Decimal values."""
        return float(value)

    @staticmethod
    def format_string(value: str) -> str:
        """Format string values, removing null bytes."""
        return str(value).replace("\x00", "")

    @abstractmethod
    def format_value(
        self,
        value: (
            None
            | datetime
            | date
            | uuid.UUID
            | bytes
            | Decimal
            | dict
            | list
            | int
            | float
            | str
        ),
    ) -> None | str | float | dict | list | int:
        """Format a single value according to export format requirements.

        Args:
            value: The value to format

        Returns:
            Formatted value suitable for the target format

        """
        pass

    def format_row(
        self, row: dict[str, Any], **kwargs: dict[str, str | int | float]
    ) -> dict[str, Any]:
        """Format the provided rows with the correct format_value.

        Args:
            row: Dictionary containing row data
            **kwargs: Additional format-specific parameters

        Returns:
            Formatted row dictionary

        """
        formatted_row: dict[str, Any] = {}
        for key, value in row.items():
            try:
                formatted_row[key] = self.format_value(value)
            except Exception as e:
                formatted_row[key] = f"ERROR: {str(e)}"
        return formatted_row


class JSONFormatter(BaseFormatter):
    """Formatter for JSON exports."""

    @classmethod
    def format_value(
        cls,
        value: (
            datetime
            | date
            | uuid.UUID
            | bytes
            | Decimal
            | dict
            | list
            | int
            | float
            | str
            | None
        ),
    ) -> str | float | dict | list | int | None:
        """Format the provided values."""
        if value is None:
            return cls.format_none()
        elif isinstance(value, (datetime | date)):
            return cls.format_datetime(value)
        elif isinstance(value, uuid.UUID):
            return cls.format_uuid(value)
        elif isinstance(value, bytes):
            return cls.format_bytes(value)
        elif isinstance(value, Decimal):
            return cls.format_decimal(value)
        elif isinstance(value, (dict | list | int | float)):
            return value
        else:
            return cls.format_string(str(value))


class CSVFormatter(BaseFormatter):
    """Formatter for CSV exports."""

    @classmethod
    def format_value(
        cls,
        value: (
            datetime
            | date
            | uuid.UUID
            | bytes
            | Decimal
            | dict
            | list
            | int
            | float
            | str
            | None
        ),
    ) -> str | float | dict | list | int | None:
        """Format the provided values."""
        if value is None:
            return cls.format_none()
        elif isinstance(value, (datetime | date)):
            return cls.format_datetime(value)
        elif isinstance(value, uuid.UUID):
            return cls.format_uuid(value)
        elif isinstance(value, bytes):
            return cls.format_bytes(value)
        elif isinstance(value, Decimal):
            return cls.format_decimal(value)
        elif isinstance(value, (dict | list)):
            return json.dumps(value)
        elif isinstance(value, (int | float)):
            return value
        else:
            return cls.format_string(str(value))
