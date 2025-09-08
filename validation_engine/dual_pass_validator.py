"""
Dual-pass validator for the EBCDIC to ASCII Converter.

This module implements the independent dual-pass validation strategy for
verifying conversion accuracy.
"""

import os
from typing import Dict, Any, List, Optional, Tuple

from ebcdic_converter.copybook_parser import parse_copybook, Field
from ebcdic_converter.ebcdic_reader import EbcdicReader
from ebcdic_converter.conversion_engine import ConversionEngine
from ebcdic_converter.validation_engine.normalization import normalize_value
from ebcdic_converter.validation_engine.error_classifier import classify_error
from ebcdic_converter.validation_engine.report_generator import generate_report


class DualPassValidator:
    """
    Dual-pass validator for EBCDIC to ASCII conversion.
    
    This class implements the independent dual-pass validation strategy,
    which performs a second independent conversion of the original EBCDIC data
    and compares it to the initial conversion output.
    """
    
    def __init__(self, ebcdic_file: str, ascii_file: str, structure: Field,
                 encoding: str = 'cp037', tolerance: float = 0.01):
        """
        Initialize the dual-pass validator.
        
        Args:
            ebcdic_file: Path to the original EBCDIC file
            ascii_file: Path to the converted ASCII file
            structure: Root field of the parsed copybook structure
            encoding: EBCDIC encoding (default: cp037)
            tolerance: Numeric tolerance for comparisons (default: 0.01)
        """
        self.ebcdic_file = ebcdic_file
        self.ascii_file = ascii_file
        self.structure = structure
        self.encoding = encoding
        self.tolerance = tolerance
    
    def validate(self) -> Dict[str, Any]:
        """
        Perform dual-pass validation.
        
        Returns:
            dict: Validation results including statistics and mismatches
        """
        # Initialize results
        results = {
            'total_records': 0,
            'total_fields': 0,
            'mismatches': 0,
            'mismatch_details': []
        }
        
        # Create a new conversion engine for the second pass
        engine = ConversionEngine(self.structure, self.encoding)
        
        # Open the EBCDIC file for the second pass
        ebcdic_reader = EbcdicReader(self.ebcdic_file, encoding=self.encoding)
        
        # Open the ASCII file to read the first pass results
        # This is a simplified approach; in a real implementation,
        # we would need to parse the ASCII file based on its format
        with open(self.ascii_file, 'r', encoding='utf-8') as f:
            ascii_lines = f.readlines()
        
        # Perform validation record by record
        for record_index, (ebcdic_record, ascii_line) in enumerate(zip(ebcdic_reader, ascii_lines)):
            # Convert the EBCDIC record in the second pass
            second_pass_result = engine.convert(ebcdic_record)
            
            # Parse the ASCII line from the first pass
            # This is a simplified approach; in a real implementation,
            # we would need to parse the ASCII line based on its format
            first_pass_result = self._parse_ascii_line(ascii_line)
            
            # Compare the results
            record_mismatches = self._compare_records(
                first_pass_result, second_pass_result, record_index
            )
            
            # Update statistics
            results['total_records'] += 1
            results['total_fields'] += len(self._flatten_dict(first_pass_result))
            results['mismatches'] += len(record_mismatches)
            results['mismatch_details'].extend(record_mismatches)
        
        return results
    
    def _parse_ascii_line(self, line: str) -> Dict[str, Any]:
        """
        Parse an ASCII line from the first pass.
        
        This is a simplified implementation that assumes a specific format.
        In a real implementation, this would need to be more sophisticated.
        
        Args:
            line: ASCII line from the first pass
            
        Returns:
            dict: Parsed record as a dictionary
        """
        # This is a placeholder implementation
        # In a real implementation, we would parse the line based on the output format
        # For now, we'll just return an empty dictionary
        return {}
    
    def _compare_records(self, first_pass: Dict[str, Any], second_pass: Dict[str, Any],
                        record_index: int) -> List[Dict[str, Any]]:
        """
        Compare two records and identify mismatches.
        
        Args:
            first_pass: Record from the first pass
            second_pass: Record from the second pass
            record_index: Index of the record
            
        Returns:
            list: List of mismatch details
        """
        mismatches = []
        
        # Flatten both dictionaries for easier comparison
        flat_first = self._flatten_dict(first_pass)
        flat_second = self._flatten_dict(second_pass)
        
        # Check for fields in first pass that are missing in second pass
        for field_path, first_value in flat_first.items():
            if field_path not in flat_second:
                mismatches.append({
                    'record_index': record_index,
                    'field_path': field_path,
                    'first_pass': first_value,
                    'second_pass': None,
                    'error_type': 'missing_field',
                    'error_details': 'Field present in first pass but missing in second pass'
                })
                continue
            
            # Get the second pass value
            second_value = flat_second[field_path]
            
            # Normalize values for comparison
            norm_first = normalize_value(first_value)
            norm_second = normalize_value(second_value)
            
            # Compare normalized values
            if not self._values_equal(norm_first, norm_second):
                # Values don't match, classify the error
                error_type, error_details = classify_error(
                    norm_first, norm_second, self.tolerance
                )
                
                mismatches.append({
                    'record_index': record_index,
                    'field_path': field_path,
                    'first_pass': first_value,
                    'second_pass': second_value,
                    'error_type': error_type,
                    'error_details': error_details
                })
        
        # Check for fields in second pass that are missing in first pass
        for field_path, second_value in flat_second.items():
            if field_path not in flat_first:
                mismatches.append({
                    'record_index': record_index,
                    'field_path': field_path,
                    'first_pass': None,
                    'second_pass': second_value,
                    'error_type': 'missing_field',
                    'error_details': 'Field present in second pass but missing in first pass'
                })
        
        return mismatches
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten a nested dictionary.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested dictionaries
            
        Returns:
            dict: Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _values_equal(self, value1: Any, value2: Any) -> bool:
        """
        Check if two values are equal, with tolerance for numeric values.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            bool: True if values are equal, False otherwise
        """
        # Check for None
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False
        
        # Check for numeric values
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            # Use tolerance for floating point comparisons
            if isinstance(value1, float) or isinstance(value2, float):
                return abs(value1 - value2) <= self.tolerance
            else:
                return value1 == value2
        
        # Check for strings
        if isinstance(value1, str) and isinstance(value2, str):
            # Normalize strings by stripping whitespace
            return value1.strip() == value2.strip()
        
        # Default comparison
        return value1 == value2
    
    def generate_report(self, results: Dict[str, Any], report_file: str):
        """
        Generate a validation report.
        
        Args:
            results: Validation results
            report_file: Path to the report file
        """
        generate_report(results, report_file)
