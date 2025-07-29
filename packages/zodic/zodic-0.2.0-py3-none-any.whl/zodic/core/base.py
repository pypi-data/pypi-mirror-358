"""Base schema class for Zodic."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Tuple, TypeVar, Union, cast

from .errors import ZodError, custom_issue
from .types import (
    ParseFailure,
    ParseSuccess,
    RefinementProtocol,
    SafeParseResult,
    TransformProtocol,
    ValidationContext,
)

T = TypeVar("T")
U = TypeVar("U")


class Schema(ABC, Generic[T]):
    """Base class for all Zodic schemas."""

    def __init__(self) -> None:
        self._transforms: List[Callable[[Any], Any]] = []
        self._refinements: List[Tuple[Callable[[Any], bool], str]] = []
        self._optional = False
        self._nullable = False
        self._default_value: Any = None
        self._has_default = False

    @abstractmethod
    def _parse_value(self, value: Any, ctx: ValidationContext) -> T:
        """Parse and validate the input value.

        Must be implemented by subclasses.
        """
        pass

    def parse(self, value: Any) -> T:
        """
        Parse and validate the input value.

        Args:
            value: The value to validate

        Returns:
            The parsed and validated value

        Raises:
            ZodError: If validation fails
        """
        result = self.safe_parse(value)
        if result["success"]:
            return result["data"]  # type: ignore
        else:
            raise result["error"]

    def safe_parse(self, value: Any) -> SafeParseResult:
        """
        Parse and validate the input value, returning a result object.

        Args:
            value: The value to validate

        Returns:
            A result object with success status and either data or error
        """
        try:
            ctx = ValidationContext()

            # Handle None values for optional/nullable schemas
            if value is None:
                if self._nullable:
                    return ParseSuccess(success=True, data=cast(T, None))
                elif self._optional and self._has_default:
                    value = self._default_value
                elif self._optional:
                    return ParseSuccess(success=True, data=cast(T, None))
                # If not optional/nullable, let the schema handle the None

            # Handle undefined values (using a sentinel for optional fields)
            if value is UNDEFINED:
                if self._has_default:
                    value = self._default_value
                elif self._optional:
                    return ParseSuccess(success=True, data=cast(T, None))
                else:
                    issues = [custom_issue("Required", ctx, value)]
                    return ParseFailure(success=False, error=ZodError(issues))

            # Parse the value using the schema-specific logic
            parsed_value = self._parse_value(value, ctx)

            # Apply transformations
            for transform in self._transforms:
                parsed_value = transform(parsed_value)

            # Apply refinements
            for refinement, message in self._refinements:
                if not refinement(parsed_value):
                    issues = [custom_issue(message, ctx, parsed_value)]
                    return ParseFailure(success=False, error=ZodError(issues))

            return ParseSuccess(success=True, data=parsed_value)

        except ZodError as e:
            return ParseFailure(success=False, error=e)
        except Exception as e:
            # Convert unexpected exceptions to ZodError
            issues = [custom_issue(f"Unexpected error: {str(e)}", ctx, value)]
            return ParseFailure(success=False, error=ZodError(issues))

    def optional(self) -> "Schema[Union[T, None]]":
        """Make this schema optional (value can be None or undefined)."""
        new_schema = self._clone()
        new_schema._optional = True
        return cast("Schema[Union[T, None]]", new_schema)

    def nullable(self) -> "Schema[Union[T, None]]":
        """Make this schema nullable (value can be None)."""
        new_schema = self._clone()
        new_schema._nullable = True
        return cast("Schema[Union[T, None]]", new_schema)

    def default(self, value: T) -> "Schema[T]":
        """Provide a default value for this schema."""
        new_schema = self._clone()
        new_schema._default_value = value
        new_schema._has_default = True
        return new_schema

    def transform(self, func: TransformProtocol) -> "Schema[Any]":
        """Apply a transformation function to the parsed value."""
        new_schema = self._clone()
        new_schema._transforms.append(func)
        return cast("Schema[Any]", new_schema)

    def refine(
        self, predicate: RefinementProtocol, message: str = "Invalid value"
    ) -> "Schema[T]":
        """Add a custom validation refinement."""
        new_schema = self._clone()
        new_schema._refinements.append((predicate, message))
        return new_schema

    def _clone(self) -> "Schema[T]":
        """Create a copy of this schema."""
        # Create a new instance of the same class
        new_schema = self.__class__.__new__(self.__class__)

        # Copy all attributes
        new_schema._transforms = self._transforms.copy()
        new_schema._refinements = self._refinements.copy()
        new_schema._optional = self._optional
        new_schema._nullable = self._nullable
        new_schema._default_value = self._default_value
        new_schema._has_default = self._has_default

        # Copy any schema-specific attributes
        for attr, value in self.__dict__.items():
            if not attr.startswith("_"):
                setattr(new_schema, attr, value)

        return new_schema

    def __or__(self, other: "Schema[U]") -> "Schema[Union[T, U]]":
        """Support union syntax with | operator."""
        # Import here to avoid circular imports
        from ..schemas.special import UnionSchema

        return UnionSchema([self, other])


# Sentinel value for undefined/missing values
class UndefinedType:
    """Sentinel type for undefined values."""

    def __repr__(self) -> str:
        return "UNDEFINED"


UNDEFINED = UndefinedType()
