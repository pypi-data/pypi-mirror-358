"""
Merger class for combining dictionaries with customizable strategies.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .strategies import (
    BUILTIN_DICT_STRATEGIES,
    BUILTIN_LIST_STRATEGIES,
    BuiltinDictStrategies,
    BuiltinListStrategies,
    DictStrategy,
    ListStrategy,
    _deep_merge_dicts_with_strategy,
)


class Merger:
    """
    A flexible dictionary merger with customizable strategies for lists and dictionaries.

    Example:
        >>> merger = Merger().lists("unique").dicts("deep")
        >>> result = merger.merge(dict1, dict2, dict3)

        >>> @merger.list_strategy("custom_list")
        ... def custom_list_merge(left, right):
        ...     return sorted(set(left + right))

        >>> @merger.dict_strategy("custom_dict")
        ... def custom_dict_merge(left, right):
        ...     return {**left, **right}
    """

    def __init__(self) -> None:
        """Initialize merger with default strategies."""
        self._list_strategy: ListStrategy = BUILTIN_LIST_STRATEGIES["append"]
        self._dict_strategy: DictStrategy = BUILTIN_DICT_STRATEGIES["deep"]
        self._custom_list_strategies: dict[str, ListStrategy] = {}
        self._custom_dict_strategies: dict[str, DictStrategy] = {}

    def lists(self, strategy: str | ListStrategy | BuiltinListStrategies) -> Merger:
        """
        Set the list merge strategy.

        Args:
            strategy: Built-in strategy name, custom strategy name, or strategy function

        Returns:
            Self for method chaining

        Raises:
            ValueError: If strategy is not found
        """
        if isinstance(strategy, BuiltinListStrategies):
            strategy = strategy.value

        if isinstance(strategy, str):
            if strategy in BUILTIN_LIST_STRATEGIES:
                self._list_strategy = BUILTIN_LIST_STRATEGIES[strategy]
            elif strategy in self._custom_list_strategies:
                self._list_strategy = self._custom_list_strategies[strategy]
            else:
                raise ValueError(f"Unknown list strategy: {strategy}")
        else:
            # Assume it's a callable strategy
            self._list_strategy = strategy

        return self

    def dicts(self, strategy: str | DictStrategy | BuiltinDictStrategies) -> Merger:
        """
        Set the dictionary merge strategy.

        Args:
            strategy: Built-in strategy name, custom strategy name, or strategy function

        Returns:
            Self for method chaining

        Raises:
            ValueError: If strategy is not found
        """
        if isinstance(strategy, BuiltinDictStrategies):
            strategy = strategy.value

        if isinstance(strategy, str):
            if strategy in BUILTIN_DICT_STRATEGIES:
                self._dict_strategy = BUILTIN_DICT_STRATEGIES[strategy]
            elif strategy in self._custom_dict_strategies:
                self._dict_strategy = self._custom_dict_strategies[strategy]
            else:
                raise ValueError(f"Unknown dict strategy: {strategy}")
        else:
            # Assume it's a callable strategy
            self._dict_strategy = strategy

        return self

    def list_strategy(self, name: str) -> Callable[[ListStrategy], ListStrategy]:
        """
        Decorator for registering custom list strategies.

        Args:
            name: Name of the custom list strategy

        Returns:
            Decorator function

        Example:
            >>> merger = Merger()
            >>> @merger.list_strategy("sorted_unique")
            ... def sorted_unique_merge(left, right):
            ...     return sorted(set(left + right))
        """

        def decorator(func: ListStrategy) -> ListStrategy:
            self._custom_list_strategies[name] = func
            return func

        return decorator

    def dict_strategy(self, name: str) -> Callable[[DictStrategy], DictStrategy]:
        """
        Decorator for registering custom dictionary strategies.

        Args:
            name: Name of the custom dictionary strategy

        Returns:
            Decorator function

        Example:
            >>> merger = Merger()
            >>> @merger.dict_strategy("custom_merge")
            ... def custom_dict_merge(left, right):
            ...     return {**left, **right}
        """

        def decorator(func: DictStrategy) -> DictStrategy:
            self._custom_dict_strategies[name] = func
            return func

        return decorator

    def merge(self, *dicts: dict[str, Any]) -> dict[str, Any]:
        """
        Merge multiple dictionaries using configured strategies.

        Args:
            *dicts: Dictionaries to merge

        Returns:
            Merged dictionary

        Raises:
            TypeError: If any argument is not a dictionary
        """
        if not dicts:
            return {}

        # Validate all arguments are dictionaries
        for i, d in enumerate(dicts):
            if not isinstance(d, dict):
                raise TypeError(f"Argument {i} is not a dictionary: {type(d)}")

        result = deepcopy(dicts[0])

        for dict_to_merge in dicts[1:]:
            result = self._merge_dicts(result, dict_to_merge)

        return result

    def _merge_dicts(
        self, left: dict[str, Any], right: dict[str, Any]
    ) -> dict[str, Any]:
        """Internal method to merge two dictionaries."""
        # Special handling for deep merge to pass list strategy
        if self._dict_strategy == BUILTIN_DICT_STRATEGIES["deep"]:
            return _deep_merge_dicts_with_strategy(left, right, self._list_strategy)
        else:
            return self._dict_strategy(left, right)

    def _merge_lists(self, left: list[Any], right: list[Any]) -> list[Any]:
        """Internal method to merge two lists."""
        return self._list_strategy(left, right)

    def _find_list_strategy_name(self) -> str | None:
        """Find the name of the current list strategy."""
        for name, strategy in BUILTIN_LIST_STRATEGIES.items():
            if strategy is self._list_strategy:
                return name

        # Check custom strategies
        for name, strategy in self._custom_list_strategies.items():
            if strategy is self._list_strategy:
                return name

        return None

    def _find_dict_strategy_name(self) -> str | None:
        """Find the name of the current dict strategy."""
        for name, strategy in BUILTIN_DICT_STRATEGIES.items():
            if strategy is self._dict_strategy:
                return name

        # Check custom strategies
        for name, strategy in self._custom_dict_strategies.items():
            if strategy is self._dict_strategy:
                return name

        return None

    def copy(self) -> Merger:
        """
        Create a copy of this merger with the same strategies.

        Returns:
            New Merger instance with copied strategies
        """
        new_merger = Merger()

        # Copy strategies by finding their names and using public API
        list_strategy_name = self._find_list_strategy_name()
        dict_strategy_name = self._find_dict_strategy_name()

        if list_strategy_name:
            new_merger.lists(list_strategy_name)
        if dict_strategy_name:
            new_merger.dicts(dict_strategy_name)

        # Copy custom strategies
        new_merger._custom_list_strategies = self._custom_list_strategies.copy()
        new_merger._custom_dict_strategies = self._custom_dict_strategies.copy()

        return new_merger

    def __repr__(self) -> str:
        """String representation of the merger."""
        list_strategy_name = self._find_list_strategy_name() or "custom"
        dict_strategy_name = self._find_dict_strategy_name() or "custom"

        return f"Merger(lists='{list_strategy_name}', dicts='{dict_strategy_name}')"


# Convenience functions for quick merging
def merge(
    *dicts: dict[str, Any], lists: str = "append", dict_strategy: str = "deep"
) -> dict[str, Any]:
    """
    Quick merge function with default strategies.

    Args:
        *dicts: Dictionaries to merge
        lists: List merge strategy (default: "append")
        dict_strategy: Dictionary merge strategy (default: "deep")

    Returns:
        Merged dictionary
    """
    merger = Merger().lists(lists).dicts(dict_strategy)
    return merger.merge(*dicts)


def merge_unique(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Merge dictionaries with unique list merging.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary with unique lists
    """
    return merge(*dicts, lists="unique")


def merge_shallow(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Merge dictionaries with shallow merging.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Shallow merged dictionary
    """
    return merge(*dicts, dict_strategy="shallow")
