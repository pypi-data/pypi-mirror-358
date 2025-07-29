"""Type definitions for Zodic."""

import sys
from typing import Any, List, Optional, Protocol, TypeVar, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

# Always use typing_extensions for Literal to avoid conflicts
try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal  # type: ignore[assignment]

# Type variables
T = TypeVar("T")
U = TypeVar("U")

# Input/Output types
Input = Any
Output = TypeVar("Output")


# Validation context for error reporting
class ValidationContext:
    """Context information for validation operations."""

    def __init__(self, path: Optional[List[Union[str, int]]] = None) -> None:
        self.path = path or []

    def push(self, key: Union[str, int]) -> "ValidationContext":
        """Create a new context with an additional path element."""
        return ValidationContext(self.path + [key])

    def get_path_string(self) -> str:
        """Get a human-readable path string."""
        if not self.path:
            return "root"

        result = ""
        for i, segment in enumerate(self.path):
            if isinstance(segment, str):
                if i == 0:
                    result = segment
                else:
                    result += f".{segment}"
            else:  # int (array index)
                result += f"[{segment}]"
        return result


# Parse result types - using separate definitions for Python 3.9/3.10
# compatibility
class ParseSuccessDict(TypedDict):
    """Successful parse result structure."""

    success: Literal[True]
    data: Any


class ParseFailureDict(TypedDict):
    """Failed parse result structure."""

    success: Literal[False]
    error: Any  # ZodError - avoiding forward reference


# Type aliases for better typing
def ParseSuccess(success: Literal[True], data: T) -> ParseSuccessDict:
    """Create a successful parse result."""
    return {"success": success, "data": data}


def ParseFailure(success: Literal[False], error: Any) -> ParseFailureDict:
    """Create a failed parse result."""
    return {"success": success, "error": error}


# Union type for safe parse results
SafeParseResult = Union[ParseSuccessDict, ParseFailureDict]


# Issue types for error reporting
class ValidationIssue(TypedDict):
    """A single validation issue."""

    code: str
    message: str
    path: List[Union[str, int]]
    received: Any
    expected: Optional[str]


# Protocol for custom validators
class ValidatorProtocol(Protocol):
    """Protocol for custom validator functions."""

    def __call__(self, value: Any, ctx: ValidationContext) -> Any:
        """Validate and return the parsed value."""
        ...


# Transform function protocol
class TransformProtocol(Protocol):
    """Protocol for transform functions."""

    def __call__(self, value: Any) -> Any:
        """Transform the input value to output value."""
        ...


# Refinement function protocol
class RefinementProtocol(Protocol):
    """Protocol for refinement/custom validation functions."""

    def __call__(self, value: Any) -> bool:
        """Return True if value passes validation."""
        ...
