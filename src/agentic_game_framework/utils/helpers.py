"""
Utility Helpers for Agentic Game Framework.

This module provides common utility functions that can be used across
different components of the framework.
"""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar, Union

T = TypeVar('T')


def generate_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        str: A unique identifier
    """
    return str(uuid.uuid4())


def timestamp_now() -> float:
    """
    Get the current timestamp.
    
    Returns:
        float: Current timestamp in seconds since epoch
    """
    return time.time()


def datetime_now() -> datetime:
    """
    Get the current datetime.
    
    Returns:
        datetime: Current datetime
    """
    return datetime.now()


def datetime_to_timestamp(dt: datetime) -> float:
    """
    Convert a datetime to a timestamp.
    
    Args:
        dt: Datetime to convert
        
    Returns:
        float: Timestamp in seconds since epoch
    """
    return dt.timestamp()


def timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert a timestamp to a datetime.
    
    Args:
        timestamp: Timestamp in seconds since epoch
        
    Returns:
        datetime: Corresponding datetime
    """
    return datetime.fromtimestamp(timestamp)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime as a string.
    
    Args:
        dt: Datetime to format
        format_str: Format string
        
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime from a string.
    
    Args:
        datetime_str: String to parse
        format_str: Format string
        
    Returns:
        datetime: Parsed datetime
        
    Raises:
        ValueError: If the string cannot be parsed
    """
    return datetime.strptime(datetime_str, format_str)


def ensure_dir(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Any: Loaded data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Any, file_path: str, indent: Optional[int] = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the JSON file
        indent: Indentation level (None for compact JSON)
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries, with dict2 values taking precedence.
    
    If both dict1 and dict2 have a dictionary at the same key, their contents
    will be merged recursively.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if (
            key in result and
            isinstance(result[key], dict) and
            isinstance(value, dict)
        ):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result


def filter_dict(
    data: Dict[str, Any],
    keys: Optional[List[str]] = None,
    exclude_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Filter a dictionary to include or exclude specific keys.
    
    Args:
        data: Dictionary to filter
        keys: Keys to include (if None, include all)
        exclude_keys: Keys to exclude
        
    Returns:
        Dict[str, Any]: Filtered dictionary
    """
    result = {}
    
    exclude_keys = exclude_keys or []
    exclude_set = set(exclude_keys)
    
    if keys is None:
        # Include all keys except excluded ones
        for key, value in data.items():
            if key not in exclude_set:
                result[key] = value
    else:
        # Include only specified keys, except excluded ones
        keys_set = set(keys)
        for key in keys_set - exclude_set:
            if key in data:
                result[key] = data[key]
                
    return result


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between a minimum and maximum.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(max_value, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        float: Interpolated value
    """
    return a + (b - a) * clamp(t, 0.0, 1.0)


def distance(a: float, b: float) -> float:
    """
    Calculate the absolute distance between two values.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        float: Absolute distance
    """
    return abs(b - a)


def find_closest(
    value: float,
    candidates: List[float]
) -> Optional[float]:
    """
    Find the closest value in a list of candidates.
    
    Args:
        value: Target value
        candidates: List of candidate values
        
    Returns:
        Optional[float]: Closest value, or None if candidates is empty
    """
    if not candidates:
        return None
        
    return min(candidates, key=lambda x: distance(x, value))


def find_closest_item(
    value: float,
    items: List[T],
    key_func: callable
) -> Optional[T]:
    """
    Find the item with the closest value according to a key function.
    
    Args:
        value: Target value
        items: List of items
        key_func: Function to extract the comparison value from an item
        
    Returns:
        Optional[T]: Closest item, or None if items is empty
    """
    if not items:
        return None
        
    return min(items, key=lambda x: distance(key_func(x), value))


def weighted_choice(
    items: List[T],
    weights: List[float]
) -> T:
    """
    Choose an item from a list with weighted probability.
    
    Args:
        items: List of items to choose from
        weights: List of weights corresponding to items
        
    Returns:
        T: Chosen item
        
    Raises:
        ValueError: If items and weights have different lengths
        ValueError: If any weight is negative
        ValueError: If all weights are zero
    """
    if len(items) != len(weights):
        raise ValueError("Items and weights must have the same length")
        
    if any(w < 0 for w in weights):
        raise ValueError("Weights cannot be negative")
        
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("At least one weight must be positive")
        
    # Choose a random point in the total weight range
    import random
    r = random.random() * total_weight
    
    # Find the item at that point
    current = 0
    for i, w in enumerate(weights):
        current += w
        if r <= current:
            return items[i]
            
    # Fallback (should not happen due to floating point precision)
    return items[-1]


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of a specified size.
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List[List[T]]: List of chunks
    """
    return [
        items[i:i + chunk_size]
        for i in range(0, len(items), chunk_size)
    ]


def flatten_list(nested_list: List[List[T]]) -> List[T]:
    """
    Flatten a nested list.
    
    Args:
        nested_list: Nested list to flatten
        
    Returns:
        List[T]: Flattened list
    """
    return [item for sublist in nested_list for item in sublist]


def unique_items(items: List[T]) -> List[T]:
    """
    Get unique items from a list, preserving order.
    
    Args:
        items: List with potential duplicates
        
    Returns:
        List[T]: List with duplicates removed
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
            
    return result