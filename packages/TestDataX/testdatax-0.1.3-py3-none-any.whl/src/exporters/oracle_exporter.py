import decimal
from datetime import date, datetime
from typing import Any
from uuid import UUID

from .base_exporter import BaseExporter
from .utils.constants import DEFAULT_SCHEMA

ORACLE_TYPE_MAPPING = {
    "string": "VARCHAR2(255)",  # Oracle's Unicode string type
    "text": "CLOB",  # Oracle's large text type
    "integer": "NUMBER(10)",  # Standard integer in Oracle
    "bigint": "NUMBER(19)",  # Large integers in Oracle
    "float": "FLOAT",  # Same in Oracle
    "decimal": "NUMBER(18,2)",  # Oracle's decimal type
    "boolean": "NUMBER(1)",  # Oracle has no native boolean
    "date": "DATE",  # Same in Oracle
    "datetime": "TIMESTAMP",  # Oracle's datetime type
    "blob": "BLOB",  # Oracle's binary large object
    "uuid": "VARCHAR2(36)",  # Oracle has no native UUID
    "enum": "VARCHAR2(255)",  # Oracle has no ENUM type
}


class OracleExporter(BaseExporter):
    """Exports data to ORACLE compatible SQL file."""

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
        """Format a value for use in a ORACLE query.

        This method handles various data types and converts them to their
        appropriate string representation for use in ORACLE queries.
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
            str: The formatted value ready for use in a ORACLE query.

        Raises:
            ValueError: If the input value type is not supported.

        """
        if value is None:
            return "NULL"
        elif isinstance(value, (str)):
            return "'" + str(value).replace("'", "''") + "'"  # uses '' for escaping
        elif isinstance(value, UUID):
            return f"'{str(value)}'"
        elif isinstance(value, datetime):
            return (
                f"TO_TIMESTAMP('{value.isoformat()}', "
                f"'YYYY-MM-DD\"T\"HH24:MI:SS.FF')"
            )
        elif isinstance(value, date):
            return f"DATE '{value.isoformat()}'"
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, bytes):
            return f"HEXTORAW('{value.hex()}')"  # Oracle BLOB format
        elif isinstance(value, (int | float | decimal.Decimal)):
            return str(value)
        else:
            raise ValueError(f"Unsupported type: {type(value)}")

    def _get_column_type(self, field: dict) -> str:
        """Get the ORACLE column type based on the field type.

        Args:
            field (dict): A dictionary containing field information, including its type.
                The type can be either a string or a dictionary with a 'type' key.

        Returns:
            str: The corresponding ORACLE data type from ORACLE_TYPE_MAPPING.

        Raises:
            KeyError: If the field type is not found in ORACLE_TYPE_MAPPING.

        """
        field_type = field.get("type", "string")
        if isinstance(field_type, dict):
            field_type = field_type.get("type", "string")
        return ORACLE_TYPE_MAPPING[field_type]

    def _create_table_stmt(self, schema: dict, table_name: str = "output") -> str:
        """Generate a ORACLE CREATE TABLE statement based on provided schema.

        This method constructs a CREATE TABLE SQL statement by mapping schema field
        definitions to their corresponding ORACLE column types. For ENUM types,
        it creates a CHECK constraint to validate the values.

        Args:
            schema (dict): A dictionary defining the table schema with field names
                as keys and type definitions as values.
            table_name (str, optional): Name for the table. Defaults to "output".

        Returns:
            str: A complete ORACLE CREATE TABLE statement as a string.

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
        """Create a ORACLE INSERT statement from a dictionary of values.

        Args:
            row (dict[str, Any]): Dictionary containing column names as keys
                and values to insert
            table_name (str, optional): Name of the target table. Defaults to "output"

        Returns:
            str: Formatted ORACLE INSERT statement string

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
        """Export data to ORACLE compatible SQL file."""
        if not data:
            return

        table_name = output_path.split("/")[-1].split(".")[0]

        with open(output_path, "w") as f:
            # Always write CREATE TABLE using DEFAULT_SCHEMA if no schema provided
            schema_to_use = schema or DEFAULT_SCHEMA
            f.write(self._create_table_stmt(schema_to_use, table_name))
            for row in data:
                f.write(self._create_insert_stmt(row, table_name) + "\n")
