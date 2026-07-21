"""Test helper utilities."""


def assert_dict_subset(subset: dict, superset: dict) -> None:
    """Assert that all key-value pairs in subset exist in superset."""
    for key, value in subset.items():
        assert key in superset, f"Key '{key}' not found"
        assert superset[key] == value, f"Key '{key}': expected {value}, got {superset[key]}"
