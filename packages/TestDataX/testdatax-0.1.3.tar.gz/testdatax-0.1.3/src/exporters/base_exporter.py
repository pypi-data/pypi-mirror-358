from abc import ABC, abstractmethod
from typing import Any


class BaseExporter(ABC):
    """Base class for all data exporters.

    A common interface for data export operations.
    """

    @abstractmethod
    def export(
        self, data: list[dict[str, Any]], output_path: str, schema: dict | None = None
    ) -> None:
        """Export data to a specified output path.

        Args:
            data: List of dictionaries containing the data to export
            output_path: Path where the exported data should be saved
            schema: Dictionary containing schema definition

        """
        pass
