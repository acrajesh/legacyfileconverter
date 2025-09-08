# Legacy File Converter

A Python-based utility for converting EBCDIC files to ASCII format using COBOL copybook definitions.

## Overview

This tool is designed to facilitate data migration from legacy mainframe systems by converting EBCDIC-encoded data files to ASCII format while preserving the data structure defined in COBOL copybooks.

## Features

- Parse COBOL copybook files to extract data structure definitions
- Read and process EBCDIC-encoded input files
- Convert EBCDIC data to ASCII based on copybook specifications
- Support for various COBOL data types and features (REDEFINES, OCCURS, etc.)
- Validation engine to ensure data integrity during conversion
- Configurable through command-line arguments or YAML configuration files

## Installation

```bash
# Clone the repository
git clone git@github.com:yourusername/legacyfileconverter.git
cd legacyfileconverter

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python converter.py --copybook <path_to_copybook> --input <path_to_ebcdic_file> --output <path_to_output_file> [options]
```

### Command-line Options

- `--copybook`: Path to the COBOL copybook file (required)
- `--input`: Path to the input EBCDIC file (required)
- `--output`: Path to the output ASCII file (required)
- `--config`: Path to YAML configuration file
- `--validate`: Enable validation
- `--tolerance`: Numeric tolerance for validation comparisons (default: 0.01)
- `--report`: Path to validation report file
- `--threads`: Number of threads for processing (default: 1)
- `--buffer-size`: Buffer size for file operations (default: 8192)

## Example

```bash
python converter.py --copybook customer.cpy --input customer.dat --output customer.ascii --validate
```

## Project Structure

- `cli.py`: Command-line interface and main entry point
- `copybook_parser.py`: Parses COBOL copybook files
- `conversion_engine.py`: Core conversion logic
- `ebcdic_reader.py`: Reads EBCDIC-encoded input files
- `ascii_writer.py`: Writes converted data to ASCII output files
- `validation_engine/`: Validates conversion results
- `data_types/`: Handlers for different COBOL data types

## License

[MIT License](LICENSE)
