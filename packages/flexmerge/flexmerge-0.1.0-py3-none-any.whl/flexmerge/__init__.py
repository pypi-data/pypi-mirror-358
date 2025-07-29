"""
flexmerge - A simple and intuitive dictionary merging library

This library provides a clean API for merging dictionaries with customizable
strategies for handling lists, nested dictionaries, and other data types.
"""

from .merger import Merger, merge, merge_shallow, merge_unique
from .strategies import (
    BuiltinDictStrategies,
    BuiltinListStrategies,
    DictStrategy,
    ListStrategy,
)

__version__ = "0.1.0"
__all__ = [
    "Merger",
    "merge",
    "merge_unique",
    "merge_shallow",
    "ListStrategy",
    "DictStrategy",
    "BuiltinListStrategies",
    "BuiltinDictStrategies",
]
