"""
Command-line interface for the EBCDIC to ASCII Converter.

This module handles argument parsing and provides the main entry point for the application.
"""

import argparse
import os
import sys
import yaml
from pathlib import Path

# Use local version instead of ebcdic_converter package
__version__ = '1.0.0'  # Define version locally
# Use direct imports instead of package imports
from config import load_config
from copybook_parser import parse_copybook
from ebcdic_reader import EbcdicReader
from ascii_writer import AsciiWriter
from conversion_engine import ConversionEngine
from validation_engine.dual_pass_validator import DualPassValidator
from logger import setup_logger, log_summary


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert EBCDIC files to ASCII using COBOL copybook definitions"
    )
    
    parser.add_argument(
        "--version", action="version", version=f"EBCDIC to ASCII Converter v{__version__}"
    )
    
    parser.add_argument(
        "--copybook", required=True, help="Path to the COBOL copybook file"
    )
    
    parser.add_argument(
        "--input", required=True, help="Path to the input EBCDIC file"
    )
    
    parser.add_argument(
        "--output", required=True, help="Path to the output ASCII file"
    )
    
    parser.add_argument(
        "--config", help="Path to YAML configuration file"
    )
    
    parser.add_argument(
        "--validate", action="store_true", help="Enable validation"
    )
    
    parser.add_argument(
        "--tolerance", type=float, default=0.01, 
        help="Numeric tolerance for validation comparisons"
    )
    
    parser.add_argument(
        "--report", help="Path to validation report file"
    )
    
    parser.add_argument(
        "--threads", type=int, default=1,
        help="Number of threads for processing (default: 1)"
    )
    
    parser.add_argument(
        "--buffer-size", type=int, default=8192,
        help="Buffer size for file operations (default: 8192)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Load configuration (from file if provided, otherwise use CLI arguments)
    config = load_config(args)
    
    # Setup logging
    logger = setup_logger(config)
    logger.info(f"Starting EBCDIC to ASCII Converter v{__version__}")
    
    try:
        # Parse copybook
        logger.info(f"Parsing copybook: {config['copybook']['file']}")
        structure = parse_copybook(config['copybook']['file'])
        
        # Initialize reader, writer, and conversion engine
        reader = EbcdicReader(
            config['input']['file'],
            encoding=config['input'].get('encoding', 'cp037'),
            buffer_size=config['performance'].get('buffer_size', 8192)
        )
        
        writer = AsciiWriter(
            config['output']['file'],
            format=config['output'].get('format', 'flat')
        )
        
        engine = ConversionEngine(structure)
        
        # Perform conversion
        logger.info("Starting conversion process")
        records_processed = 0
        
        for ebcdic_record in reader:
            ascii_record = engine.convert(ebcdic_record)
            writer.write(ascii_record)
            records_processed += 1
            
            if records_processed % 10000 == 0:
                logger.info(f"Processed {records_processed} records")
        
        writer.close()
        logger.info(f"Conversion completed. Processed {records_processed} records.")
        
        # Perform validation if enabled
        if config['validation'].get('enabled', False):
            logger.info("Starting validation process")
            validator = DualPassValidator(
                config['input']['file'],
                config['output']['file'],
                structure,
                tolerance=config['validation'].get('tolerance', 0.01)
            )
            
            validation_result = validator.validate()
            
            if config['validation'].get('report_file'):
                validator.generate_report(
                    validation_result,
                    config['validation']['report_file']
                )
            
            logger.info(f"Validation completed. Mismatches: {validation_result['mismatches']}")
        
        # Log summary
        log_summary(config, records_processed)
        
        logger.info("EBCDIC to ASCII conversion completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
