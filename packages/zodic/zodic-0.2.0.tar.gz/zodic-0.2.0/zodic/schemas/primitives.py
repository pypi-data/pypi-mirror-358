"""Primitive type schemas for Zodic."""

import re
from datetime import date, datetime
from typing import Any, Optional, Pattern, TypeVar, Union, cast

from ..core.base import Schema
from ..core.errors import ZodError, custom_issue, invalid_type_issue
from ..core.types import ValidationContext

T = TypeVar("T")


class StringSchema(Schema[str]):
    """Schema for string validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_length: Optional[int] = None
        self._max_length: Optional[int] = None
        self._pattern: Optional[Pattern[str]] = None
        self._email_validation = False
        self._url_validation = False

    def _parse_value(self, value: Any, ctx: ValidationContext) -> str:
        """Parse and validate a string value."""
        if not isinstance(value, str):
            raise ZodError([invalid_type_issue(value, "string", ctx)])

        # Length validations
        if self._min_length is not None and len(value) < self._min_length:
            raise ZodError(
                [
                    custom_issue(
                        f"String must be at least {self._min_length} characters long",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_length is not None and len(value) > self._max_length:
            raise ZodError(
                [
                    custom_issue(
                        f"String must be at most {self._max_length} characters long",
                        ctx,
                        value,
                    )
                ]
            )

        # Pattern validation
        if self._pattern is not None and not self._pattern.match(value):
            raise ZodError(
                [
                    custom_issue(
                        f"String does not match pattern {self._pattern.pattern}",
                        ctx,
                        value,
                    )
                ]
            )

        # Email validation
        if self._email_validation:
            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_pattern.match(value):
                raise ZodError([custom_issue("Invalid email format", ctx, value)])

        # URL validation
        if self._url_validation:
            url_pattern = re.compile(
                r"^https?://"  # http:// or https://
                r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
                r"localhost|"  # localhost...
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
                r"(?::\d+)?"  # optional port
                r"(?:/?|[/?]\S+)$",
                re.IGNORECASE,
            )
            if not url_pattern.match(value):
                raise ZodError([custom_issue("Invalid URL format", ctx, value)])

        return value

    def min(self, length: int) -> "StringSchema":
        """Set minimum length constraint."""
        new_schema = self._clone()
        new_schema._min_length = length
        return new_schema

    def max(self, length: int) -> "StringSchema":
        """Set maximum length constraint."""
        new_schema = self._clone()
        new_schema._max_length = length
        return new_schema

    def length(self, length: int) -> "StringSchema":
        """Set exact length constraint."""
        return self.min(length).max(length)

    def regex(self, pattern: Union[str, Pattern[str]]) -> "StringSchema":
        """Set regex pattern constraint."""
        new_schema = self._clone()
        if isinstance(pattern, str):
            new_schema._pattern = re.compile(pattern)
        else:
            new_schema._pattern = pattern
        return new_schema

    def email(self) -> "StringSchema":
        """Validate as email format."""
        new_schema = self._clone()
        new_schema._email_validation = True
        return new_schema

    def url(self) -> "StringSchema":
        """Validate as URL format."""
        new_schema = self._clone()
        new_schema._url_validation = True
        return new_schema

    def _clone(self) -> "StringSchema":
        """Create a copy of this schema."""
        new_schema = cast("StringSchema", super()._clone())
        new_schema._min_length = self._min_length
        new_schema._max_length = self._max_length
        new_schema._pattern = self._pattern
        new_schema._email_validation = self._email_validation
        new_schema._url_validation = self._url_validation
        return new_schema


class NumberSchema(Schema[Union[int, float]]):
    """Schema for number validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_value: Optional[float] = None
        self._max_value: Optional[float] = None
        self._int_only = False
        self._positive_only = False

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Union[int, float]:
        """Parse and validate a number value."""
        # Reject boolean values (which are technically int in Python)
        if isinstance(value, bool):
            raise ZodError([invalid_type_issue(value, "number", ctx)])

        if not isinstance(value, (int, float)):
            raise ZodError([invalid_type_issue(value, "number", ctx)])

        # Check for NaN and infinity
        if isinstance(value, float):
            if value != value:  # NaN check
                raise ZodError([custom_issue("Number cannot be NaN", ctx, value)])
            if value == float("inf") or value == float("-inf"):
                raise ZodError([custom_issue("Number cannot be infinite", ctx, value)])

        # Integer constraint
        if self._int_only and not isinstance(value, int):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                raise ZodError([custom_issue("Expected integer", ctx, value)])

        # Positive validation (more precise than min_value)
        if self._positive_only and value <= 0:
            raise ZodError([custom_issue("Number must be positive", ctx, value)])

        # Range validations
        if self._min_value is not None and value < self._min_value:
            raise ZodError(
                [
                    custom_issue(
                        f"Number must be greater than or equal to {self._min_value}",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_value is not None and value > self._max_value:
            raise ZodError(
                [
                    custom_issue(
                        f"Number must be less than or equal to {self._max_value}",
                        ctx,
                        value,
                    )
                ]
            )

        return cast(Union[int, float], value)

    def min(self, value: float) -> "NumberSchema":
        """Set minimum value constraint."""
        new_schema = self._clone()
        new_schema._min_value = value
        return new_schema

    def max(self, value: float) -> "NumberSchema":
        """Set maximum value constraint."""
        new_schema = self._clone()
        new_schema._max_value = value
        return new_schema

    def int(self) -> "NumberSchema":
        """Require the number to be an integer."""
        new_schema = self._clone()
        new_schema._int_only = True
        return new_schema

    def positive(self) -> "NumberSchema":
        """Require the number to be positive (> 0)."""
        new_schema = self._clone()
        new_schema._positive_only = True
        return new_schema

    def negative(self) -> "NumberSchema":
        """Require the number to be negative (< 0)."""
        return self.max(-0.000001)  # Slightly below 0 to exclude 0

    def nonnegative(self) -> "NumberSchema":
        """Require the number to be non-negative (>= 0)."""
        return self.min(0)

    def _clone(self) -> "NumberSchema":
        """Create a copy of this schema."""
        new_schema = cast("NumberSchema", super()._clone())
        new_schema._min_value = self._min_value
        new_schema._max_value = self._max_value
        new_schema._int_only = self._int_only
        new_schema._positive_only = self._positive_only
        return new_schema


class BooleanSchema(Schema[bool]):
    """Schema for boolean validation."""

    def _parse_value(self, value: Any, ctx: ValidationContext) -> bool:
        """Parse and validate a boolean value."""
        if not isinstance(value, bool):
            raise ZodError([invalid_type_issue(value, "boolean", ctx)])
        return value


class NoneSchema(Schema[None]):
    """Schema for None/null validation."""

    def _parse_value(self, value: Any, ctx: ValidationContext) -> None:
        """Parse and validate a None value."""
        if value is not None:
            raise ZodError([invalid_type_issue(value, "null", ctx)])
        return None


# Factory functions (following Zod's API)
def string() -> StringSchema:
    """Create a string schema."""
    return StringSchema()


def number() -> NumberSchema:
    """Create a number schema."""
    return NumberSchema()


def boolean() -> BooleanSchema:
    """Create a boolean schema."""
    return BooleanSchema()


def none() -> NoneSchema:
    """Create a None schema."""
    return NoneSchema()


class LiteralSchema(Schema[T]):
    """Schema for literal value validation."""

    def __init__(self, value: T) -> None:
        super().__init__()
        self.literal_value = value

    def _parse_value(self, value: Any, ctx: ValidationContext) -> T:
        """Parse and validate a literal value."""
        if value != self.literal_value:
            raise ZodError(
                [
                    custom_issue(
                        f"Expected literal value {repr(self.literal_value)}, received {repr(value)}",
                        ctx,
                        value,
                    )
                ]
            )
        return self.literal_value

    def _clone(self) -> "LiteralSchema[T]":
        """Create a copy of this schema."""
        new_schema = cast("LiteralSchema[T]", super()._clone())
        new_schema.literal_value = self.literal_value
        return new_schema


def literal(value: T) -> LiteralSchema[T]:
    """Create a literal schema."""
    return LiteralSchema(value)


class DateSchema(Schema[date]):
    """Schema for date validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_date: Optional[date] = None
        self._max_date: Optional[date] = None

    def _parse_value(self, value: Any, ctx: ValidationContext) -> date:
        """Parse and validate a date value."""
        parsed_date = None

        if isinstance(value, datetime):
            # Convert datetime to date
            parsed_date = value.date()
        elif isinstance(value, date):
            parsed_date = value
        elif isinstance(value, str):
            # Try to parse ISO format date string
            try:
                parsed_date = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                ).date()
            except ValueError:
                try:
                    # Try common date formats
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                        try:
                            parsed_date = datetime.strptime(value, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError("No valid date format found")
                except ValueError:
                    raise ZodError([custom_issue("Invalid date format", ctx, value)])
        else:
            raise ZodError([invalid_type_issue(value, "date", ctx)])

        # Validate date range for all parsed dates
        if self._min_date is not None and parsed_date < self._min_date:
            raise ZodError(
                [
                    custom_issue(
                        f"Date must be after {self._min_date}",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_date is not None and parsed_date > self._max_date:
            raise ZodError(
                [
                    custom_issue(
                        f"Date must be before {self._max_date}",
                        ctx,
                        value,
                    )
                ]
            )

        return parsed_date

    def min(self, min_date: date) -> "DateSchema":
        """Set minimum date constraint."""
        new_schema = self._clone()
        new_schema._min_date = min_date
        return new_schema

    def max(self, max_date: date) -> "DateSchema":
        """Set maximum date constraint."""
        new_schema = self._clone()
        new_schema._max_date = max_date
        return new_schema

    def _clone(self) -> "DateSchema":
        """Create a copy of this schema."""
        new_schema = cast("DateSchema", super()._clone())
        new_schema._min_date = self._min_date
        new_schema._max_date = self._max_date
        return new_schema


class DateTimeSchema(Schema[datetime]):
    """Schema for datetime validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_datetime: Optional[datetime] = None
        self._max_datetime: Optional[datetime] = None

    def _parse_value(self, value: Any, ctx: ValidationContext) -> datetime:
        """Parse and validate a datetime value."""
        if isinstance(value, datetime):
            parsed_datetime = value
        elif isinstance(value, str):
            # Try to parse ISO format datetime string
            try:
                parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
                # Convert to naive datetime if it has timezone info
                if parsed_datetime.tzinfo is not None:
                    parsed_datetime = parsed_datetime.replace(tzinfo=None)
            except ValueError:
                try:
                    # Try common datetime formats
                    for fmt in [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S",
                        "%m/%d/%Y %H:%M:%S",
                    ]:
                        try:
                            parsed_datetime = datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError("No valid datetime format found")
                except ValueError:
                    raise ZodError(
                        [custom_issue("Invalid datetime format", ctx, value)]
                    )
        else:
            raise ZodError([invalid_type_issue(value, "datetime", ctx)])

        # Validate datetime range
        if self._min_datetime is not None and parsed_datetime < self._min_datetime:
            raise ZodError(
                [
                    custom_issue(
                        f"Datetime must be after {self._min_datetime}",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_datetime is not None and parsed_datetime > self._max_datetime:
            raise ZodError(
                [
                    custom_issue(
                        f"Datetime must be before {self._max_datetime}",
                        ctx,
                        value,
                    )
                ]
            )

        return parsed_datetime

    def min(self, min_datetime: datetime) -> "DateTimeSchema":
        """Set minimum datetime constraint."""
        new_schema = self._clone()
        new_schema._min_datetime = min_datetime
        return new_schema

    def max(self, max_datetime: datetime) -> "DateTimeSchema":
        """Set maximum datetime constraint."""
        new_schema = self._clone()
        new_schema._max_datetime = max_datetime
        return new_schema

    def _clone(self) -> "DateTimeSchema":
        """Create a copy of this schema."""
        new_schema = cast("DateTimeSchema", super()._clone())
        new_schema._min_datetime = self._min_datetime
        new_schema._max_datetime = self._max_datetime
        return new_schema


def date_schema() -> DateSchema:
    """Create a date schema."""
    return DateSchema()


def datetime_schema() -> DateTimeSchema:
    """Create a datetime schema."""
    return DateTimeSchema()
