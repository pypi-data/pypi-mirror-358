"""Tests for convenience functions."""

import pytest

from flexmerge.merger import merge, merge_shallow, merge_unique


class TestConvenienceFunctions:
    """Test convenience functions for quick merging."""

    @pytest.fixture
    def sample_dicts(self):
        """Sample dictionaries for testing."""
        return {
            "dict1": {"a": 1, "list": [1, 2], "nested": {"x": 1}},
            "dict2": {"b": 2, "list": [3, 4], "nested": {"y": 2}},
            "tags1": {"tags": ["python", "web"], "config": {"debug": True}},
            "tags2": {"tags": ["web", "api"], "config": {"port": 8000}},
        }

    def test_merge_default(self, sample_dicts):
        """Test default merge function."""
        result = merge(sample_dicts["dict1"], sample_dicts["dict2"])
        expected = {"a": 1, "b": 2, "list": [1, 2, 3, 4], "nested": {"x": 1, "y": 2}}
        assert result == expected

    def test_merge_with_unique_strategy(self, sample_dicts):
        """Test merge with unique list strategy."""
        result = merge(sample_dicts["dict1"], sample_dicts["dict2"], lists="unique")
        expected = {"a": 1, "b": 2, "list": [1, 2, 3, 4], "nested": {"x": 1, "y": 2}}
        assert result == expected

    def test_merge_with_shallow_strategy(self, sample_dicts):
        """Test merge with shallow dict strategy."""
        result = merge(
            sample_dicts["dict1"], sample_dicts["dict2"], dict_strategy="shallow"
        )
        expected = {
            "a": 1,
            "b": 2,
            "list": [3, 4],  # Shallow merge replaces list
            "nested": {"y": 2},  # Shallow merge replaces nested dict
        }
        assert result == expected

    def test_merge_unique(self, sample_dicts):
        """Test merge_unique convenience function."""
        result = merge_unique(sample_dicts["tags1"], sample_dicts["tags2"])
        expected = {
            "tags": ["python", "web", "api"],
            "config": {"debug": True, "port": 8000},
        }
        assert result == expected

    def test_merge_shallow(self, sample_dicts):
        """Test merge_shallow convenience function."""
        dict1 = {"nested": {"a": 1, "b": 2}, "other": "value1"}
        dict2 = {"nested": {"c": 3}, "other": "value2"}

        result = merge_shallow(dict1, dict2)
        expected = {"nested": {"c": 3}, "other": "value2"}
        assert result == expected

    @pytest.mark.parametrize("func", [merge, merge_unique, merge_shallow])
    def test_empty_dicts(self, func):
        """Test convenience functions with empty dictionaries."""
        assert func() == {}
        assert func({}) == {}
        assert func({}, {}) == {}

    @pytest.mark.parametrize("func", [merge, merge_unique, merge_shallow])
    def test_single_dict(self, func):
        """Test convenience functions with single dictionary."""
        test_dict = {"a": 1, "b": [1, 2]}
        result = func(test_dict)
        assert result == test_dict

        # Ensure original is not modified
        test_dict["c"] = 3
        assert func({"a": 1, "b": [1, 2]}) == {"a": 1, "b": [1, 2]}

    @pytest.mark.parametrize(
        "func,expected",
        [
            (merge, {"a": 4, "b": 2, "c": 3}),
            (merge_unique, {"a": 4, "b": 2, "c": 3}),
            (merge_shallow, {"a": 4, "b": 2, "c": 3}),
        ],
    )
    def test_multiple_dicts(self, func, expected):
        """Test convenience functions with multiple dictionaries."""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        dict3 = {"c": 3}
        dict4 = {"a": 4}  # Override

        result = func(dict1, dict2, dict3, dict4)
        assert result == expected

    def test_merge_with_lists_and_nested_dicts(self):
        """Test merge function with complex nested structures."""
        dict1 = {
            "items": [1, 2],
            "config": {"db": {"host": "localhost"}},
            "features": ["auth"],
        }
        dict2 = {
            "items": [2, 3],
            "config": {"db": {"port": 5432}},
            "features": ["logging"],
        }

        # Test with different strategies
        result_default = merge(dict1, dict2)
        expected_default = {
            "items": [1, 2, 2, 3],
            "config": {"db": {"host": "localhost", "port": 5432}},
            "features": ["auth", "logging"],
        }
        assert result_default == expected_default

        result_unique = merge(dict1, dict2, lists="unique")
        expected_unique = {
            "items": [1, 2, 3],
            "config": {"db": {"host": "localhost", "port": 5432}},
            "features": ["auth", "logging"],
        }
        assert result_unique == expected_unique

    def test_error_handling(self):
        """Test error handling in convenience functions."""
        with pytest.raises(TypeError):
            merge("not_a_dict")

        with pytest.raises(TypeError):
            merge_unique({"a": 1}, "not_a_dict")

        with pytest.raises(TypeError):
            merge_shallow(None, {"a": 1})


class TestConvenienceFunctionEdgeCases:
    """Test edge cases for convenience functions."""

    def test_merge_with_none_values(self):
        """Test merging dictionaries with None values."""
        dict1 = {"key": None, "other": "value1"}
        dict2 = {"key": "value", "other": None}

        result = merge(dict1, dict2)
        assert result == {"key": "value", "other": None}

    def test_merge_with_empty_lists(self):
        """Test merging dictionaries with empty lists."""
        dict1 = {"items": [], "other": [1, 2]}
        dict2 = {"items": [1, 2], "other": []}

        result = merge_unique(dict1, dict2)
        assert result == {"items": [1, 2], "other": [1, 2]}

    def test_merge_with_mixed_types(self):
        """Test merging with mixed data types."""
        dict1 = {
            "string": "hello",
            "number": 42,
            "boolean": True,
            "list": [1, 2],
            "dict": {"a": 1},
        }
        dict2 = {
            "string": "world",
            "number": 100,
            "boolean": False,
            "list": [3, 4],
            "dict": {"b": 2},
        }

        result = merge(dict1, dict2)
        expected = {
            "string": "world",
            "number": 100,
            "boolean": False,
            "list": [1, 2, 3, 4],
            "dict": {"a": 1, "b": 2},
        }
        assert result == expected

    @pytest.mark.parametrize(
        "strategy", ["unique", "append", "prepend", "replace", "keep"]
    )
    def test_all_list_strategies_with_convenience_functions(self, strategy):
        """Test all list strategies work with convenience functions."""
        dict1 = {"items": [1, 2]}
        dict2 = {"items": [2, 3]}

        result = merge(dict1, dict2, lists=strategy)

        # Verify result is a dictionary and has the items key
        assert isinstance(result, dict)
        assert "items" in result
        assert isinstance(result["items"], list)

    def test_deeply_nested_merge_with_convenience_functions(self):
        """Test deeply nested structures with convenience functions."""
        dict1 = {
            "level1": {
                "level2": {"level3": {"items": [1, 2], "config": {"debug": True}}}
            }
        }
        dict2 = {
            "level1": {
                "level2": {"level3": {"items": [2, 3], "config": {"port": 8000}}}
            }
        }

        result = merge_unique(dict1, dict2)
        expected = {
            "level1": {
                "level2": {
                    "level3": {
                        "items": [1, 2, 3],
                        "config": {"debug": True, "port": 8000},
                    }
                }
            }
        }
        assert result == expected
