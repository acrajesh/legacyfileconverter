"""
Logger module for the EBCDIC to ASCII Converter.

This module provides logging functionality and summary generation.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any


def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up the logger for the application.
    
    Args:
        config: Application configuration
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger('ebcdic_converter')
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if 'log_file' in config.get('output', {}):
        file_handler = logging.FileHandler(config['output']['log_file'])
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_summary(config: Dict[str, Any], records_processed: int) -> None:
    """
    Log a summary of the conversion process.
    
    Args:
        config: Application configuration
        records_processed: Number of records processed
    """
    # Create logger
    logger = logging.getLogger('ebcdic_converter')
    
    # Log summary
    logger.info("Conversion Summary:")
    logger.info(f"  Input file: {config['input']['file']}")
    logger.info(f"  Copybook file: {config['copybook']['file']}")
    logger.info(f"  Output file: {config['output']['file']}")
    logger.info(f"  Records processed: {records_processed}")
    
    # Log validation summary if validation was enabled
    if config['validation'].get('enabled', False):
        logger.info("Validation Summary:")
        logger.info(f"  Validation method: {config['validation'].get('method', 'dual_pass')}")
        logger.info(f"  Tolerance: {config['validation'].get('tolerance', 0.01)}")
        if 'report_file' in config['validation']:
            logger.info(f"  Report file: {config['validation']['report_file']}")
    
    # Log performance summary
    logger.info("Performance Summary:")
    logger.info(f"  Threads: {config['performance'].get('threads', 1)}")
    logger.info(f"  Buffer size: {config['performance'].get('buffer_size', 8192)}")
    
    # Generate summary file if specified
    if 'summary_file' in config.get('output', {}):
        generate_summary_file(config, records_processed)


def generate_summary_file(config: Dict[str, Any], records_processed: int) -> None:
    """
    Generate a summary file for the conversion process.
    
    Args:
        config: Application configuration
        records_processed: Number of records processed
    """
    summary_file = config['output']['summary_file']
    
    with open(summary_file, 'w') as f:
        f.write("EBCDIC to ASCII Conversion Summary\n")
        f.write("=================================\n\n")
        
        # Write timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Generated: {timestamp}\n\n")
        
        # Write input/output information
        f.write("Files:\n")
        f.write(f"  Input file: {config['input']['file']}\n")
        f.write(f"  Copybook file: {config['copybook']['file']}\n")
        f.write(f"  Output file: {config['output']['file']}\n")
        if 'log_file' in config.get('output', {}):
            f.write(f"  Log file: {config['output']['log_file']}\n")
        if 'validation' in config and 'report_file' in config['validation']:
            f.write(f"  Validation report: {config['validation']['report_file']}\n")
        f.write("\n")
        
        # Write processing statistics
        f.write("Processing Statistics:\n")
        f.write(f"  Records processed: {records_processed}\n")
        f.write(f"  Threads used: {config['performance'].get('threads', 1)}\n")
        f.write(f"  Buffer size: {config['performance'].get('buffer_size', 8192)} bytes\n")
        f.write("\n")
        
        # Write validation information if enabled
        if config['validation'].get('enabled', False):
            f.write("Validation:\n")
            f.write(f"  Method: {config['validation'].get('method', 'dual_pass')}\n")
            f.write(f"  Tolerance: {config['validation'].get('tolerance', 0.01)}\n")
            f.write("\n")
        
        # Write configuration summary
        f.write("Configuration:\n")
        f.write(f"  Input encoding: {config['input'].get('encoding', 'cp037')}\n")
        f.write(f"  Output format: {config['output'].get('format', 'flat')}\n")
        f.write("\n")
        
        f.write("End of Summary\n")
