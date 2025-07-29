"""
Merge strategies for different data types.

This module defines the strategy protocols and provides built-in strategies
for common merge operations.
"""

from enum import Enum
from typing import Any, Protocol


class ListStrategy(Protocol):
    """Protocol for list merge strategies."""

    def __call__(self, left: list[Any], right: list[Any]) -> list[Any]:
        """Merge two lists according to the strategy."""
        ...


class DictStrategy(Protocol):
    """Protocol for dictionary merge strategies."""

    def __call__(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        """Merge two dictionaries according to the strategy."""
        ...


class BuiltinListStrategies(Enum):
    """Enumeration of built-in list merge strategies."""

    APPEND = "append"
    PREPEND = "prepend"
    UNIQUE = "unique"
    REPLACE = "replace"
    KEEP = "keep"


class BuiltinDictStrategies(Enum):
    """Enumeration of built-in dictionary merge strategies."""

    DEEP = "deep"
    SHALLOW = "shallow"
    REPLACE = "replace"
    KEEP = "keep"


def _append_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Append right list to left list."""
    return left + right


def _prepend_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Prepend right list to left list."""
    return right + left


def _unique_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Combine lists and remove duplicates while preserving order."""
    result = []
    seen = set()

    # Add items from left list
    for item in left:
        # Handle unhashable items
        try:
            if item not in seen:
                result.append(item)
                seen.add(item)
        except TypeError:
            # Item is unhashable, check manually
            if item not in result:
                result.append(item)

    # Add items from right list
    for item in right:
        try:
            if item not in seen:
                result.append(item)
                seen.add(item)
        except TypeError:
            # Item is unhashable, check manually
            if item not in result:
                result.append(item)

    return result


def _replace_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Replace left list with right list."""
    return right


def _keep_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Keep left list, ignore right list."""
    return left


def _deep_merge_dicts_with_strategy(
    left: dict[str, Any], right: dict[str, Any], list_strategy: ListStrategy
) -> dict[str, Any]:
    """Deep merge two dictionaries with optional list strategy."""
    result = left.copy()

    for key, right_value in right.items():
        if key in result:
            left_value = result[key]
            if isinstance(left_value, dict) and isinstance(right_value, dict):
                # Recursively merge nested dictionaries
                result[key] = _deep_merge_dicts_with_strategy(
                    left_value, right_value, list_strategy
                )
            elif isinstance(left_value, list) and isinstance(right_value, list):
                # Use the provided list strategy
                result[key] = list_strategy(left_value, right_value)
            else:
                # Replace with right value
                result[key] = right_value
        else:
            result[key] = right_value

    return result


def _deep_merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries with default list strategy."""
    return _deep_merge_dicts_with_strategy(left, right, _append_lists)


def _shallow_merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge two dictionaries."""
    result = left.copy()
    result.update(right)
    return result


def _replace_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Replace left dict with right dict."""
    return right


def _keep_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Keep left dict, ignore right dict."""
    return left


# Built-in strategy implementations
BUILTIN_LIST_STRATEGIES: dict[str, ListStrategy] = {
    BuiltinListStrategies.APPEND.value: _append_lists,
    BuiltinListStrategies.PREPEND.value: _prepend_lists,
    BuiltinListStrategies.UNIQUE.value: _unique_lists,
    BuiltinListStrategies.REPLACE.value: _replace_lists,
    BuiltinListStrategies.KEEP.value: _keep_lists,
}

BUILTIN_DICT_STRATEGIES: dict[str, DictStrategy] = {
    BuiltinDictStrategies.DEEP.value: _deep_merge_dicts,
    BuiltinDictStrategies.SHALLOW.value: _shallow_merge_dicts,
    BuiltinDictStrategies.REPLACE.value: _replace_dicts,
    BuiltinDictStrategies.KEEP.value: _keep_dicts,
}
