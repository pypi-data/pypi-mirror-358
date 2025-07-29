"""Tests for the Merger class."""

from typing import Any

import pytest

from flexmerge import BuiltinDictStrategies, BuiltinListStrategies, Merger


class TestMergerBasics:
    """Test basic Merger functionality."""

    @pytest.fixture
    def merger(self):
        """Create a basic merger instance."""
        return Merger()

    @pytest.fixture
    def sample_dicts(self):
        """Sample dictionaries for testing."""
        return {
            "dict1": {"a": 1, "b": 2},
            "dict2": {"c": 3, "d": 4},
            "overlapping1": {"a": 1, "b": 2},
            "overlapping2": {"b": 3, "c": 4},
        }

    def test_empty_merge(self, merger):
        """Test merging with no arguments."""
        result = merger.merge()
        assert result == {}

    def test_single_dict_merge(self, merger, sample_dicts):
        """Test merging a single dictionary."""
        input_dict = sample_dicts["dict1"].copy()
        result = merger.merge(input_dict)
        assert result == {"a": 1, "b": 2}

        # Ensure original is not modified
        input_dict["c"] = 3
        assert "c" not in result

    def test_simple_merge(self, merger, sample_dicts):
        """Test merging two simple dictionaries."""
        result = merger.merge(sample_dicts["dict1"], sample_dicts["dict2"])
        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}

    def test_overlapping_keys(self, merger, sample_dicts):
        """Test merging with overlapping keys."""
        result = merger.merge(
            sample_dicts["overlapping1"], sample_dicts["overlapping2"]
        )
        assert result == {"a": 1, "b": 3, "c": 4}

    @pytest.mark.parametrize(
        "invalid_input,expected_error",
        [
            ("not a dict", "Argument 0 is not a dictionary"),
            (["not", "a", "dict"], "Argument 1 is not a dictionary"),
            (123, "Argument 0 is not a dictionary"),
            (None, "Argument 0 is not a dictionary"),
        ],
    )
    def test_invalid_input_type(self, merger, invalid_input, expected_error):
        """Test error handling for invalid input types."""
        if "Argument 0" in expected_error:
            with pytest.raises(TypeError, match=expected_error):
                merger.merge(invalid_input)
        else:
            with pytest.raises(TypeError, match=expected_error):
                merger.merge({"a": 1}, invalid_input)


class TestListStrategies:
    """Test different list merge strategies."""

    @pytest.fixture
    def list_dicts(self):
        """Sample dictionaries with lists for testing."""
        return {
            "dict1": {"items": [1, 2]},
            "dict2": {"items": [3, 4]},
            "overlapping": {"items": [1, 2, 3], "other": [2, 3, 4]},
        }

    @pytest.mark.parametrize(
        "strategy,expected",
        [
            ("append", [1, 2, 3, 4]),
            ("prepend", [3, 4, 1, 2]),
            ("unique", [1, 2, 3, 4]),
            ("replace", [3, 4]),
            ("keep", [1, 2]),
        ],
    )
    def test_list_strategies(self, strategy, expected, list_dicts):
        """Test different list merge strategies."""
        merger = Merger().lists(strategy)
        result = merger.merge(list_dicts["dict1"], list_dicts["dict2"])
        assert result == {"items": expected}

    def test_unique_strategy_with_unhashable(self):
        """Test unique strategy with unhashable items."""
        merger = Merger().lists("unique")
        dict1 = {"items": [{"a": 1}, [1, 2]]}
        dict2 = {"items": [{"b": 2}, [3, 4]]}
        result = merger.merge(dict1, dict2)
        assert result == {"items": [{"a": 1}, [1, 2], {"b": 2}, [3, 4]]}

    def test_enum_strategy(self, list_dicts):
        """Test using enum for strategy."""
        merger = Merger().lists(BuiltinListStrategies.UNIQUE)
        dict1 = {"items": [1, 2, 3]}
        dict2 = {"items": [2, 3, 4]}
        result = merger.merge(dict1, dict2)
        assert result == {"items": [1, 2, 3, 4]}


class TestDictStrategies:
    """Test different dictionary merge strategies."""

    @pytest.fixture
    def nested_dicts(self):
        """Sample nested dictionaries for testing."""
        return {
            "dict1": {"nested": {"a": 1, "b": 2}},
            "dict2": {"nested": {"b": 3, "c": 4}},
        }

    @pytest.mark.parametrize(
        "strategy,expected",
        [
            ("deep", {"nested": {"a": 1, "b": 3, "c": 4}}),
            ("shallow", {"nested": {"b": 3, "c": 4}}),
            ("replace", {"nested": {"b": 3, "c": 4}}),
            ("keep", {"nested": {"a": 1, "b": 2}}),
        ],
    )
    def test_dict_strategies(self, strategy, expected, nested_dicts):
        """Test different dictionary merge strategies."""
        merger = Merger().dicts(strategy)
        result = merger.merge(nested_dicts["dict1"], nested_dicts["dict2"])
        assert result == expected

    def test_enum_strategy(self, nested_dicts):
        """Test using enum for strategy."""
        merger = Merger().dicts(BuiltinDictStrategies.SHALLOW)
        result = merger.merge(nested_dicts["dict1"], nested_dicts["dict2"])
        assert result == {"nested": {"b": 3, "c": 4}}


class TestCustomStrategies:
    """Test custom strategy functionality."""

    def test_custom_list_strategy_decorator(self):
        """Test registering custom list strategy with decorator."""
        merger = Merger()

        @merger.list_strategy("sorted_unique")
        def sorted_unique_merge(left, right):
            return sorted(set(left + right))

        merger = merger.lists("sorted_unique")
        dict1 = {"items": [3, 1, 2]}
        dict2 = {"items": [2, 4, 1]}
        result = merger.merge(dict1, dict2)
        assert result == {"items": [1, 2, 3, 4]}

    def test_custom_dict_strategy_decorator(self):
        """Test registering custom dict strategy with decorator."""
        merger = Merger()

        @merger.dict_strategy("custom_dict")
        def custom_dict_merge(left, right):
            if left.get("merge_me") and right.get("merge_me"):
                result = left.copy()
                result.update(right)
                return result
            return left

        merger = merger.dicts("custom_dict")
        dict1 = {"merge_me": True, "a": 1}
        dict2 = {"merge_me": True, "b": 2}
        result = merger.merge(dict1, dict2)
        assert result == {"merge_me": True, "a": 1, "b": 2}

        # Test without merge_me key
        dict3 = {"a": 1}
        dict4 = {"b": 2}
        result2 = merger.merge(dict3, dict4)
        assert result2 == {"a": 1}

    def test_direct_function_strategy(self):
        """Test using function directly as strategy."""

        def custom_list_merge(left, right):
            return [max(left + right)]

        merger = Merger().lists(custom_list_merge)
        dict1 = {"items": [1, 2]}
        dict2 = {"items": [3, 4]}
        result = merger.merge(dict1, dict2)
        assert result == {"items": [4]}

    @pytest.mark.parametrize(
        "strategy_type,strategy_name",
        [
            ("lists", "nonexistent"),
            ("dicts", "nonexistent"),
        ],
    )
    def test_unknown_strategy_error(self, strategy_type, strategy_name):
        """Test error for unknown strategy."""
        merger = Merger()
        with pytest.raises(
            ValueError, match=f"Unknown {strategy_type[:-1]} strategy: {strategy_name}"
        ):
            getattr(merger, strategy_type)(strategy_name)

    def test_type_safe_custom_strategies(self):
        """Test type-safe custom strategy registration."""
        merger = Merger()

        @merger.list_strategy("type_safe_list")
        def type_safe_list_merge(left: list[Any], right: list[Any]) -> list[Any]:
            return sorted(set(left + right))

        @merger.dict_strategy("type_safe_dict")
        def type_safe_dict_merge(
            left: dict[str, Any], right: dict[str, Any]
        ) -> dict[str, Any]:
            return {**left, **right}

        # Test type-safe list strategy
        merger_list = merger.lists("type_safe_list")
        dict1 = {"items": [3, 1, 2]}
        dict2 = {"items": [2, 4, 1]}
        result = merger_list.merge(dict1, dict2)
        assert result == {"items": [1, 2, 3, 4]}

        # Test type-safe dict strategy
        merger_dict = merger.dicts("type_safe_dict")
        dict3 = {"a": 1, "nested": {"x": 1}}
        dict4 = {"b": 2, "nested": {"y": 2}}
        result2 = merger_dict.merge(dict3, dict4)
        assert result2 == {"a": 1, "b": 2, "nested": {"y": 2}}


class TestMethodChaining:
    """Test method chaining functionality."""

    def test_chaining_returns_self(self):
        """Test that methods return self for chaining."""
        merger = Merger()
        result = merger.lists("unique").dicts("shallow")
        assert isinstance(result, Merger)
        assert result is merger

    def test_complex_chaining(self):
        """Test complex method chaining."""
        merger = Merger().lists("unique").dicts("deep")
        dict1 = {"items": [1, 2, 3], "nested": {"a": 1, "b": 2}}
        dict2 = {"items": [2, 3, 4], "nested": {"b": 3, "c": 4}}
        result = merger.merge(dict1, dict2)
        expected = {"items": [1, 2, 3, 4], "nested": {"a": 1, "b": 3, "c": 4}}
        assert result == expected


class TestMergerCopy:
    """Test merger copying functionality."""

    def test_copy_preserves_strategies(self):
        """Test that copy preserves strategies."""
        original = Merger().lists("unique").dicts("shallow")
        copy = original.copy()

        # Test that they work the same
        dict1 = {"items": [1, 2], "nested": {"a": 1}}
        dict2 = {"items": [2, 3], "nested": {"b": 2}}

        result1 = original.merge(dict1, dict2)
        result2 = copy.merge(dict1, dict2)
        assert result1 == result2

    def test_copy_independence(self):
        """Test that copies are independent."""
        original = Merger().lists("unique")
        copy = original.copy()

        # Modify copy
        copy.lists("append")

        # Original should be unchanged
        dict1 = {"items": [1, 2]}
        dict2 = {"items": [2, 3]}

        original_result = original.merge(dict1, dict2)
        copy_result = copy.merge(dict1, dict2)

        assert original_result == {"items": [1, 2, 3]}  # unique
        assert copy_result == {"items": [1, 2, 2, 3]}  # append

    def test_copy_preserves_custom_strategies(self):
        """Test that copy preserves custom strategies."""
        original = Merger()

        @original.list_strategy("custom_list")
        def custom_list_strategy(left, right):
            return left + right

        @original.dict_strategy("custom_dict")
        def custom_dict_strategy(left, right):
            return {**left, **right}

        copy = original.copy()
        assert "custom_list" in copy._custom_list_strategies
        assert "custom_dict" in copy._custom_dict_strategies
        assert copy._custom_list_strategies["custom_list"] is custom_list_strategy
        assert copy._custom_dict_strategies["custom_dict"] is custom_dict_strategy


class TestMergerRepr:
    """Test string representation."""

    @pytest.mark.parametrize(
        "list_strategy,dict_strategy,expected",
        [
            ("append", "deep", "Merger(lists='append', dicts='deep')"),
            ("unique", "shallow", "Merger(lists='unique', dicts='shallow')"),
        ],
    )
    def test_repr_with_builtin_strategies(self, list_strategy, dict_strategy, expected):
        """Test representation with built-in strategies."""
        merger = Merger().lists(list_strategy).dicts(dict_strategy)
        assert repr(merger) == expected

    def test_custom_function_repr(self):
        """Test representation with custom function."""

        def custom_merge(left, right):
            return left + right

        merger = Merger().lists(custom_merge)
        assert repr(merger) == "Merger(lists='custom', dicts='deep')"


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_multiple_dicts(self):
        """Test merging multiple dictionaries."""
        merger = Merger().lists("unique").dicts("deep")

        dict1 = {"tags": ["python"], "config": {"debug": True}}
        dict2 = {"tags": ["web"], "config": {"port": 8000}}
        dict3 = {"tags": ["python"], "config": {"debug": False, "host": "localhost"}}

        result = merger.merge(dict1, dict2, dict3)
        expected = {
            "tags": ["python", "web"],
            "config": {"debug": False, "port": 8000, "host": "localhost"},
        }
        assert result == expected

    def test_mixed_data_types(self):
        """Test merging with mixed data types."""
        merger = Merger().lists("append")

        dict1 = {
            "string": "hello",
            "number": 42,
            "list": [1, 2],
            "dict": {"a": 1},
            "none": None,
        }
        dict2 = {
            "string": "world",
            "number": 100,
            "list": [3, 4],
            "dict": {"b": 2},
            "boolean": True,
        }

        result = merger.merge(dict1, dict2)
        expected = {
            "string": "world",
            "number": 100,
            "list": [1, 2, 3, 4],
            "dict": {"a": 1, "b": 2},
            "none": None,
            "boolean": True,
        }
        assert result == expected

    def test_deeply_nested_structures(self):
        """Test merging deeply nested structures."""
        merger = Merger().lists("unique").dicts("deep")

        dict1 = {"level1": {"level2": {"level3": {"items": [1, 2], "value": "old"}}}}
        dict2 = {"level1": {"level2": {"level3": {"items": [2, 3], "value": "new"}}}}

        result = merger.merge(dict1, dict2)
        expected = {
            "level1": {"level2": {"level3": {"items": [1, 2, 3], "value": "new"}}}
        }
        assert result == expected


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_lists_merge(self):
        """Test merging empty lists."""
        merger = Merger().lists("unique")
        dict1 = {"items": []}
        dict2 = {"items": [1, 2]}
        result = merger.merge(dict1, dict2)
        assert result == {"items": [1, 2]}

    def test_empty_dicts_merge(self):
        """Test merging empty dictionaries."""
        merger = Merger().dicts("deep")
        dict1 = {"nested": {}}
        dict2 = {"nested": {"a": 1}}
        result = merger.merge(dict1, dict2)
        assert result == {"nested": {"a": 1}}

    def test_none_values(self):
        """Test handling of None values."""
        merger = Merger()
        dict1 = {"key": None}
        dict2 = {"key": "value"}
        result = merger.merge(dict1, dict2)
        assert result == {"key": "value"}

    def test_list_strategy_with_non_list_values(self):
        """Test list strategy when values are not lists."""
        merger = Merger().lists("unique")
        dict1 = {"key": "not_a_list"}
        dict2 = {"key": "also_not_a_list"}
        result = merger.merge(dict1, dict2)
        assert result == {"key": "also_not_a_list"}


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the Merger class."""

    def test_real_world_config_merging(self):
        """Test real-world configuration merging scenario."""
        merger = Merger().lists("unique").dicts("deep")

        default_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "options": ["ssl", "timeout"],
            },
            "features": ["auth", "logging"],
            "debug": False,
        }

        production_config = {
            "database": {"host": "prod.example.com", "options": ["ssl", "pooling"]},
            "features": ["auth", "monitoring"],
            "cache": {"redis": "redis.example.com"},
        }

        user_config = {
            "database": {"timeout": 30},
            "features": ["auth", "custom_feature"],
            "debug": True,
        }

        result = merger.merge(default_config, production_config, user_config)

        expected = {
            "database": {
                "host": "prod.example.com",
                "port": 5432,
                "options": ["ssl", "timeout", "pooling"],
                "timeout": 30,
            },
            "features": ["auth", "logging", "monitoring", "custom_feature"],
            "debug": True,
            "cache": {"redis": "redis.example.com"},
        }

        assert result == expected
