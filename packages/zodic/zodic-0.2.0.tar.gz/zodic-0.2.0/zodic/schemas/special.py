"""Special schema types for Zodic."""

from typing import Any, List, TypeVar, Union

from ..core.base import Schema
from ..core.errors import ZodError, custom_issue
from ..core.types import ValidationContext

T = TypeVar("T")
U = TypeVar("U")


class OptionalSchema(Schema[Union[T, None]]):
    """Schema wrapper for optional values."""

    def __init__(self, inner_schema: Schema[T]) -> None:
        super().__init__()
        self.inner_schema = inner_schema
        self._optional = True

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Union[T, None]:
        """Parse an optional value."""
        from ..core.base import UNDEFINED

        if value is None or value is UNDEFINED:
            return None

        return self.inner_schema._parse_value(value, ctx)


class NullableSchema(Schema[Union[T, None]]):
    """Schema wrapper for nullable values."""

    def __init__(self, inner_schema: Schema[T]) -> None:
        super().__init__()
        self.inner_schema = inner_schema
        self._nullable = True

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Union[T, None]:
        """Parse a nullable value."""
        if value is None:
            return None

        return self.inner_schema._parse_value(value, ctx)


class UnionSchema(Schema[Union[T, U]]):
    """Schema for union types (OR validation)."""

    def __init__(self, schemas: List[Schema[Any]]) -> None:
        super().__init__()
        self.schemas = schemas

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Any:
        """Parse a union value by trying each schema."""
        if not self.schemas:
            raise ZodError(
                [custom_issue("Union must have at least one schema", ctx, value)]
            )

        errors: List[ZodError] = []

        for schema in self.schemas:
            result = schema.safe_parse(value)
            if result["success"]:
                return result["data"]
            else:
                errors.append(result["error"])

        # If no schema matched, create a comprehensive error
        error_messages = []
        for i, error in enumerate(errors):
            error_messages.append(f"Option {i + 1}: {str(error)}")

        combined_message = "Value did not match any union option:\n" + "\n".join(
            error_messages
        )
        raise ZodError([custom_issue(combined_message, ctx, value)])


# Factory functions
def optional(schema: Schema[T]) -> OptionalSchema[T]:
    """Create an optional schema."""
    return OptionalSchema(schema)


def nullable(schema: Schema[T]) -> NullableSchema[T]:
    """Create a nullable schema."""
    return NullableSchema(schema)


def union(schemas: List[Schema[Any]]) -> UnionSchema:
    """Create a union schema."""
    return UnionSchema(schemas)
