"""
Zodic - A TypeScript Zod-inspired validation library for Python.

Zodic provides a simple, chainable API for validating and parsing data
with excellent type safety and developer experience.

Example:
    >>> import zodic as z
    >>> schema = z.string().min(3).max(10)
    >>> result = schema.parse("hello")  # Returns "hello"
    >>> user_schema = z.object({
    ...     'name': z.string(),
    ...     'age': z.number().int().positive()
    ... })
    >>> user = user_schema.parse({'name': 'John', 'age': 30})
"""

__version__ = "0.2.0"
__author__ = "Touhidul Alam Seyam"
__email__ = "seyamalam41@gmail.com"

from .core.base import Schema
from .core.errors import ValidationError, ZodError
from .schemas.collections import array, object
from .schemas.enums import enum
from .schemas.primitives import (
    boolean,
    date_schema,
    datetime_schema,
    literal,
    none,
    number,
    string,
)
from .schemas.special import nullable, optional, union

# Convenience aliases
date = date_schema
datetime = datetime_schema

# Main API exports - following Zod's naming convention
__all__ = [
    # Core classes
    "Schema",
    "ZodError",
    "ValidationError",
    # Schema constructors
    "string",
    "number",
    "boolean",
    "none",
    "literal",
    "date_schema",
    "datetime_schema",
    "date",
    "datetime",
    "object",
    "array",
    "enum",
    "optional",
    "nullable",
    "union",
    # Version info
    "__version__",
]
