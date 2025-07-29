"""Error classes for Zodic validation."""

from typing import Any, Dict, List, Optional

from .types import ValidationContext, ValidationIssue


class ZodError(Exception):
    """Main exception class for Zodic validation errors."""

    def __init__(self, issues: List[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a human-readable error message."""
        if len(self.issues) == 1:
            issue = self.issues[0]
            path = self._format_path(issue["path"])
            return f"Validation error at {path}: {issue['message']}"
        else:
            lines = [f"Validation failed with {len(self.issues)} issues:"]
            for issue in self.issues:
                path = self._format_path(issue["path"])
                lines.append(f"  - {path}: {issue['message']}")
            return "\n".join(lines)

    def _format_path(self, path: List[Any]) -> str:
        """Format a path list into a readable string."""
        if not path:
            return "root"

        result = ""
        for i, segment in enumerate(path):
            if isinstance(segment, str):
                if i == 0:
                    result = segment
                else:
                    result += f".{segment}"
            else:  # int (array index)
                result += f"[{segment}]"
        return result

    def flatten(self) -> Dict[str, List[str]]:
        """Flatten errors into a dictionary mapping paths to error messages."""
        result: Dict[str, List[str]] = {}
        for issue in self.issues:
            path_str = self._format_path(issue["path"])
            if path_str not in result:
                result[path_str] = []
            result[path_str].append(issue["message"])
        return result

    def format(self) -> List[Dict[str, Any]]:
        """Format errors as a list of dictionaries."""
        return [
            {
                "code": issue["code"],
                "message": issue["message"],
                "path": issue["path"],
                "received": issue["received"],
                "expected": issue.get("expected"),
            }
            for issue in self.issues
        ]


class ValidationError(ZodError):
    """Alias for ZodError for compatibility."""

    pass


def create_issue(
    code: str,
    message: str,
    ctx: ValidationContext,
    received: Any,
    expected: Optional[str] = None,
) -> ValidationIssue:
    """Create a validation issue."""
    return ValidationIssue(
        code=code,
        message=message,
        path=ctx.path.copy(),
        received=received,
        expected=expected,
    )


def invalid_type_issue(
    received: Any,
    expected: str,
    ctx: ValidationContext,
) -> ValidationIssue:
    """Create an invalid type issue."""
    received_type = type(received).__name__
    return create_issue(
        code="invalid_type",
        message=f"Expected {expected}, received {received_type}",
        ctx=ctx,
        received=received,
        expected=expected,
    )


def custom_issue(
    message: str,
    ctx: ValidationContext,
    received: Any,
    code: str = "custom",
) -> ValidationIssue:
    """Create a custom validation issue."""
    return create_issue(
        code=code,
        message=message,
        ctx=ctx,
        received=received,
    )
