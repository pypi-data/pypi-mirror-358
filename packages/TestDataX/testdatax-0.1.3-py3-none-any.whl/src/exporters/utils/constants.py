from typing import Literal, cast

# Export related constants
EXPORT_FORMATS = ["csv", "json", "parquet", "orc", "mysql", "mssql", "oracle"]
EXPORT_PATTERNS = "^(csv|json|parquet|orc|mysql|mssql|oracle)$"

# Chunk size for exporting data
CHUNK_SIZE = 10000
CHUNK_SIZE_JSON = CHUNK_SIZE
CHUNK_SIZE_CSV = CHUNK_SIZE
CHUNK_SIZE_PARQUET = CHUNK_SIZE
CHUNK_SIZE_ORC = CHUNK_SIZE

# ORC compression types
OrcCompression = Literal["UNCOMPRESSED", "SNAPPY", "ZLIB", "LZ4", "ZSTD"]
OrcStrategy = Literal["SPEED", "COMPRESSION"]

# Valid compression options
VALID_ORC_COMPRESSION: list[OrcCompression] = cast(
    list[OrcCompression], ["UNCOMPRESSED", "SNAPPY", "ZLIB", "LZ4", "ZSTD"]
)
VALID_ORC_STRATEGIES: list[OrcStrategy] = cast(
    list[OrcStrategy], ["SPEED", "COMPRESSION"]
)

# Default settings
DEFAULT_ORC_COMPRESSION: OrcCompression = "SNAPPY"
DEFAULT_ORC_STRATEGY: OrcStrategy = "SPEED"

# Parquet compression types - matching pyarrow's expected values
ParquetCompression = Literal["none", "snappy", "gzip", "brotli", "lz4", "zstd"]

# Valid compression options for Parquet
VALID_PARQUET_COMPRESSION: list[ParquetCompression] = cast(
    list[ParquetCompression], ["none", "snappy", "gzip", "brotli", "lz4", "zstd"]
)

# Default compression for Parquet
DEFAULT_PARQUET_COMPRESSION: ParquetCompression = "snappy"

# Default schema for data generation
DEFAULT_SCHEMA = {
    "username": {"type": "string", "faker": "name"},
    "bio": "text",
    "age": "integer",
    "emp_number": "bigint",
    "height": "float",
    "salary": "decimal",
    "is_active": "boolean",
    "signup_date": "date",
    "signup_dt": "datetime",
    "profile_picture": "blob",
    "uuid": "uuid",
    "user_enum": {"type": "enum", "values": ["active", "inactive", "pending"]},
}
