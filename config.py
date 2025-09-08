"""
Configuration loader for the EBCDIC to ASCII Converter.

This module handles loading and merging configuration from YAML files and command-line arguments.
"""

import os
import yaml
from pathlib import Path


def load_config(args):
    """
    Load configuration from YAML file and/or command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        dict: Merged configuration dictionary
    """
    # Default configuration
    config = {
        'input': {
            'file': None,
            'encoding': 'cp037',
        },
        'copybook': {
            'file': None,
        },
        'output': {
            'file': None,
            'format': 'flat',
        },
        'validation': {
            'enabled': False,
            'method': 'dual_pass',
            'tolerance': 0.01,
            'report_file': None,
            'error_threshold': 0,
            'categorize_errors': True,
        },
        'performance': {
            'threads': 1,
            'buffer_size': 8192,
        },
    }
    
    # Load configuration from YAML file if provided
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                # Merge YAML configuration with defaults
                if 'input' in yaml_config:
                    config['input'].update(yaml_config['input'])
                if 'copybook' in yaml_config:
                    config['copybook'].update(yaml_config['copybook'])
                if 'output' in yaml_config:
                    config['output'].update(yaml_config['output'])
                if 'validation' in yaml_config:
                    config['validation'].update(yaml_config['validation'])
                if 'performance' in yaml_config:
                    config['performance'].update(yaml_config['performance'])
    
    # Override with command-line arguments
    if args.input:
        config['input']['file'] = args.input
    if args.copybook:
        config['copybook']['file'] = args.copybook
    if args.output:
        config['output']['file'] = args.output
    if args.validate:
        config['validation']['enabled'] = True
    if args.tolerance:
        config['validation']['tolerance'] = args.tolerance
    if args.report:
        config['validation']['report_file'] = args.report
    if args.threads:
        config['performance']['threads'] = args.threads
    if args.buffer_size:
        config['performance']['buffer_size'] = args.buffer_size
    
    # Validate required configuration
    if not config['input']['file']:
        raise ValueError("Input file is required")
    if not config['copybook']['file']:
        raise ValueError("Copybook file is required")
    if not config['output']['file']:
        raise ValueError("Output file is required")
    
    return config
