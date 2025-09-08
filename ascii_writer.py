"""
ASCII writer for the EBCDIC to ASCII Converter.

This module handles writing converted ASCII records to output files.
"""

import csv
import json
from typing import Dict, List, Any, Optional, TextIO


class AsciiWriter:
    """
    Writer for ASCII output files.
    
    This class provides an interface for writing converted records to ASCII files
    in various formats (flat, CSV, JSON).
    """
    
    def __init__(self, file_path: str, format: str = 'flat'):
        """
        Initialize the ASCII writer.
        
        Args:
            file_path: Path to the output file
            format: Output format ('flat', 'csv', or 'json')
        """
        self.file_path = file_path
        self.format = format.lower()
        self.file = None
        self.csv_writer = None
        self.json_records = []
        
        # Validate format
        if self.format not in ['flat', 'csv', 'json']:
            raise ValueError(f"Unsupported output format: {format}")
        
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def open(self):
        """Open the output file for writing."""
        if self.file is None:
            self.file = open(self.file_path, 'w', newline='', encoding='utf-8')
            
            # Set up CSV writer if needed
            if self.format == 'csv':
                self.csv_writer = csv.DictWriter(self.file, fieldnames=[])
                self.csv_writer.fieldnames = None  # Will be set on first write
                
    def close(self):
        """Close the output file."""
        if self.file is not None:
            # Write JSON records if in JSON format
            if self.format == 'json':
                json.dump(self.json_records, self.file, indent=2)
                
            self.file.close()
            self.file = None
            
    def write(self, record: Dict[str, Any]):
        """
        Write a record to the output file.
        
        Args:
            record: Dictionary containing field names and values
        """
        if self.file is None:
            self.open()
            
        if self.format == 'flat':
            # For flat format, just write the values as a string
            values = []
            for field_name, value in record.items():
                if isinstance(value, (list, dict)):
                    # Convert complex structures to string representation
                    values.append(str(value))
                else:
                    values.append(str(value))
            
            self.file.write(''.join(values) + '\n')
            
        elif self.format == 'csv':
            # For CSV format, use the CSV writer
            if self.csv_writer.fieldnames is None:
                # First record, set up the fieldnames
                self.csv_writer.fieldnames = list(record.keys())
                self.csv_writer.writeheader()
                
            self.csv_writer.writerow(record)
            
        elif self.format == 'json':
            # For JSON format, collect records to write at close
            self.json_records.append(record)
