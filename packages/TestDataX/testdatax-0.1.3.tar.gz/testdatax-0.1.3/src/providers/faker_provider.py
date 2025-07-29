from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from faker import Faker

from .base import DataProvider


class FakerProvider(DataProvider):
    """FakerProvider generates fake data using the Faker library."""

    def __init__(self) -> None:
        """Initialize the FakerProvider with a Faker instance."""
        self.faker = Faker()

    def generate_string(self, **kwargs: str) -> str:
        """Generate a fake string using the specified Faker provider."""
        provider = kwargs.get("value_provider") or "name"
        return str(getattr(self.faker, provider)())

    def generate_text(self, **kwargs: str) -> str:
        """Generate a fake text string."""
        return self.faker.text()

    def generate_integer(
        self, min_value: int | None = None, max_value: int | None = None
    ) -> int:
        """Generate a fake integer within the specified range."""
        min_val = min_value if min_value is not None else 0
        max_val = max_value if max_value is not None else 100
        return self.faker.pyint(min_value=min_val, max_value=max_val)

    def generate_decimal(self, **kwargs: Decimal) -> Decimal:
        """Generate a fake decimal number."""
        return Decimal(str(self.faker.pyfloat(right_digits=2)))

    def generate_boolean(self) -> bool:
        """Generate a fake boolean value."""
        return self.faker.boolean()

    def generate_date(self) -> date:
        """Generate a fake date object."""
        return self.faker.date_object()

    def generate_datetime(self) -> datetime:
        """Generate a fake datetime object."""
        return self.faker.date_time()

    def generate_binary(self, length: int = 64) -> bytes:
        """Generate a fake binary string of the specified length."""
        return self.faker.binary(length=length)

    def generate_uuid(self) -> UUID:
        """Generate a fake UUID."""
        uuid_value = self.faker.uuid4()
        if isinstance(uuid_value, UUID):
            return uuid_value
        return UUID(str(uuid_value))

    def generate_enum(self, values: list[str]) -> str:
        """Generate a fake value from the given list of values."""
        if not values:
            raise ValueError("Enum values cannot be empty")
        return self.faker.random_element(values)
