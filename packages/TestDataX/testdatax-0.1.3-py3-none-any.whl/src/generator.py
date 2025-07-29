from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from faker import Faker

from .providers import DataProvider, FakerProvider
from .schemas import DataType, FieldSchema


class DataGenerator:
    """The DataGenerator class generates synthetic data based on the provided field schemas.

    Supported data types:
        - STRING: Generates usernames
        - TEXT: Generates paragraphs of text
        - INTEGER: Generates integers between 0 and 100
        - BIGINT: Generates large integers between 0 and 9999999999
        - FLOAT: Generates floating point numbers with 2 decimal places
        - DECIMAL: Generates Decimal numbers with 2 decimal places
        - BOOLEAN: Generates True/False values
        - DATE: Generates date objects
        - DATETIME: Generates datetime objects
        - BLOB: Generates binary data
        - UUID: Generates UUID objects
        - ENUM: Generates values from provided enum_values list

    """  # noqa: E501

    def __init__(self, provider: DataProvider | None = None) -> None:
        """Initialize the DataGenerator with Faker instance and type generator mappings.

        The constructor initializes the Faker instance and creates a mapping of DataType
        enums to their corresponding generator methods.
        """
        self.provider = provider or FakerProvider()
        self.faker = Faker()
        self.type_generators = {
            DataType.STRING: self._generate_string,
            DataType.TEXT: self._generate_text,
            DataType.INTEGER: self._generate_integer,
            DataType.BIGINT: self._generate_bigint,
            DataType.FLOAT: self._generate_float,
            DataType.DECIMAL: self._generate_decimal,
            DataType.BOOLEAN: self._generate_boolean,
            DataType.DATE: self._generate_date,
            DataType.DATETIME: self._generate_datetime,
            DataType.BLOB: self._generate_blob,
            DataType.UUID: self._generate_uuid,
            DataType.ENUM: self._generate_enum,
        }

    def generate_data(
        self, fields: list[FieldSchema], count: int
    ) -> list[dict[str, Any]]:
        """Generate data based on the provided schema and count."""
        data = []
        for _ in range(count):
            row = {}
            for field in fields:
                generator = self.type_generators[field.type]
                row[field.name] = generator(field)
            data.append(row)
        return data

    def _generate_string(self, field: FieldSchema) -> str:
        provider_value = str(field.value_provider) if field.value_provider else "name"
        return self.provider.generate_string(value_provider=provider_value)

    def _generate_text(self, field: FieldSchema) -> str:
        return self.provider.generate_text()

    def _generate_integer(self, field: FieldSchema) -> int:
        min_val = (
            int(field.min_value)
            if hasattr(field, "min_value") and field.min_value is not None
            else 0
        )
        max_val = (
            int(field.max_value)
            if hasattr(field, "max_value") and field.max_value is not None
            else 100
        )
        return self.provider.generate_integer(
            min_value=min_val,
            max_value=max_val,
        )

    def _generate_bigint(self, field: FieldSchema) -> int:
        return self.faker.random_int(min=0, max=9999999999)

    def _generate_float(self, field: FieldSchema) -> float:
        return self.faker.pyfloat(right_digits=2)

    def _generate_decimal(self, field: FieldSchema) -> Decimal:
        return self.provider.generate_decimal()

    def _generate_boolean(self, field: FieldSchema) -> bool:
        return self.provider.generate_boolean()

    def _generate_date(self, field: FieldSchema) -> date:
        return self.provider.generate_date()

    def _generate_datetime(self, field: FieldSchema) -> datetime:
        return self.provider.generate_datetime()

    def _generate_blob(self, field: FieldSchema) -> bytes:
        return self.provider.generate_binary()

    def _generate_uuid(self, field: FieldSchema) -> UUID:
        return self.provider.generate_uuid()

    def _generate_enum(self, field: FieldSchema) -> str:
        if not field.enum_values:
            raise ValueError(f"Enum field {field.name} must have values defined")
        return self.provider.generate_enum(field.enum_values)
