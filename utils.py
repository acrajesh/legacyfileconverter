"""
Utility functions for the EBCDIC to ASCII Converter.

This module provides utility functions for endianness handling, formatting,
and other general helpers.
"""

import sys
import struct
from typing import Any, Dict, List, Optional


def is_big_endian():
    """
    Check if the system is big-endian.
    
    Returns:
        bool: True if the system is big-endian, False if little-endian
    """
    return sys.byteorder == 'big'


def swap_endianness(data: bytes) -> bytes:
    """
    Swap the endianness of a byte sequence.
    
    Args:
        data: Byte sequence to swap
        
    Returns:
        bytes: Byte sequence with swapped endianness
    """
    # Swap bytes in pairs
    return b''.join(data[i:i+2][::-1] for i in range(0, len(data), 2))


def format_hex_dump(data: bytes, bytes_per_line: int = 16) -> str:
    """
    Format a byte sequence as a hex dump.
    
    Args:
        data: Byte sequence to format
        bytes_per_line: Number of bytes per line in the output
        
    Returns:
        str: Formatted hex dump
    """
    result = []
    
    for i in range(0, len(data), bytes_per_line):
        # Get a chunk of bytes
        chunk = data[i:i+bytes_per_line]
        
        # Format as hex
        hex_values = ' '.join(f'{b:02x}' for b in chunk)
        
        # Format as ASCII (printable characters only)
        ascii_values = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        
        # Add line to result
        result.append(f'{i:08x}  {hex_values:<{bytes_per_line*3}}  {ascii_values}')
    
    return '\n'.join(result)


def format_field_value(value: Any, field_type: str, width: int = 0) -> str:
    """
    Format a field value for display.
    
    Args:
        value: Value to format
        field_type: Type of the field ('numeric', 'string', etc.)
        width: Width of the field for padding
        
    Returns:
        str: Formatted value
    """
    if value is None:
        return ' ' * width if width > 0 else ''
    
    if field_type == 'numeric':
        if isinstance(value, float):
            # Format float with appropriate precision
            formatted = f'{value:.6g}'
        else:
            # Format integer
            formatted = str(value)
    elif field_type == 'string':
        # Format string
        formatted = str(value)
    else:
        # Default formatting
        formatted = str(value)
    
    # Pad to width if specified
    if width > 0:
        return formatted.ljust(width)
    
    return formatted


def get_record_length_from_structure(structure) -> int:
    """
    Calculate the record length from a structure definition.
    
    Args:
        structure: Root field of the parsed copybook structure
        
    Returns:
        int: Record length in bytes
    """
    # The size of the root field is the record length
    return structure.size


def create_sample_record(structure, fill_value: bytes = b'\x00') -> bytes:
    """
    Create a sample record based on a structure definition.
    
    Args:
        structure: Root field of the parsed copybook structure
        fill_value: Byte value to fill the record with
        
    Returns:
        bytes: Sample record
    """
    # Create a record of the appropriate length filled with the fill value
    record_length = get_record_length_from_structure(structure)
    return fill_value * record_length
