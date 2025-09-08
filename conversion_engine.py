"""
Conversion engine for the EBCDIC to ASCII Converter.

This module handles the core conversion logic for transforming EBCDIC data to ASCII
based on COBOL copybook structure definitions.
"""

from typing import Dict, Any, List, Optional
from ebcdic_converter.copybook_parser import Field
from ebcdic_converter.data_types import get_handler_for_field


class ConversionEngine:
    """
    Core conversion engine for transforming EBCDIC data to ASCII.
    
    This class handles the conversion of EBCDIC records to ASCII based on
    the structure defined in a COBOL copybook.
    """
    
    def __init__(self, structure: Field, encoding: str = 'cp037'):
        """
        Initialize the conversion engine.
        
        Args:
            structure: Root field of the parsed copybook structure
            encoding: EBCDIC encoding (default: cp037)
        """
        self.structure = structure
        self.encoding = encoding
        
    def convert(self, ebcdic_record: bytes) -> Dict[str, Any]:
        """
        Convert an EBCDIC record to ASCII.
        
        Args:
            ebcdic_record: Raw EBCDIC record data
            
        Returns:
            dict: Dictionary containing field names and converted values
        """
        # Start with an empty result dictionary
        result = {}
        
        # Process the record structure
        self._process_field(ebcdic_record, self.structure, result)
        
        return result
    
    def _process_field(self, record: bytes, field: Field, result: Dict[str, Any], parent_path: str = ''):
        """
        Process a field and its children recursively.
        
        Args:
            record: Raw EBCDIC record data
            field: Field to process
            result: Dictionary to store results
            parent_path: Path to parent field for nested structures
        """
        # Skip the root field
        if field.level == 0:
            # Process children of root
            for child in field.children:
                self._process_field(record, child, result, parent_path)
            return
        
        # Skip FILLER fields
        if field.is_filler:
            return
        
        # Skip 88-level condition items
        if field.level == 88:
            return
        
        # Determine the field path
        field_path = f"{parent_path}.{field.name}" if parent_path else field.name
        
        # Handle REDEFINES
        if field.redefines:
            # For REDEFINES, we process both the original and the redefined field
            # The redefined field will overwrite the original in the result
            pass
        
        # Process group items
        if field.is_group:
            # For group items, create a nested dictionary
            group_result = {}
            
            # Process children
            for child in field.children:
                self._process_field(record, child, group_result, field_path)
            
            # Add group to result
            result[field.name] = group_result
            return
        
        # Process elementary items
        if field.picture or field.usage:
            # Get the appropriate handler for this field type
            handler = get_handler_for_field(field)
            
            # Extract and convert the field value
            if hasattr(handler, 'extract_from_record'):
                value = handler.extract_from_record(record, field, self.encoding)
            else:
                # Fallback for handlers that don't implement extract_from_record
                start = field.offset
                end = start + field.size
                field_data = record[start:end]
                
                if hasattr(handler, 'ebcdic_to_ascii'):
                    ascii_value = handler.ebcdic_to_ascii(field_data, field, self.encoding)
                else:
                    # Last resort fallback
                    ascii_value = field_data.decode(self.encoding)
                
                if hasattr(handler, 'to_dict_value'):
                    value = handler.to_dict_value(ascii_value, field)
                else:
                    value = ascii_value
            
            # Handle OCCURS
            if field.occurs and field.occurs > 1:
                # For OCCURS, create a list of values
                # This is a simplified approach; a more complete implementation
                # would handle nested OCCURS and DEPENDING ON
                result[field.name] = value
            else:
                # Add to result
                result[field.name] = value
    
    def convert_batch(self, ebcdic_records: List[bytes]) -> List[Dict[str, Any]]:
        """
        Convert a batch of EBCDIC records to ASCII.
        
        Args:
            ebcdic_records: List of raw EBCDIC record data
            
        Returns:
            list: List of dictionaries containing field names and converted values
        """
        return [self.convert(record) for record in ebcdic_records]
