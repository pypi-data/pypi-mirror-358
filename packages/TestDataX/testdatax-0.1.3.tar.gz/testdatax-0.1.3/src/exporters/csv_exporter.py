import csv
import logging
from typing import Any

import pandas as pd

from .base_exporter import BaseExporter
from .utils.chunker import DataChunker
from .utils.constants import CHUNK_SIZE_CSV
from .utils.formatters import CSVFormatter

logger = logging.getLogger(__name__)


class CsvExporter(BaseExporter):
    """Export data to CSV with support for chunked writing and data type formatting."""

    def __init__(self, chunk_size: int = CHUNK_SIZE_CSV) -> None:
        """Initialize CsvExporter with specified chunk size.

        Args:
            chunk_size (int, optional): Number of rows to write at once.
            Defaults to CHUNK_SIZE_CSV.

        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")
        self.chunk_size = chunk_size
        self.chunker = DataChunker(chunk_size)
        self.formatter = CSVFormatter()

    def export(
        self, data: list[dict[str, Any]], output_path: str, schema: dict | None = None
    ) -> None:
        """Export data to a CSV file with proper formatting and chunking.

        Args:
            data (list[dict[str, Any]]): List of dictionaries for the data to export.
            output_path (str): Path to the output CSV file.
            schema (dict | None, optional): Schema definition for the data.

        Raises:
            ValueError: If data is invalid or file operations fail.

        """
        logger.info("Starting CSV export.")

        if not data:
            if schema:
                # Write an empty file with headers if schema is provided
                pd.DataFrame(columns=list(schema.keys())).to_csv(
                    output_path,
                    index=False,
                    quoting=csv.QUOTE_NONNUMERIC,
                    quotechar='"',
                    doublequote=True,
                    lineterminator="\n",
                    encoding="utf-8",
                )
                logger.info(f"Exported an empty file with headers to {output_path}.")
            else:
                logger.warning(
                    "No data provided and no schema to write headers. Exiting."
                )
            return

        try:
            # Determine fieldnames based on schema or data keys
            if schema:
                fieldnames = list(schema.keys())
                for field in fieldnames:
                    if field not in data[0]:
                        raise ValueError(
                            f"Field '{field}' in schema is not present in data."
                        )
            else:
                fieldnames = list(data[0].keys())

            first_chunk = True
            formatted_rows = []
            for chunk in self.chunker.chunk_data(data):
                formatted_chunk = [self.formatter.format_row(row) for row in chunk]
                formatted_rows.extend(formatted_chunk)
                df = pd.DataFrame(formatted_chunk, columns=fieldnames)

                # Write the data to CSV in chunks
                mode = "w" if first_chunk else "a"
                header = first_chunk
                df.to_csv(  # type: ignore
                    output_path,
                    index=False,  # Do not write the index column
                    quoting=csv.QUOTE_NONNUMERIC,  # Quote non-numeric fields
                    quotechar='"',  # Use double quotes for quoting
                    doublequote=True,  # Escape double quotes by doubling
                    lineterminator="\n",  # Use Unix-style line endings
                    encoding="utf-8",  # Use UTF-8 encoding
                    mode=mode,  # Write mode ('w', else 'a')
                    header=header,  # Include header only in first chunk
                )
                first_chunk = False

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
            raise ValueError(f"Export failed: {str(e)}") from e
