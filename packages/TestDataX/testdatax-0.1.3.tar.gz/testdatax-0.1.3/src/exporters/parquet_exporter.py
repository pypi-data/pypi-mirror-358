import logging
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .base_exporter import BaseExporter
from .utils.chunker import DataChunker
from .utils.constants import (
    CHUNK_SIZE_PARQUET,
    DEFAULT_PARQUET_COMPRESSION,
    VALID_PARQUET_COMPRESSION,
    ParquetCompression,
)

logger = logging.getLogger(__name__)


class ParquetExporter(BaseExporter):
    """Exporter class for writing data to Parquet format files."""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE_PARQUET,
        compression: ParquetCompression = DEFAULT_PARQUET_COMPRESSION,
    ) -> None:
        """Initialize Exporter with specified chunk size.

        Args:
            chunk_size (int, optional): Number of rows to write at once.
            Defaults to CHUNK_SIZE_PARQUET.
            compression (str, optional): Compression codec.

        """
        if compression not in VALID_PARQUET_COMPRESSION:
            raise ValueError(f"Invalid compression: {compression}")

        self.chunk_size = chunk_size
        self.compression = compression
        self.chunker = DataChunker(chunk_size)

    def _get_compressed_path(self, path: str) -> str:
        """Insert compression type into filename before extension."""
        if self.compression == "none":
            return path
        base = path
        for comp in VALID_PARQUET_COMPRESSION:
            base = base.replace(f".{comp}", "")
        base = base.replace(".parquet", "")
        return f"{base}.{self.compression}.parquet"

    def export(
        self,
        data: list[dict[str, Any]],
        output_path: str,
        schema: dict | None = None,
    ) -> None:
        """Export data to a Parquet file.

        Args:
            data: List of dictionaries containing the data to export
            output_path: Path where the Parquet file will be written
            schema: Optional dictionary defining the data schema
            chunk_size: Number of rows to write at once (default: CHUNK_SIZE_PARQUET)

        """
        if not data:
            logger.info("No data to export")
            raise RuntimeError("No data to export")

        # Validate base path ends with .parquet before adding compression
        if not output_path.endswith(".parquet"):
            raise ValueError("Output path must have .parquet extension")

        output_path = self._get_compressed_path(output_path)
        logger.info(f"Starting Parquet export to {output_path} with {len(data)} rows")
        if not isinstance(data, list):
            raise TypeError("Data must be a list of dictionaries")

        writer = None
        try:
            for i, chunk in enumerate(self.chunker.chunk_data(data), 1):
                logger.debug(f"Processing chunk {i}")
                df = pd.DataFrame(chunk)
                if "uuid" in df.columns:
                    df["uuid"] = df["uuid"].astype(str)
                table = pa.Table.from_pandas(df)
                # Initialize writer with first chunk's schema
                if writer is None:
                    writer = pq.ParquetWriter(
                        output_path,
                        table.schema,
                        compression=self.compression,
                    )
                writer.write_table(table)
            logger.info(f"Successfully exported {len(data)} rows to {output_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to write Parquet file: {e}") from e
        finally:
            if writer is not None:
                writer.close()
