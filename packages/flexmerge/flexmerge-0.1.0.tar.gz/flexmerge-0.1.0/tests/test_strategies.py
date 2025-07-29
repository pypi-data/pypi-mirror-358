"""Tests for the strategies module public API."""

import pytest

from flexmerge.strategies import (
    BUILTIN_DICT_STRATEGIES,
    BUILTIN_LIST_STRATEGIES,
    BuiltinDictStrategies,
    BuiltinListStrategies,
)


class TestBuiltinStrategies:
    """Test built-in strategy collections."""

    def test_builtin_list_strategies_completeness(self):
        """Test that all enum values have corresponding strategies."""
        for strategy_enum in BuiltinListStrategies:
            assert strategy_enum.value in BUILTIN_LIST_STRATEGIES
            assert callable(BUILTIN_LIST_STRATEGIES[strategy_enum.value])

    def test_builtin_dict_strategies_completeness(self):
        """Test that all enum values have corresponding strategies."""
        for strategy_enum in BuiltinDictStrategies:
            assert strategy_enum.value in BUILTIN_DICT_STRATEGIES
            assert callable(BUILTIN_DICT_STRATEGIES[strategy_enum.value])

    @pytest.mark.parametrize(
        "strategy_name", ["append", "prepend", "unique", "replace", "keep"]
    )
    def test_builtin_list_strategies_callable(self, strategy_name):
        """Test that all built-in list strategies are callable."""
        strategy = BUILTIN_LIST_STRATEGIES[strategy_name]
        assert callable(strategy)

        # Test that they can be called with lists
        result = strategy([1, 2], [3, 4])
        assert isinstance(result, list)

    @pytest.mark.parametrize("strategy_name", ["deep", "shallow", "replace", "keep"])
    def test_builtin_dict_strategies_callable(self, strategy_name):
        """Test that all built-in dict strategies are callable."""
        strategy = BUILTIN_DICT_STRATEGIES[strategy_name]
        assert callable(strategy)

        # Test that they can be called with dicts
        result = strategy({"a": 1}, {"b": 2})
        assert isinstance(result, dict)


class TestStrategyEnums:
    """Test strategy enum classes."""

    def test_builtin_list_strategies_enum_values(self):
        """Test BuiltinListStrategies enum values."""
        expected_values = {"append", "prepend", "unique", "replace", "keep"}
        actual_values = {strategy.value for strategy in BuiltinListStrategies}
        assert actual_values == expected_values

    def test_builtin_dict_strategies_enum_values(self):
        """Test BuiltinDictStrategies enum values."""
        expected_values = {"deep", "shallow", "replace", "keep"}
        actual_values = {strategy.value for strategy in BuiltinDictStrategies}
        assert actual_values == expected_values

    def test_enum_string_representation(self):
        """Test string representation of enums."""
        assert BuiltinListStrategies.APPEND.value == "append"
        assert BuiltinDictStrategies.DEEP.value == "deep"
