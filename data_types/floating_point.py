"""
Floating point format handler for the EBCDIC to ASCII Converter.

This module handles conversion of COMP-1 and COMP-2 format data (floating point).
"""

import struct
from typing import Dict, Any, Optional


class FloatingPointHandler:
    """
    Handler for COMP-1 and COMP-2 format data.
    
    This class provides methods for converting floating point format data between EBCDIC and ASCII.
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field) -> str:
        """
        Convert EBCDIC floating point data to ASCII.
        
        Args:
            data: Raw floating point data
            field: Field object from the copybook parser
            
        Returns:
            str: ASCII representation of the data
        """
        # Determine the format based on the field size and usage
        if field.usage == 'COMP-1' or len(data) == 4:
            # Single-precision float (32-bit)
            value = struct.unpack('>f', data)[0]  # big-endian float
        elif field.usage == 'COMP-2' or len(data) == 8:
            # Double-precision float (64-bit)
            value = struct.unpack('>d', data)[0]  # big-endian double
        else:
            # Unsupported size, return as string of hex values
            return ' '.join(f'{b:02x}' for b in data)
        
        # Convert to string with appropriate precision
        if field.usage == 'COMP-1':
            return f"{value:.7g}"  # 7 significant digits for single precision
        else:
            return f"{value:.16g}"  # 16 significant digits for double precision
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> Any:
        """
        Extract and convert a floating point field from an EBCDIC record.
        
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
        ascii_value = FloatingPointHandler.ebcdic_to_ascii(field_data, field)
        
        # Convert to appropriate Python value
        return FloatingPointHandler.to_dict_value(ascii_value, field)
    
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
        # For floating point fields, convert to float
        try:
            return float(ascii_value)
        except ValueError:
            # If conversion fails, return as string
            return ascii_value
