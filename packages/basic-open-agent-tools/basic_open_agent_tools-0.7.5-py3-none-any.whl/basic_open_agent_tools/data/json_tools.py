"""JSON processing utilities for AI agents."""

import gzip
import json

from ..exceptions import SerializationError


def safe_json_serialize(data: dict, indent: int) -> str:
    """Safely serialize data to JSON string with error handling.

    Args:
        data: Data to serialize to JSON (accepts any serializable type)
        indent: Number of spaces for indentation (0 for compact)

    Returns:
        JSON string representation of the data

    Raises:
        SerializationError: If data cannot be serialized to JSON
        TypeError: If data contains non-serializable objects

    Example:
        >>> safe_json_serialize({"name": "test", "value": 42})
        '{"name": "test", "value": 42}'
        >>> safe_json_serialize({"a": 1, "b": 2}, indent=2)
        '{\\n  "a": 1,\\n  "b": 2\\n}'
    """
    if not isinstance(indent, int):
        raise TypeError("indent must be an integer")

    try:
        # Use None for compact format when indent is 0
        actual_indent = None if indent == 0 else indent
        return json.dumps(data, indent=actual_indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize data to JSON: {e}")


def safe_json_deserialize(json_str: str) -> dict:
    """Safely deserialize JSON string to Python object with error handling.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Deserialized Python object

    Raises:
        SerializationError: If JSON string cannot be parsed
        TypeError: If input is not a string

    Example:
        >>> safe_json_deserialize('{"name": "test", "value": 42}')
        {'name': 'test', 'value': 42}
        >>> safe_json_deserialize('[1, 2, 3]')
        [1, 2, 3]
    """
    if not isinstance(json_str, str):
        raise TypeError("Input must be a string")

    try:
        result = json.loads(json_str)
        # Always return dict for agent compatibility
        if isinstance(result, dict):
            return result
        else:
            # Wrap non-dict results in a dict for consistency
            return {"result": result}
    except (json.JSONDecodeError, ValueError) as e:
        raise SerializationError(f"Failed to deserialize JSON string: {e}")


def validate_json_string(json_str: str) -> bool:
    """Validate JSON string without deserializing.

    Args:
        json_str: JSON string to validate

    Returns:
        True if valid JSON, False otherwise

    Example:
        >>> validate_json_string('{"valid": true}')
        True
        >>> validate_json_string('{"invalid": }')
        False
    """
    if not isinstance(json_str, str):
        return False  # type: ignore[unreachable]

    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def compress_json_data(data: dict) -> bytes:
    """Compress JSON data for storage or transmission.

    Args:
        data: Data to serialize and compress

    Returns:
        Compressed JSON data as bytes

    Raises:
        SerializationError: If data cannot be serialized or compressed
        TypeError: If data contains non-serializable objects

    Example:
        >>> compressed = compress_json_data({"test": "data"})
        >>> isinstance(compressed, bytes)
        True
    """
    try:
        json_str = safe_json_serialize(data, 0)
        return gzip.compress(json_str.encode("utf-8"))
    except Exception as e:
        raise SerializationError(f"Failed to compress JSON data: {e}")


def decompress_json_data(compressed_data: bytes) -> dict:
    """Decompress and deserialize JSON data.

    Args:
        compressed_data: Compressed JSON data as bytes

    Returns:
        Deserialized Python object

    Raises:
        SerializationError: If data cannot be decompressed or deserialized
        TypeError: If input is not bytes

    Example:
        >>> original = {"test": "data"}
        >>> compressed = compress_json_data(original)
        >>> decompressed = decompress_json_data(compressed)
        >>> decompressed == original
        True
    """
    if not isinstance(compressed_data, bytes):
        raise TypeError("Input must be bytes")

    try:
        json_str = gzip.decompress(compressed_data).decode("utf-8")
        return safe_json_deserialize(json_str)
    except Exception as e:
        raise SerializationError(f"Failed to decompress JSON data: {e}")
