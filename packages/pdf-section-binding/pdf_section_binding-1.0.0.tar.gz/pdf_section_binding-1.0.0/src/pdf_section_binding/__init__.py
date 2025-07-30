"""PDF Section Binding - A CLI tool for reordering PDF pages for bookbinding."""

from .version import __version__, __author__, __email__, __description__
from .core import calculate_signature_order, SectionBindingProcessor
from .cli import main

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "calculate_signature_order",
    "SectionBindingProcessor",
    "main",
]
