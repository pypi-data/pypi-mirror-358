import decimal
from datetime import date, datetime
from typing import Any
from uuid import UUID

from .base_exporter import BaseExporter
from .utils.constants import DEFAULT_SCHEMA

MSSQL_TYPE_MAPPING = {
    "string": "NVARCHAR(255)",  # Unicode string support
    "text": "NVARCHAR(MAX)",  # Unicode text, replaces TEXT which is deprecated
    "integer": "INT",  # Same as MSSQL
    "bigint": "BIGINT",  # Same as MSSQL
    "float": "FLOAT",  # Same as MSSQL
    "decimal": "DECIMAL(18,2)",  # Same as MSSQL
    "boolean": "BIT",  # MSSQL uses BIT instead of TINYINT for boolean
    "date": "DATE",  # Same as MSSQL
    "datetime": "DATETIME2",  # More precise than DATETIME
    "blob": "VARBINARY(MAX)",  # MSSQL equivalent for BLOB
    "uuid": "UNIQUEIDENTIFIER",  # Native GUID/UUID type in MSSQL
    "enum": "NVARCHAR(255)",  # MSSQL doesn't have ENUM, use NVARCHAR instead
}


class MssqlExporter(BaseExporter):
    """Exports data to MSSQL compatible SQL file."""

    def _format_value(
        self,
        value: (
            None
            | str
            | UUID
            | datetime
            | date
            | bool
            | bytes
            | int
            | float
            | decimal.Decimal
        ),
    ) -> str:
        """Format a value for use in a MSSQL query.

        This method handles various data types and converts them to their
        appropriate string representation for use in MSSQL queries.
        It includes proper escaping for special characters in strings.

        Args:
            value: The value to format. Can be one of the following types:
                - None: Converted to 'NULL'
                - str: Escaped and wrapped in single quotes
                - UUID: Converted to string, escaped and wrapped in single quotes
                - datetime: Converted to ISO format string and wrapped in single quotes
                - date: Converted to ISO format string and wrapped in single quotes
                - bool: Converted to '1' for True or '0' for False
                - bytes: Use 0x prefix for hexadecimal to binary conversion
                - int: Converted to string representation
                - float: Converted to string representation
                - decimal.Decimal: Converted to string representation

        Returns:
            str: The formatted value ready for use in a MSSQL query.

        Raises:
            ValueError: If the input value type is not supported.

        """
        if value is None:
            return "NULL"
        elif isinstance(value, (str | UUID)):
            return "'" + str(value).replace("'", "\\'").replace("\n", "\\n") + "'"
        elif isinstance(value, (datetime | date)):
            return f"'{value.isoformat()}'"
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, bytes):
            return f"0x{value.hex()}"
        elif isinstance(value, (int | float | decimal.Decimal)):
            return str(value)
        else:
            raise ValueError(f"Unsupported type: {type(value)}")

    def _get_column_type(self, field: dict) -> str:
        """Get the MSSQL column type based on the field type.

        Args:
            field (dict): A dictionary containing field information, including its type.
                The type can be either a string or a dictionary with a 'type' key.

        Returns:
            str: The corresponding MSSQL data type from MSSQL_TYPE_MAPPING.

        Raises:
            KeyError: If the field type is not found in MSSQL_TYPE_MAPPING.

        """
        field_type = field.get("type", "string")
        if isinstance(field_type, dict):
            field_type = field_type.get("type", "string")
        return MSSQL_TYPE_MAPPING[field_type]

    def _create_table_stmt(self, schema: dict, table_name: str = "output") -> str:
        """Generate a MSSQL CREATE TABLE statement based on provided schema.

        This method constructs a CREATE TABLE SQL statement by mapping schema field
        definitions to their corresponding MSSQL column types. For ENUM types,
        it creates a CHECK constraint to validate the values.

        Args:
            schema (dict): A dictionary defining the table schema with field names
                as keys and type definitions as values.
            table_name (str, optional): Name for the table. Defaults to "output".

        Returns:
            str: A complete MSSQL CREATE TABLE statement as a string.

        Example:
            schema = {
                "id": "int",
                "status": {"type": "enum", "values": ["active", "inactive"]}
            }
            result = _create_table_stmt(schema, "users")
            # Returns: CREATE TABLE users (
            #     id INT NULL,
            #     status NVARCHAR(255) NULL CHECK (status IN ('active','inactive'))
            # );

        """
        columns = []
        check_constraints = []

        for field_name, field_def in schema.items():
            field_type_dict = (
                field_def if isinstance(field_def, dict) else {"type": field_def}
            )
            sql_type = self._get_column_type(field_type_dict)

            if (
                isinstance(field_def, dict)
                and field_def.get("type") == "enum"
                and "values" in field_def
            ):
                values = "','".join(field_def["values"])
                check_constraints.append(f"CHECK ({field_name} IN ('{values}'))")

            columns.append(f"    {field_name} {sql_type} NULL")

        # Combine columns and check constraints
        return (
            f"CREATE TABLE {table_name} (\n"
            + ",\n".join(columns)
            + (
                (",\n    " + ",\n    ".join(check_constraints))
                if check_constraints
                else ""
            )
            + "\n);\n\n"
        )

    def _create_insert_stmt(
        self, row: dict[str, Any], table_name: str = "output"
    ) -> str:
        """Create a MSSQL INSERT statement from a dictionary of values.

        Args:
            row (dict[str, Any]): Dictionary containing column names as keys
                and values to insert
            table_name (str, optional): Name of the target table. Defaults to "output"

        Returns:
            str: Formatted MSSQL INSERT statement string

        Example:
            >>> row = {"id": 1, "name": "test"}
            >>> _create_insert_stmt(row, "users")
            'INSERT INTO users (id, name) VALUES (1, "test");'

        """
        columns = ", ".join(row.keys())
        values = ", ".join(self._format_value(v) for v in row.values())
        return f"INSERT INTO {table_name} ({columns}) VALUES ({values});"

    def export(
        self, data: list[dict[str, Any]], output_path: str, schema: dict | None = None
    ) -> None:
        """Export data to MSSQL compatible SQL file."""
        if not data:
            return

        table_name = output_path.split("/")[-1].split(".")[0]

        with open(output_path, "w") as f:
            # Always write CREATE TABLE using DEFAULT_SCHEMA if no schema provided
            schema_to_use = schema or DEFAULT_SCHEMA
            f.write(self._create_table_stmt(schema_to_use, table_name))
            for row in data:
                f.write(self._create_insert_stmt(row, table_name) + "\n")
