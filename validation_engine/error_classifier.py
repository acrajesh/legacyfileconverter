"""
Error classifier for the EBCDIC to ASCII Converter validation engine.

This module provides functions for classifying errors in validation results.
"""

from typing import Any, Tuple


def classify_error(value1: Any, value2: Any, tolerance: float = 0.01) -> Tuple[str, str]:
    """
    Classify the error between two values.
    
    Args:
        value1: First value
        value2: Second value
        tolerance: Numeric tolerance for comparisons
        
    Returns:
        tuple: (error_type, error_details)
    """
    # Check for None values
    if value1 is None or value2 is None:
        return "missing_value", "One of the values is None"
    
    # Check for type mismatches
    if type(value1) != type(value2):
        return "type_mismatch", f"Type mismatch: {type(value1).__name__} vs {type(value2).__name__}"
    
    # Handle numeric values
    if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        return classify_numeric_error(value1, value2, tolerance)
    
    # Handle string values
    if isinstance(value1, str) and isinstance(value2, str):
        return classify_string_error(value1, value2)
    
    # Default error classification
    return "unknown_error", "Unknown error type"


def classify_numeric_error(value1: float, value2: float, tolerance: float) -> Tuple[str, str]:
    """
    Classify the error between two numeric values.
    
    Args:
        value1: First numeric value
        value2: Second numeric value
        tolerance: Numeric tolerance for comparisons
        
    Returns:
        tuple: (error_type, error_details)
    """
    # Check for sign errors
    if value1 * value2 < 0:
        return "sign_error", f"Sign mismatch: {value1} vs {value2}"
    
    # Check for off-by-one errors
    if abs(value1 - value2) == 1:
        return "off_by_one", f"Off by one: {value1} vs {value2}"
    
    # Check for precision loss
    if abs(value1 - value2) <= tolerance:
        return "precision_loss", f"Precision loss within tolerance: {value1} vs {value2}"
    
    # Check for scale errors (factor of 10, 100, etc.)
    for i in range(1, 10):
        factor = 10 ** i
        if abs(value1 * factor - value2) < tolerance or abs(value1 - value2 * factor) < tolerance:
            return "scale_error", f"Scale error (factor of 10^{i}): {value1} vs {value2}"
    
    # Default numeric error
    return "numeric_mismatch", f"Numeric values don't match: {value1} vs {value2}"


def classify_string_error(value1: str, value2: str) -> Tuple[str, str]:
    """
    Classify the error between two string values.
    
    Args:
        value1: First string value
        value2: Second string value
        
    Returns:
        tuple: (error_type, error_details)
    """
    # Check for whitespace differences
    if value1.strip() == value2.strip():
        return "whitespace_error", "Whitespace differences only"
    
    # Check for case differences
    if value1.lower() == value2.lower():
        return "case_error", "Case differences only"
    
    # Check for character encoding issues
    encoding_issue = False
    for c1, c2 in zip(value1, value2):
        if c1 != c2 and (ord(c1) > 127 or ord(c2) > 127):
            encoding_issue = True
            break
    
    if encoding_issue:
        return "character_encoding", "Possible character encoding issues"
    
    # Check for truncation
    if value1.startswith(value2) or value2.startswith(value1):
        return "truncation", "One string appears to be truncated"
    
    # Default string error
    return "string_mismatch", f"String values don't match: '{value1}' vs '{value2}'"
