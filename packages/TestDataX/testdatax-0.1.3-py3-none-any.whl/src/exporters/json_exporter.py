import json
import logging
from typing import Any

from .base_exporter import BaseExporter
from .utils.chunker import DataChunker
from .utils.constants import CHUNK_SIZE_JSON
from .utils.formatters import JSONFormatter

logger = logging.getLogger(__name__)


class JsonExporter(BaseExporter):
    """Export data to JSON with support for chunked writing and data type formatting."""

    def __init__(self, chunk_size: int = CHUNK_SIZE_JSON) -> None:
        """Initialize the JSON exporter with a specified chunk size.

        Args:
            chunk_size (int): Number of records to process at once.
            Defaults to CHUNK_SIZE_JSON.

        Raises:
            ValueError: If chunk_size is less than or equal to zero.

        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")
        self.chunk_size = chunk_size
        self.chunker = DataChunker(chunk_size)
        self.formatter = JSONFormatter()

    def export(
        self, data: list[dict[str, Any]], output_path: str, schema: dict | None = None
    ) -> None:
        """Export data to a JSON file with proper formatting and chunking.

        Args:
            data (list[dict[str, Any]]): List of dictionaries for the data to export.
            output_path (str): Path to the output JSON file.
            schema (dict | None, optional): Schema definition for the data.

        Raises:
            ValueError: If data is invalid or file operations fail.

        """
        logger.info("Starting JSON export.")

        if not data:
            if schema:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
                logger.info("Exported empty array.")
            return

        try:
            # Validate schema if provided
            if schema:
                fieldnames = list(schema.keys())
                for field in fieldnames:
                    if field not in data[0]:
                        raise ValueError(
                            f"Field '{field}' in schema is not present in data."
                        )
            # Format the data and write it in chunks to the output file
            all_formatted_rows = []
            for chunk in self.chunker.chunk_data(data):
                formatted_chunk = [self.formatter.format_row(row) for row in chunk]
                all_formatted_rows.extend(formatted_chunk)

            # Write the complete file with proper formatting using json.dumps
            with open(output_path, "w", encoding="utf-8") as f:
                json_str = json.dumps(all_formatted_rows, indent=4)
                f.write(json_str)

            logger.info(f"Successfully exported {len(data)} rows to {output_path}.")

        except UnicodeEncodeError as e:
            logger.error(f"Encoding error: {e}")
            raise ValueError(f"Encoding error: {str(e)}") from e
        except OSError as e:
            logger.error(f"File operation error: {e}")
            raise ValueError(f"File operation error: {str(e)}") from e
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
