"""
Signed format handler for the EBCDIC to ASCII Converter.

This module handles conversion of SIGN LEADING/TRAILING SEPARATE format data.
"""

from typing import Dict, Any, Optional


class SignedHandler:
    """
    Handler for SIGN LEADING/TRAILING SEPARATE format data.
    
    This class provides methods for converting signed format data between EBCDIC and ASCII.
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field, encoding: str = 'cp037') -> str:
        """
        Convert EBCDIC signed data to ASCII.
        
        Args:
            data: Raw EBCDIC data
            field: Field object from the copybook parser
            encoding: EBCDIC encoding (default: cp037)
            
        Returns:
            str: ASCII representation of the data
        """
        # Decode the EBCDIC data to ASCII
        ascii_value = data.decode(encoding)
        
        # Handle sign based on SIGN LEADING or TRAILING
        if field.sign_separate:
            if field.sign_leading:
                # Sign is at the beginning
                sign_char = ascii_value[0]
                value = ascii_value[1:]
                
                # Convert sign character to +/- prefix
                if sign_char in ['+', 'C']:
                    return value
                elif sign_char in ['-', 'D']:
                    return '-' + value
                else:
                    # Invalid sign, treat as positive
                    return value
            else:
                # Sign is at the end
                sign_char = ascii_value[-1]
                value = ascii_value[:-1]
                
                # Convert sign character to +/- prefix
                if sign_char in ['+', 'C']:
                    return value
                elif sign_char in ['-', 'D']:
                    return '-' + value
                else:
                    # Invalid sign, treat as positive
                    return value
        else:
            # No separate sign, just return the value
            return ascii_value
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> Any:
        """
        Extract and convert a signed field from an EBCDIC record.
        
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
        
        # Convert to ASCII
        ascii_value = SignedHandler.ebcdic_to_ascii(field_data, field, encoding)
        
        # Convert to appropriate Python value
        return SignedHandler.to_dict_value(ascii_value, field)
    
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
        # For signed numeric fields, convert to integer or float
        try:
            # Check if it's a decimal number
            if 'V' in field.picture or '.' in field.picture:
                # Determine decimal places
                decimal_places = 0
                if 'V' in field.picture:
                    # V indicates implied decimal point
                    v_pos = field.picture.find('V')
                    decimal_part = field.picture[v_pos+1:]
                    decimal_places = sum(1 for c in decimal_part if c in '9')
                
                # Insert decimal point
                if decimal_places > 0:
                    value = ascii_value
                    if value.startswith('-'):
                        integer_part = value[1:-decimal_places] if len(value) > decimal_places + 1 else '0'
                        decimal_part = value[-decimal_places:].ljust(decimal_places, '0')
                        value = f"-{integer_part}.{decimal_part}"
                    else:
                        integer_part = value[:-decimal_places] if len(value) > decimal_places else '0'
                        decimal_part = value[-decimal_places:].ljust(decimal_places, '0')
                        value = f"{integer_part}.{decimal_part}"
                    
                    return float(value)
                else:
                    return int(ascii_value)
            else:
                return int(ascii_value)
        except ValueError:
            # If conversion fails, return as string
            return ascii_value
