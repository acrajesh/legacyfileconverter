"""
Optional native binary format handler for the EBCDIC to ASCII Converter.

This module handles conversion of COMP-5 format data (native binary format).
"""

import struct
import sys
from typing import Dict, Any, Optional


class NativeBinaryHandler:
    """
    Handler for COMP-5 format data.
    
    This class provides methods for converting native binary format data between EBCDIC and ASCII.
    COMP-5 is similar to COMP/BINARY but uses the native byte order of the platform.
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field) -> str:
        """
        Convert EBCDIC native binary data to ASCII.
        
        Args:
            data: Raw binary data
            field: Field object from the copybook parser
            
        Returns:
            str: ASCII representation of the data
        """
        # Determine the format based on the field size
        # Use native byte order (< for little-endian, > for big-endian)
        byte_order = '<' if sys.byteorder == 'little' else '>'
        
        if len(data) == 2:
            # 2-byte binary (halfword)
            value = struct.unpack(f'{byte_order}h', data)[0]  # native short
        elif len(data) == 4:
            # 4-byte binary (fullword)
            value = struct.unpack(f'{byte_order}i', data)[0]  # native int
        elif len(data) == 8:
            # 8-byte binary (doubleword)
            value = struct.unpack(f'{byte_order}q', data)[0]  # native long long
        else:
            # Unsupported size, return as string of hex values
            return ' '.join(f'{b:02x}' for b in data)
        
        # Convert to string
        return str(value)
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> Any:
        """
        Extract and convert a native binary field from an EBCDIC record.
        
        Args:
            record: Complete EBCDIC record
            field: Field object from the copybook parser
            encoding: EBCDIC encoding (default: cp037)
            
        Returns:
            Any: Python representation of the field
        """
        # Extract the field data from the record
        start = field.offset
        end = start + field.size
        field_data = record[start:end]
        
        # Convert to ASCII string
        ascii_value = NativeBinaryHandler.ebcdic_to_ascii(field_data, field)
        
        # Convert to appropriate Python value
        return NativeBinaryHandler.to_dict_value(ascii_value, field)
    
    @staticmethod
    def to_dict_value(ascii_value: str, field) -> Any:
        """
        Convert ASCII string to appropriate Python value for dictionary representation.
        
        Args:
            ascii_value: ASCII string value
            field: Field object from the copybook parser
            
        Returns:
            Any: Python representation of the value
        """
        # For binary fields, convert to integer or float
        try:
            # Check if it's a decimal number
            if field.picture and ('V' in field.picture or '.' in field.picture):
                return float(ascii_value)
            else:
                return int(ascii_value)
        except ValueError:
            # If conversion fails, return as string
            return ascii_value
