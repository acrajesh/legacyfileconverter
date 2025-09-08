"""
Normalization module for the EBCDIC to ASCII Converter validation engine.

This module provides functions for normalizing values before comparison
to avoid false positive mismatches.
"""

from typing import Any, Union, Dict, List


def normalize_value(value: Any) -> Any:
    """
    Normalize a value for comparison.
    
    Args:
        value: Value to normalize
        
    Returns:
        Normalized value
    """
    if value is None:
        return None
    
    # Normalize numeric values
    if isinstance(value, (int, float)):
        return normalize_numeric(value)
    
    # Normalize strings
    if isinstance(value, str):
        return normalize_string(value)
    
    # Normalize lists
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    
    # Normalize dictionaries
    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    
    # Return other types as is
    return value


def normalize_numeric(value: Union[int, float]) -> Union[int, float]:
    """
    Normalize a numeric value.
    
    Args:
        value: Numeric value to normalize
        
    Returns:
        Normalized numeric value
    """
    # Convert to float for consistent handling
    float_value = float(value)
    
    # Check if it's an integer value
    if float_value.is_integer():
        return int(float_value)
    
    # For floating point, strip trailing zeros
    # Convert to string, strip zeros, and convert back to float
    str_value = f"{float_value:.10f}".rstrip('0').rstrip('.')
    return float(str_value) if '.' in str_value else int(str_value)


def normalize_string(value: str) -> str:
    """
    Normalize a string value.
    
    Args:
        value: String value to normalize
        
    Returns:
        Normalized string value
    """
    # Strip leading and trailing whitespace
    normalized = value.strip()
    
    # Try to convert to numeric if it looks like a number
    if is_numeric_string(normalized):
        try:
            # Try to convert to float
            float_value = float(normalized)
            
            # If it's an integer, convert to int
            if float_value.is_integer():
                return int(float_value)
            
            # Otherwise, return as float
            return float_value
        except ValueError:
            # If conversion fails, return as string
            pass
    
    return normalized


def is_numeric_string(value: str) -> bool:
    """
    Check if a string represents a numeric value.
    
    Args:
        value: String to check
        
    Returns:
        bool: True if the string represents a numeric value, False otherwise
    """
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Check if it's empty
    if not value:
        return False
    
    # Check if it's a negative number
    if value.startswith('-'):
        value = value[1:]
    
    # Check if it's a decimal number
    if '.' in value:
        parts = value.split('.')
        if len(parts) != 2:
            return False
        return parts[0].isdigit() and parts[1].isdigit()
    
    # Check if it's an integer
    return value.isdigit()
