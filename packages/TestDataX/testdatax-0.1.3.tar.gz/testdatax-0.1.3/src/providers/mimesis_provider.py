from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from mimesis import Address, Cryptographic, Datetime, Locale, Numeric, Person, Text
from mimesis.random import Random

from .base import DataProvider


class MimesisProvider(DataProvider):
    """MimesisProvider generates fake data using the Mimesis library."""

    def __init__(self, locale: Locale = Locale.EN) -> None:
        """Initialize the MimesisProvider with a specific locale."""
        self.locale = locale
        self.person = Person(locale=locale)
        self.address = Address(locale=locale)
        self.text = Text(locale=locale)
        self.numeric = Numeric()
        self.datetime = Datetime(locale=locale)
        self.crypto = Cryptographic()
        self.random = Random()

    def generate_string(self, **kwargs: str) -> str:
        """Generate a fake string using the specified provider."""
        provider = kwargs.get("value_provider") or "name"

        # Map common Faker providers to Mimesis equivalents
        provider_map = {
            "name": lambda: self.person.full_name(),
            "first_name": lambda: self.person.first_name(),
            "last_name": lambda: self.person.last_name(),
            "email": lambda: self.person.email(),
            "username": lambda: self.person.username(),
            "phone_number": lambda: self.person.telephone(),
            "address": lambda: self.address.address(),
            "company": lambda: self.person.occupation(),
            "word": lambda: self.text.word(),
            "sentence": lambda: self.text.sentence(),
        }

        generator = provider_map.get(provider, lambda: self.person.full_name())
        return str(generator())

    def generate_text(self, **kwargs: str) -> str:
        """Generate a fake text string."""
        return str(self.text.text(quantity=1))

    def generate_integer(
        self, min_value: int | None = None, max_value: int | None = None
    ) -> int:
        """Generate a fake integer within the specified range."""
        min_val = min_value if min_value is not None else 0
        max_val = max_value if max_value is not None else 100
        return int(self.numeric.integer_number(start=min_val, end=max_val))

    def generate_decimal(self, **kwargs: Decimal) -> Decimal:
        """Generate a fake decimal number."""
        float_val = self.numeric.float_number(start=0.0, end=999999.99)
        return Decimal(f"{float_val:.2f}")

    def generate_boolean(self) -> bool:
        """Generate a fake boolean value."""
        return bool(self.random.choice([True, False]))

    def generate_date(self) -> date:
        """Generate a fake date object."""
        return self.datetime.date()

    def generate_datetime(self) -> datetime:
        """Generate a fake datetime object."""
        return self.datetime.datetime()

    def generate_binary(self, length: int = 64) -> bytes:
        """Generate a fake binary string of the specified length."""
        return bytes(self.random.randbytes(length))

    def generate_uuid(self) -> UUID:
        """Generate a fake UUID."""
        return UUID(self.crypto.uuid())

    def generate_enum(self, values: list[str]) -> str:
        """Generate a fake value from the given list of values."""
        if not values:
            raise ValueError("Enum values cannot be empty")
        return str(self.random.choice(values))
