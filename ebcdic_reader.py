"""
EBCDIC reader for the EBCDIC to ASCII Converter.

This module handles reading fixed-block EBCDIC records from files.
"""

import os
from typing import Iterator, Optional, BinaryIO


class EbcdicReader:
    """
    Reader for fixed-block EBCDIC files.
    
    This class provides a streaming interface for reading fixed-length records
    from an EBCDIC-encoded file.
    """
    
    def __init__(self, file_path: str, record_length: Optional[int] = None, 
                 encoding: str = 'cp037', buffer_size: int = 8192):
        """
        Initialize the EBCDIC reader.
        
        Args:
            file_path: Path to the EBCDIC file
            record_length: Length of each record in bytes (if None, will be determined from the file)
            encoding: EBCDIC encoding (default: cp037)
            buffer_size: Size of the buffer for file reading
        """
        self.file_path = file_path
        self.encoding = encoding
        self.buffer_size = buffer_size
        self.file_size = os.path.getsize(file_path)
        self.file = None
        
        # If record length is not provided, try to determine it
        self._record_length = record_length
        
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def __iter__(self) -> Iterator[bytes]:
        """
        Iterate over records in the EBCDIC file.
        
        Yields:
            bytes: Raw EBCDIC record data
        """
        self.open()
        
        try:
            while True:
                record = self.read_record()
                if not record:
                    break
                yield record
        finally:
            self.close()
            
    def open(self):
        """Open the EBCDIC file for reading."""
        if self.file is None:
            self.file = open(self.file_path, 'rb')
            
    def close(self):
        """Close the EBCDIC file."""
        if self.file is not None:
            self.file.close()
            self.file = None
            
    @property
    def record_length(self) -> int:
        """
        Get the record length.
        
        If record length was not provided at initialization, it will be determined
        from the file size, assuming all records are the same length.
        
        Returns:
            int: Record length in bytes
        """
        if self._record_length is None:
            # Try to determine record length from file size
            # This is a heuristic and may not work for all files
            # For now, we'll use a common record length of 80 bytes
            self._record_length = 80
            
        return self._record_length
            
    def read_record(self) -> Optional[bytes]:
        """
        Read a single record from the EBCDIC file.
        
        Returns:
            bytes: Raw EBCDIC record data, or None if end of file
        """
        if self.file is None:
            self.open()
            
        record = self.file.read(self.record_length)
        
        if not record or len(record) < self.record_length:
            return None
            
        return record
        
    def set_record_length(self, record_length: int):
        """
        Set the record length.
        
        Args:
            record_length: Length of each record in bytes
        """
        self._record_length = record_length
