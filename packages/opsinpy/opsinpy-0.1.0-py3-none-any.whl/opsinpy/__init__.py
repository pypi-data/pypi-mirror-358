"""opsinpy: Python bindings for OPSIN (Open Parser for Systematic IUPAC Nomenclature)"""

from .exceptions import OpsinError, OpsinJVMError, OpsinParsingError
from .opsinpy import OpsinPy

__version__ = "0.1.0"
__author__ = "Charlles Abreu <craabreu@mit.edu>, Claude 3.5 Sonnet (Anthropic AI), Claude 4 Sonnet (Anthropic AI)"

__all__ = [
    "OpsinError",
    "OpsinJVMError",
    "OpsinParsingError",
    "OpsinPy",
]
