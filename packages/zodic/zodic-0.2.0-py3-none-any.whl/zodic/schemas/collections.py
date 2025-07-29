"""Collection type schemas for Zodic."""

from typing import Any, Dict, List, Optional, TypeVar, cast

from ..core.base import Schema
from ..core.errors import ZodError, custom_issue, invalid_type_issue
from ..core.types import ValidationContext

T = TypeVar("T")


class ObjectSchema(Schema[Dict[str, Any]]):
    """Schema for object/dictionary validation."""

    def __init__(self, shape: Dict[str, Schema[Any]]) -> None:
        super().__init__()
        self.shape = shape
        self._strict = False
        self._passthrough = False

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Dict[str, Any]:
        """Parse and validate an object value."""
        if not isinstance(value, dict):
            raise ZodError([invalid_type_issue(value, "object", ctx)])

        result: Dict[str, Any] = {}
        issues: List[Any] = []

        # Validate known fields
        for key, schema in self.shape.items():
            field_ctx = ctx.push(key)

            if key in value:
                try:
                    # Use _parse_value directly with the field context to preserve paths
                    field_value = schema._parse_value(value[key], field_ctx)

                    # Apply transforms and refinements manually
                    for transform in schema._transforms:
                        field_value = transform(field_value)

                    for refinement, message in schema._refinements:
                        if not refinement(field_value):
                            issues.append(custom_issue(message, field_ctx, field_value))
                            break
                    else:
                        result[key] = field_value

                except ZodError as e:
                    # Propagate nested errors with correct paths
                    issues.extend(e.issues)
            else:
                # Handle missing fields
                from ..core.base import UNDEFINED

                field_result = schema.safe_parse(UNDEFINED)
                if field_result["success"]:
                    # Only include in result if not None (for optional fields)
                    if field_result["data"] is not None:
                        result[key] = field_result["data"]
                else:
                    # Update error paths to include field name
                    for issue in field_result["error"].issues:
                        issue["path"] = field_ctx.path.copy()
                    issues.extend(field_result["error"].issues)

        # Handle unknown fields
        unknown_keys = set(value.keys()) - set(self.shape.keys())
        if unknown_keys:
            if self._strict:
                for key in unknown_keys:
                    issues.append(
                        custom_issue(
                            f"Unrecognized key: {key}", ctx.push(key), value[key]
                        )
                    )
            elif self._passthrough:
                # Include unknown fields in result
                for key in unknown_keys:
                    result[key] = value[key]
            # If neither strict nor passthrough, unknown keys are ignored (strip mode)

        if issues:
            raise ZodError(issues)

        return result

    def strict(self) -> "ObjectSchema":
        """Disallow unknown keys."""
        new_schema = self._clone()
        new_schema._strict = True
        new_schema._passthrough = False
        return new_schema

    def passthrough(self) -> "ObjectSchema":
        """Allow unknown keys and include them in the result."""
        new_schema = self._clone()
        new_schema._strict = False
        new_schema._passthrough = True
        return new_schema

    def strip(self) -> "ObjectSchema":
        """Remove unknown keys from the result (default behavior)."""
        new_schema = self._clone()
        new_schema._strict = False
        new_schema._passthrough = False
        return new_schema

    def _clone(self) -> "ObjectSchema":
        """Create a copy of this schema."""
        new_schema = cast("ObjectSchema", super()._clone())
        new_schema.shape = self.shape.copy()
        new_schema._strict = self._strict
        new_schema._passthrough = self._passthrough
        return new_schema


class ArraySchema(Schema[List[T]]):
    """Schema for array/list validation."""

    def __init__(self, element_schema: Schema[T]) -> None:
        super().__init__()
        self.element_schema = element_schema
        self._min_length: Optional[int] = None
        self._max_length: Optional[int] = None

    def _parse_value(self, value: Any, ctx: ValidationContext) -> List[T]:
        """Parse and validate an array value."""
        if not isinstance(value, list):
            raise ZodError([invalid_type_issue(value, "array", ctx)])

        # Length validations
        if self._min_length is not None and len(value) < self._min_length:
            raise ZodError(
                [
                    custom_issue(
                        f"Array must have at least {self._min_length} elements",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_length is not None and len(value) > self._max_length:
            raise ZodError(
                [
                    custom_issue(
                        f"Array must have at most {self._max_length} elements",
                        ctx,
                        value,
                    )
                ]
            )

        # Validate each element
        result: List[T] = []
        issues: List[Any] = []

        for i, item in enumerate(value):
            item_ctx = ctx.push(i)

            try:
                # Use _parse_value directly with the item context to preserve paths
                item_value = self.element_schema._parse_value(item, item_ctx)

                # Apply transforms and refinements manually
                for transform in self.element_schema._transforms:
                    item_value = transform(item_value)

                for refinement, message in self.element_schema._refinements:
                    if not refinement(item_value):
                        issues.append(custom_issue(message, item_ctx, item_value))
                        break
                else:
                    result.append(item_value)

            except ZodError as e:
                # Propagate nested errors with correct paths
                issues.extend(e.issues)

        if issues:
            raise ZodError(issues)

        return result

    def min(self, length: int) -> "ArraySchema[T]":
        """Set minimum length constraint."""
        new_schema = self._clone()
        new_schema._min_length = length
        return new_schema

    def max(self, length: int) -> "ArraySchema[T]":
        """Set maximum length constraint."""
        new_schema = self._clone()
        new_schema._max_length = length
        return new_schema

    def length(self, length: int) -> "ArraySchema[T]":
        """Set exact length constraint."""
        return self.min(length).max(length)

    def nonempty(self) -> "ArraySchema[T]":
        """Require the array to have at least one element."""
        return self.min(1)

    def _clone(self) -> "ArraySchema[T]":
        """Create a copy of this schema."""
        new_schema = cast("ArraySchema[T]", super()._clone())
        new_schema.element_schema = self.element_schema
        new_schema._min_length = self._min_length
        new_schema._max_length = self._max_length
        return new_schema


# Factory functions
def object(shape: Dict[str, Schema[Any]]) -> ObjectSchema:
    """Create an object schema."""
    return ObjectSchema(shape)


def array(element_schema: Schema[T]) -> ArraySchema[T]:
    """Create an array schema."""
    return ArraySchema(element_schema)
