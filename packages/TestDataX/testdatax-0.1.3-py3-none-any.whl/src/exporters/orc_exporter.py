import logging
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.orc as po

from .base_exporter import BaseExporter
from .utils.chunker import DataChunker
from .utils.constants import (
    CHUNK_SIZE_ORC,
    DEFAULT_ORC_COMPRESSION,
    VALID_ORC_COMPRESSION,
    OrcCompression,
)

logger = logging.getLogger(__name__)


class OrcExporter(BaseExporter):
    """Exports data to ORC file format using PyArrow and Pandas."""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE_ORC,
        compression: OrcCompression = DEFAULT_ORC_COMPRESSION,
    ) -> None:
        """Initialize Exporter with specified options.

        Args:
            chunk_size: Number of rows to write at once
            compression: Compression codec
            compression_strategy: Compression strategy

        """
        if compression not in VALID_ORC_COMPRESSION:
            raise ValueError(f"Invalid compression: {compression}")

        self.chunker = DataChunker(chunk_size)
        self.compression = compression

    def _get_compressed_path(self, path: str) -> str:
        """Insert compression type into filename before extension."""
        if self.compression == "UNCOMPRESSED":
            return path
        # Remove any existing compression extension
        base = path
        for comp in VALID_ORC_COMPRESSION:
            base = base.replace(f".{comp.lower()}", "")
        # Split at last occurrence of .orc
        base = base.replace(".orc", "")
        return f"{base}.{self.compression.lower()}.orc"

    def export(
        self,
        data: list[dict[str, Any]],
        output_path: str,
        schema: dict | None = None,
    ) -> None:
        """Export data to ORC file format.

        Args:
            data: List of dictionaries containing the data to export
            output_path: Path where the ORC file will be written
            schema: Schema definition for the data (not used for ORC)

        """
        if not data:
            logger.info("No data to export")
            raise RuntimeError("No data to export")

        # Validate base path ends with .orc before adding compression
        if not output_path.endswith(".orc"):
            raise ValueError("Output path must have .orc extension")

        output_path = self._get_compressed_path(output_path)
        logger.info(f"Starting ORC export to {output_path} with {len(data)} rows")
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
                if writer is None:
                    writer = po.ORCWriter(
                        str(output_path),
                        compression=self.compression,
                    )
                writer.write(table)
            logger.info(f"Successfully exported {len(data)} rows to {output_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to write Orc file: {e}") from e
        finally:
            if writer:
                writer.close()
