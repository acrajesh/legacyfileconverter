"""
Packed decimal format handler for the EBCDIC to ASCII Converter.

This module handles conversion of COMP-3/PACKED-DECIMAL format data.
"""

from typing import Dict, Any, Optional


class PackedDecimalHandler:
    """
    Handler for COMP-3/PACKED-DECIMAL format data.
    
    This class provides methods for converting packed decimal format data between EBCDIC and ASCII.
    """
    
    @staticmethod
    def ebcdic_to_ascii(data: bytes, field) -> str:
        """
        Convert EBCDIC packed decimal data to ASCII.
        
        Args:
            data: Raw packed decimal data
            field: Field object from the copybook parser
            
        Returns:
            str: ASCII representation of the data
        """
        # Packed decimal format: each byte contains two decimal digits (except the last byte)
        # The last byte contains one digit and the sign (C for +, D for -)
        
        # Extract digits
        digits = []
        for i in range(len(data) - 1):
            byte = data[i]
            high_nibble = byte >> 4
            low_nibble = byte & 0x0F
            digits.append(str(high_nibble))
            digits.append(str(low_nibble))
        
        # Last byte contains one digit and sign
        last_byte = data[-1]
        last_digit = last_byte >> 4
        sign_nibble = last_byte & 0x0F
        
        digits.append(str(last_digit))
        
        # Determine sign
        is_negative = sign_nibble in (0x0B, 0x0D)  # B or D indicates negative
        
        # Combine digits and sign
        value = ''.join(digits)
        if is_negative:
            value = '-' + value
        
        return value
    
    @staticmethod
    def extract_from_record(record: bytes, field, encoding: str = 'cp037') -> Any:
        """
        Extract and convert a packed decimal field from an EBCDIC record.
        
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
        ascii_value = PackedDecimalHandler.ebcdic_to_ascii(field_data, field)
        
        # Convert to appropriate Python value
        return PackedDecimalHandler.to_dict_value(ascii_value, field)
    
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
        # For packed decimal fields, determine if it's a decimal or integer
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
