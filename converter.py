#!/usr/bin/env python3
"""
EBCDIC to ASCII Converter - Main Entry Point

This script serves as the main entry point for the EBCDIC to ASCII Converter.
It imports and uses the CLI module to process command-line arguments and
execute the conversion process.
"""

import sys
# Use direct import instead of package import
from cli import main

if __name__ == "__main__":
    sys.exit(main())