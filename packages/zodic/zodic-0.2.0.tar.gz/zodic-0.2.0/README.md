# Zodic

[![PyPI version](https://badge.fury.io/py/zodic.svg)](https://badge.fury.io/py/zodic)
[![Python versions](https://img.shields.io/pypi/pyversions/zodic.svg)](https://pypi.org/project/zodic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Seyamalam/zodic/workflows/CI/badge.svg)](https://github.com/Seyamalam/zodic/actions)
[![codecov](https://codecov.io/gh/Seyamalam/zodic/branch/main/graph/badge.svg)](https://codecov.io/gh/Seyamalam/zodic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Downloads](https://pepy.tech/badge/zodic)](https://pepy.tech/project/zodic)
[![Downloads](https://pepy.tech/badge/zodic/month)](https://pepy.tech/project/zodic)

A TypeScript [Zod](https://github.com/colinhacks/zod)-inspired validation library for Python with excellent type safety and developer experience.

## Features

- **Type-safe validation** with excellent IDE support and autocompletion
- **Intuitive chainable API** for building complex schemas
- **Lightning-fast performance** - 2M+ operations/second
- **Comprehensive error reporting** with detailed nested paths  
- **Zero dependencies** - lightweight and fast imports
- **Rich validation types** - strings, numbers, dates, enums, literals, and more
- **Advanced string validation** - email, URL, regex patterns
- **Date/time parsing** - ISO formats and common date strings
- **Union types** - flexible validation with `|` operator
- **Extensible architecture** for custom validators
- **Framework agnostic** - works with FastAPI, Django, Flask, etc.

## Installation

```bash
pip install zodic
```

Requires Python 3.9+

## Quick Start

```python
import zodic as z

# Basic validation
name_schema = z.string().min(1).max(100)
name = name_schema.parse("Alice")  # Returns "Alice"

# Object validation  
user_schema = z.object({
    "name": z.string().min(1),
    "age": z.number().int().min(0).max(120),
    "email": z.string().email().optional(),
    "is_active": z.boolean().default(True),
    "role": z.enum(["admin", "user", "guest"])
})

# Parse and validate data
user_data = {
    "name": "Alice Johnson", 
    "age": 30,
    "email": "alice@example.com"
}

user = user_schema.parse(user_data)
# Returns: {"name": "Alice Johnson", "age": 30, "email": "alice@example.com", "is_active": True}
```

## Documentation

### Basic Types

```python
import zodic as z

# Primitives
z.string()     # str
z.number()     # int | float
z.boolean()    # bool  
z.none()       # None

# String validation
z.string().min(5)              # Minimum length
z.string().max(100)            # Maximum length  
z.string().length(10)          # Exact length

# Number validation
z.number().int()               # Must be integer
z.number().positive()          # > 0
z.number().min(0).max(100)     # Range validation

# Collections
z.array(z.string())            # List[str]
z.object({"name": z.string()}) # Dict with typed fields
```

### Advanced Features

```python
# Optional and nullable
z.string().optional()          # str | None (can be missing)
z.string().nullable()          # str | None (can be null)
z.string().default("hello")    # Default value if missing

# Transformations
z.string().transform(str.upper)           # Transform after validation
z.number().transform(lambda x: x * 2)     # Custom transformations

# Custom validation
z.string().refine(
    lambda x: x.startswith("prefix_"),
    "Must start with 'prefix_'"
)

# Union types  
z.union([z.string(), z.number()])         # str | int | float
z.string() | z.number()                   # Same as above (v0.2.0+)
```

### New in v0.2.0

```python
# Literal and enum validation
z.literal("admin")                        # Exact value match
z.enum(["red", "green", "blue"])         # Multiple choice

# Enhanced string validation
z.string().email()                        # Email format validation
z.string().url()                          # URL format validation
z.string().regex(r"^[A-Z]{2,3}$")        # Custom regex patterns

# Date and datetime validation
z.date()                                  # Parse dates from strings or objects
z.datetime()                              # Parse datetimes with timezone support
z.date().min(date(2024, 1, 1))           # Date range validation

# Examples
email_schema = z.string().email()
email_schema.parse("user@example.com")   # Valid

theme_schema = z.enum(["light", "dark"])
theme_schema.parse("light")               # Valid

date_schema = z.date()
date_schema.parse("2024-12-19")          # Returns date(2024, 12, 19)
date_schema.parse(datetime.now())        # Converts to date
```

### Error Handling

```python
# Parse (throws ZodError on failure)
try:
    result = schema.parse(data)
except z.ZodError as e:
    print(f"Validation failed: {e}")
    print(f"Issues: {e.issues}")

# Safe parse (returns result object)
result = schema.safe_parse(data)
if result["success"]:
    print(f"Valid data: {result['data']}")
else:
    print(f"Validation errors: {result['error']}")

# Error formatting
try:
    schema.parse(invalid_data)
except z.ZodError as e:
    # Get flattened errors
    errors = e.flatten()
    # {"field.path": ["error message"]}
    
    # Get formatted errors  
    formatted = e.format()
    # [{"code": "invalid_type", "message": "...", "path": [...]}]
```

### Real-World Example

```python
import zodic as z
from datetime import date

# API request validation
create_user_schema = z.object({
    "personal_info": z.object({
        "first_name": z.string().min(1).max(50),
        "last_name": z.string().min(1).max(50),
        "email": z.string().email(),
        "birth_date": z.date().max(date.today()),
        "phone": z.string().regex(r"^\+?1?\d{9,15}$").optional()
    }),
    "account": z.object({
        "username": z.string().min(3).max(30).regex(r"^[a-zA-Z0-9_]+$"),
        "password": z.string().min(8).regex(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"),
        "role": z.enum(["admin", "moderator", "user"]).default("user"),
        "permissions": z.array(z.string()).default([])
    }),
    "preferences": z.object({
        "theme": z.enum(["light", "dark", "auto"]).default("auto"),
        "language": z.string().regex(r"^[a-z]{2}$").default("en"),
        "notifications": z.boolean().default(True)
    }).optional(),
    "metadata": z.object({
        "source": z.literal("api"),
        "version": z.string().regex(r"^\d+\.\d+\.\d+$"),
        "created_at": z.datetime().default(lambda: datetime.now())
    })
})

# Usage
try:
    user = create_user_schema.parse(request_data)
    # user is fully typed and validated
    print(f"Creating user: {user['personal_info']['email']}")
except z.ZodError as e:
    return {"error": "Validation failed", "details": e.flatten()}
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI, HTTPException
import zodic as z

app = FastAPI()

UserSchema = z.object({
    "name": z.string().min(1),
    "email": z.string().email(),
    "age": z.number().int().min(18)
})

@app.post("/users")
async def create_user(data: dict):
    try:
        user = UserSchema.parse(data)
        # Process validated user data
        return {"user": user}
    except z.ZodError as e:
        raise HTTPException(status_code=422, detail=e.flatten())
```

### Django

```python
from django.http import JsonResponse
import zodic as z

ContactSchema = z.object({
    "name": z.string().min(1).max(100),
    "email": z.string().email(),
    "message": z.string().min(10).max(1000)
})

def contact_view(request):
    if request.method == "POST":
        try:
            data = ContactSchema.parse(request.POST.dict())
            # Process validated data
            return JsonResponse({"status": "success"})
        except z.ZodError as e:
            return JsonResponse({"errors": e.flatten()}, status=400)
```

## Performance

Zodic is designed for high performance:

- **2M+ validations/second** for simple schemas
- **500K+ validations/second** for complex nested objects  
- **Zero dependencies** - fast imports and minimal overhead
- **Optimized error handling** - detailed errors without performance cost
- **Memory efficient** - minimal allocations during validation

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Seyamalam/zodic.git
cd zodic

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run quality checks
poetry run black zodic tests
poetry run isort zodic tests  
poetry run mypy zodic
poetry run flake8 zodic tests
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

## Support

- 📖 [Documentation](https://github.com/Seyamalam/zodic)
- 🐛 [Issue Tracker](https://github.com/Seyamalam/zodic/issues)
- 💬 [Discussions](https://github.com/Seyamalam/zodic/discussions)
- 📧 [Email Support](mailto:seyamalam41@gmail.com)

**Star us on GitHub if Zodic helps you build better Python applications!**