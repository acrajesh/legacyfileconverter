"""
Display format handler for the EBCDIC to ASCII Converter.

This module handles conversion of DISPLAY format data (standard character representation).
"""

import re
from typing import Dict, Any, Optional


class DisplayHandler:
    """
    Handler for DISPLAY format data.
    
    This class provides methods for converting DISPLAY format data between EBCDIC and ASCII.
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field, encoding: str = 'cp037') -> str:
        """
        Convert EBCDIC DISPLAY data to ASCII.
        
        Args:
            data: Raw EBCDIC data
            field: Field object from the copybook parser
            encoding: EBCDIC encoding (default: cp037)
            
        Returns:
            str: ASCII representation of the data
        """
        # Decode the EBCDIC data to ASCII
        ascii_value = data.decode(encoding)
        
        # Apply special handling based on field attributes
        if field.justified_right:
            ascii_value = ascii_value.rstrip()
        
        if field.blank_when_zero and ascii_value.strip() == '0' * len(ascii_value.strip()):
            ascii_value = ' ' * len(ascii_value)
        
        return ascii_value
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> str:
        """
        Extract and convert a DISPLAY field from an EBCDIC record.
        
        Args:
            record: Complete EBCDIC record
            field: Field object from the copybook parser
            encoding: EBCDIC encoding (default: cp037)
            
        Returns:
            str: ASCII representation of the field
        """
        # Extract the field data from the record
        start = field.offset
        end = start + field.size
        field_data = record[start:end]
        
        # Convert to ASCII
        return DisplayHandler.ebcdic_to_ascii(field_data, field, encoding)
    
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
        # For alphanumeric fields, return as string
        if field.picture and ('X' in field.picture or 'A' in field.picture):
            return ascii_value
        
        # For numeric fields, try to convert to number
        if field.picture and '9' in field.picture:
            # Check if it's a decimal number
            if 'V' in field.picture or '.' in field.picture:
                # Determine decimal places
                decimal_places = 0
                if 'V' in field.picture:
                    # V indicates implied decimal point
                    v_pos = field.picture.find('V')
                    decimal_part = field.picture[v_pos+1:]
                    decimal_places = len(re.sub(r'\((\d+)\)', lambda m: '9' * int(m.group(1)), decimal_part))
                elif '.' in field.picture:
                    # Explicit decimal point
                    dot_pos = field.picture.find('.')
                    decimal_part = field.picture[dot_pos+1:]
                    decimal_places = len(re.sub(r'\((\d+)\)', lambda m: '9' * int(m.group(1)), decimal_part))
                
                # Insert decimal point if needed
                if 'V' in field.picture and '.' not in ascii_value:
                    if decimal_places > 0:
                        integer_part = ascii_value[:-decimal_places] if len(ascii_value) > decimal_places else '0'
                        decimal_part = ascii_value[-decimal_places:].ljust(decimal_places, '0')
                        ascii_value = f"{integer_part}.{decimal_part}"
                
                try:
                    return float(ascii_value)
                except ValueError:
                    return ascii_value
            else:
                # Integer
                try:
                    return int(ascii_value)
                except ValueError:
                    return ascii_value
        
        # Default to string
        return ascii_value
