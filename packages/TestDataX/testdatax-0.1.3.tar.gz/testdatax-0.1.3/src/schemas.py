from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .exporters.utils.constants import EXPORT_PATTERNS


class DataType(str, Enum):
    """An enumeration class for different data types commonly used in database schemas.

    A comprehensive set of data types that can be used to define the structure of
    generated data in various database contexts.

    Attributes:
        STRING: Represents a string data type for short character sequences
        TEXT: Represents a text data type for longer character sequences
        INTEGER: Represents a standard integer data type
        BIGINT: Represents a large integer data type
        FLOAT: Represents a floating-point number data type
        DECIMAL: Represents a precise decimal number data type
        BOOLEAN: Represents a boolean (True/False) data type
        DATE: Represents a date data type
        DATETIME: Represents a date and time data type
        BLOB: Represents a binary large object data type
        UUID: Represents a universally unique identifier data type
        ENUM: Represents an enumerated data type

    """

    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    BIGINT = "bigint"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    BLOB = "blob"
    UUID = "uuid"
    ENUM = "enum"


class FieldSchema(BaseModel):
    """Defines the schema for a single field in the data generation configuration.

    This class represents the structure and constraints for generating field values.
    """

    name: str
    type: DataType
    enum_values: list[str] | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    right_digits: int | None = None
    value_provider: str | None = None
    pattern: str | None = None


class GeneratorConfig(BaseModel):
    """A configuration class for data generation.

    This class defines the structure and parameters needed for generating synthetic
    data.

    Attributes:
        fields (list[FieldSchema]): List of field schemas defining the structure of
        data to generate.

        row_count (int): Number of rows/records to generate.
        export_format (str): Format for exporting generated data. Must match defined
        export patterns.
        output_path (str): File path where the generated data will be saved.

    """

    fields: list[FieldSchema]
    row_count: int
    export_format: str = Field(..., pattern=EXPORT_PATTERNS)
    output_path: str
