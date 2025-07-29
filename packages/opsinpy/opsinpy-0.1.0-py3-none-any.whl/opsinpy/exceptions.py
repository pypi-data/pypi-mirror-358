"""Custom exceptions for opsinpy package."""

from typing import Optional


class OpsinError(Exception):
    """Base exception for all OPSIN-related errors."""

    pass


class OpsinJVMError(OpsinError):
    """Exception raised when there are issues with JVM initialization or operation."""

    pass


class OpsinParsingError(OpsinError):
    """Exception raised when OPSIN fails to parse a chemical name."""

    def __init__(self, message: str, chemical_name: Optional[str] = None):
        super().__init__(message)
        self.chemical_name = chemical_name

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.chemical_name:
            return f"Failed to parse '{self.chemical_name}': {super().__str__()}"
        return super().__str__()
