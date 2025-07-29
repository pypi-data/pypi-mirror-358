#!/usr/bin/env python3
"""
Basic usage examples for dictmerge library.

This file demonstrates the main features and usage patterns of the dictmerge library.
"""

from dictmerge import Merger


def basic_examples():
    """Basic usage examples."""
    print("=== Basic Dictionary Merging ===")
    
    # Simple merge
    dict1 = {"name": "Alice", "age": 30}
    dict2 = {"city": "Tokyo", "country": "Japan"}
    
    merger = Merger()
    result = merger.merge(dict1, dict2)
    print(f"Simple merge: {result}")
    
    # Overlapping keys (right takes precedence)
    dict3 = {"name": "Bob", "age": 25}
    result = merger.merge(dict1, dict3)
    print(f"Overlapping keys: {result}")


def list_strategies():
    """Demonstrate different list merge strategies."""
    print("\n=== List Merge Strategies ===")
    
    dict1 = {"tags": ["python", "programming"]}
    dict2 = {"tags": ["web", "programming"]}
    
    # Append (default)
    merger = Merger().lists("append")
    result = merger.merge(dict1, dict2)
    print(f"Append: {result}")
    
    # Unique (remove duplicates)
    merger = Merger().lists("unique")
    result = merger.merge(dict1, dict2)
    print(f"Unique: {result}")
    
    # Prepend
    merger = Merger().lists("prepend")
    result = merger.merge(dict1, dict2)
    print(f"Prepend: {result}")
    
    # Replace
    merger = Merger().lists("replace")
    result = merger.merge(dict1, dict2)
    print(f"Replace: {result}")


def dict_strategies():
    """Demonstrate different dictionary merge strategies."""
    print("\n=== Dictionary Merge Strategies ===")
    
    dict1 = {
        "config": {"debug": True, "port": 8000},
        "features": {"auth": True}
    }
    dict2 = {
        "config": {"debug": False, "host": "localhost"},
        "features": {"logging": True}
    }
    
    # Deep merge (default)
    merger = Merger().dicts("deep")
    result = merger.merge(dict1, dict2)
    print(f"Deep merge: {result}")
    
    # Shallow merge
    merger = Merger().dicts("shallow")
    result = merger.merge(dict1, dict2)
    print(f"Shallow merge: {result}")


def method_chaining():
    """Demonstrate method chaining."""
    print("\n=== Method Chaining ===")
    
    dict1 = {
        "items": [1, 2, 3],
        "config": {"debug": True, "level": "info"}
    }
    dict2 = {
        "items": [2, 3, 4],
        "config": {"debug": False, "timeout": 30}
    }
    
    # Chain multiple configurations
    result = (Merger()
              .lists("unique")
              .dicts("deep")
              .merge(dict1, dict2))
    
    print(f"Chained configuration: {result}")


def custom_strategies():
    """Demonstrate custom merge strategies."""
    print("\n=== Custom Strategies ===")
    
    merger = Merger()
    
    # Custom list strategy: sort and deduplicate
    @merger.strategy("sorted_unique")
    def sorted_unique_merge(left, right):
        return sorted(set(left + right))
    
    # Custom dict strategy: only merge if both have 'mergeable' flag
    @merger.strategy("conditional_merge")
    def conditional_dict_merge(left, right):
        if left.get("mergeable") and right.get("mergeable"):
            result = left.copy()
            result.update(right)
            return result
        return left
    
    # Use custom strategies
    dict1 = {"numbers": [3, 1, 2], "mergeable": True, "a": 1}
    dict2 = {"numbers": [2, 4, 1], "mergeable": True, "b": 2}
    
    result = (merger
              .lists("sorted_unique")
              .dicts("conditional_merge")
              .merge(dict1, dict2))
    
    print(f"Custom strategies: {result}")
    
    # Test conditional merge with non-mergeable dict
    dict3 = {"numbers": [5, 6], "mergeable": False, "c": 3}
    result2 = merger.merge(dict1, dict3)
    print(f"Conditional merge (not mergeable): {result2}")


def real_world_example():
    """Real-world configuration merging example."""
    print("\n=== Real-World Example: Configuration Merging ===")
    
    # Default configuration
    default_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "options": ["ssl", "timeout"]
        },
        "features": ["auth", "logging"],
        "debug": False
    }
    
    # Environment-specific configuration
    production_config = {
        "database": {
            "host": "prod.example.com",
            "port": 5432,
            "options": ["ssl", "pooling"]
        },
        "features": ["auth", "monitoring"],
        "debug": False,
        "cache": {"redis": "redis.example.com"}
    }
    
    # User-specific overrides
    user_config = {
        "database": {
            "timeout": 30
        },
        "features": ["auth", "custom_feature"],
        "debug": True
    }
    
    # Merge configurations with appropriate strategies
    merger = Merger().lists("unique").dicts("deep")
    final_config = merger.merge(default_config, production_config, user_config)
    
    print("Final configuration:")
    for key, value in final_config.items():
        print(f"  {key}: {value}")


def convenience_functions():
    """Demonstrate convenience functions."""
    print("\n=== Convenience Functions ===")
    
    from dictmerge.merger import merge, merge_unique, merge_shallow
    
    dict1 = {"tags": ["python"], "config": {"debug": True}}
    dict2 = {"tags": ["web"], "config": {"port": 8000}}
    
    # Quick merge with default settings
    result1 = merge(dict1, dict2)
    print(f"Quick merge: {result1}")
    
    # Quick merge with unique lists
    result2 = merge_unique(dict1, dict2)
    print(f"Quick merge (unique): {result2}")
    
    # Quick shallow merge
    result3 = merge_shallow(dict1, dict2)
    print(f"Quick shallow merge: {result3}")


if __name__ == "__main__":
    basic_examples()
    list_strategies()
    dict_strategies()
    method_chaining()
    custom_strategies()
    real_world_example()
    convenience_functions() 