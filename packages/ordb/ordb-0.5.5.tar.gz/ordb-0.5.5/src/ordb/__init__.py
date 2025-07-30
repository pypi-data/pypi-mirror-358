"""ordb - Norwegian dictionary search tool."""

__version__ = "0.5.5"
__author__ = "Konrad M. Lawson"

# Main public API
from .core import (
    search_exact, search_fuzzy, search_prefix, search_anywhere_term, 
    search_fulltext, search_anywhere, search_expressions_only,
    search_all_examples, setup_database
)
from .config import SearchConfig
from .display import format_result, display_statistics

__all__ = [
    "search_exact", "search_fuzzy", "search_prefix", "search_anywhere_term",
    "search_fulltext", "search_anywhere", "search_expressions_only", 
    "search_all_examples", "setup_database", "SearchConfig", 
    "format_result", "display_statistics"
]