import logging
from collections.abc import Iterator
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DataChunker:
    """Handle data chunking operations."""

    def __init__(self, chunk_size: int) -> None:
        """Initialize the DataChunker with a specified chunk size."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero")
        self.chunk_size = chunk_size

    def chunk_data(self, data: list[T]) -> Iterator[list[T]]:
        """Yield chunks of data with memory cleanup."""
        total_chunks = (len(data) + self.chunk_size - 1) // self.chunk_size
        for chunk_num, i in enumerate(range(0, len(data), self.chunk_size), 1):
            chunk = data[i : i + self.chunk_size]
            logger.debug(f"Processing chunk {chunk_num}/{total_chunks}")
            yield chunk
            # Help garbage collection
            del chunk
