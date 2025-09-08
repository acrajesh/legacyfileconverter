"""
Optional unsigned packed decimal format handler for the EBCDIC to ASCII Converter.

This module handles conversion of COMP-6 format data (unsigned packed decimal).
"""

from typing import Dict, Any, Optional


class UnsignedPackedHandler:
    """
    Handler for COMP-6 format data.
    
    This class provides methods for converting unsigned packed decimal format data between EBCDIC and ASCII.
    COMP-6 is similar to COMP-3 but without a sign nibble (all digits are packed).
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field) -> str:
        """
        Convert EBCDIC unsigned packed decimal data to ASCII.
        
        Args:
            data: Raw unsigned packed decimal data
            field: Field object from the copybook parser
            
        Returns:
            str: ASCII representation of the data
        """
        # Unsigned packed decimal format: each byte contains two decimal digits
        
        # Extract digits
        digits = []
        for byte in data:
            high_nibble = byte >> 4
            low_nibble = byte & 0x0F
            digits.append(str(high_nibble))
            digits.append(str(low_nibble))
        
        # Combine digits
        value = ''.join(digits)
        
        # Remove leading zeros
        value = value.lstrip('0')
        if not value:
            value = '0'  # If all zeros, return '0'
        
        return value
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> Any:
        """
        Extract and convert an unsigned packed decimal field from an EBCDIC record.
        
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
        ascii_value = UnsignedPackedHandler.ebcdic_to_ascii(field_data, field)
        
        # Convert to appropriate Python value
        return UnsignedPackedHandler.to_dict_value(ascii_value, field)
    
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
        # For unsigned packed decimal fields, determine if it's a decimal or integer
        try:
            # Check if it's a decimal number
            if field.picture and ('V' in field.picture or '.' in field.picture):
                # Determine decimal places
                decimal_places = 0
                if 'V' in field.picture:
                    # V indicates implied decimal point
                    v_pos = field.picture.find('V')
                    decimal_part = field.picture[v_pos+1:]
                    decimal_places = sum(1 for c in decimal_part if c in '9')
                
                # Insert decimal point
                if decimal_places > 0:
                    integer_part = ascii_value[:-decimal_places] if len(ascii_value) > decimal_places else '0'
                    decimal_part = ascii_value[-decimal_places:].ljust(decimal_places, '0')
                    value = f"{integer_part}.{decimal_part}"
                    return float(value)
                else:
                    return int(ascii_value)
            else:
                return int(ascii_value)
        except ValueError:
            # If conversion fails, return as string
            return ascii_value
