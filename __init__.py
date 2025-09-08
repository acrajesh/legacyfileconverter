"""
Validation engine initialization for the EBCDIC to ASCII Converter.

This package contains modules for validating conversion results.
"""

from ebcdic_converter.validation_engine.dual_pass_validator import DualPassValidator
from ebcdic_converter.validation_engine.normalization import normalize_value
from ebcdic_converter.validation_engine.error_classifier import classify_error
from ebcdic_converter.validation_engine.report_generator import generate_report

__all__ = [
    'DualPassValidator',
    'normalize_value',
    'classify_error',
    'generate_report'
]
