"""
Report generator for the EBCDIC to ASCII Converter validation engine.

This module provides functions for generating validation reports in various formats.
"""

import os
import csv
import json
from typing import Dict, Any, List
from datetime import datetime


def generate_report(results: Dict[str, Any], report_file: str):
    """
    Generate a validation report.
    
    Args:
        results: Validation results
        report_file: Path to the report file
    """
    # Determine the report format based on the file extension
    _, ext = os.path.splitext(report_file)
    ext = ext.lower()
    
    if ext == '.csv':
        generate_csv_report(results, report_file)
    elif ext == '.html':
        generate_html_report(results, report_file)
    elif ext == '.json':
        generate_json_report(results, report_file)
    else:
        # Default to text report
        generate_text_report(results, report_file)


def generate_csv_report(results: Dict[str, Any], report_file: str):
    """
    Generate a CSV validation report.
    
    Args:
        results: Validation results
        report_file: Path to the report file
    """
    with open(report_file, 'w', newline='') as f:
        # Write summary
        summary_writer = csv.writer(f)
        summary_writer.writerow(['Summary'])
        summary_writer.writerow(['Total Records', results['total_records']])
        summary_writer.writerow(['Total Fields', results['total_fields']])
        summary_writer.writerow(['Mismatches', results['mismatches']])
        summary_writer.writerow(['Mismatch Rate', f"{results['mismatches'] / results['total_fields'] * 100:.2f}%" if results['total_fields'] > 0 else "0%"])
        summary_writer.writerow([])
        
        # Write mismatch details
        if results['mismatches'] > 0:
            detail_writer = csv.writer(f)
            detail_writer.writerow(['Record Index', 'Field Path', 'First Pass', 'Second Pass', 'Error Type', 'Error Details'])
            
            for mismatch in results['mismatch_details']:
                detail_writer.writerow([
                    mismatch['record_index'],
                    mismatch['field_path'],
                    mismatch['first_pass'],
                    mismatch['second_pass'],
                    mismatch['error_type'],
                    mismatch['error_details']
                ])


def generate_html_report(results: Dict[str, Any], report_file: str):
    """
    Generate an HTML validation report.
    
    Args:
        results: Validation results
        report_file: Path to the report file
    """
    # Calculate mismatch rate
    mismatch_rate = results['mismatches'] / results['total_fields'] * 100 if results['total_fields'] > 0 else 0
    
    # Generate HTML content
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>EBCDIC to ASCII Conversion Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ margin-bottom: 20px; }}
        .summary table {{ border-collapse: collapse; width: 400px; }}
        .summary th, .summary td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .summary th {{ background-color: #f2f2f2; }}
        .details {{ margin-top: 30px; }}
        .details table {{ border-collapse: collapse; width: 100%; }}
        .details th, .details td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .details th {{ background-color: #f2f2f2; }}
        .details tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .error-type {{ font-weight: bold; }}
        .timestamp {{ color: #666; font-size: 0.8em; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>EBCDIC to ASCII Conversion Validation Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr><th>Total Records</th><td>{results['total_records']}</td></tr>
            <tr><th>Total Fields</th><td>{results['total_fields']}</td></tr>
            <tr><th>Mismatches</th><td>{results['mismatches']}</td></tr>
            <tr><th>Mismatch Rate</th><td>{mismatch_rate:.2f}%</td></tr>
        </table>
    </div>
    """
    
    # Add mismatch details if there are any
    if results['mismatches'] > 0:
        html += f"""
    <div class="details">
        <h2>Mismatch Details</h2>
        <table>
            <tr>
                <th>Record</th>
                <th>Field Path</th>
                <th>First Pass</th>
                <th>Second Pass</th>
                <th>Error Type</th>
                <th>Error Details</th>
            </tr>
        """
        
        for mismatch in results['mismatch_details']:
            html += f"""
            <tr>
                <td>{mismatch['record_index']}</td>
                <td>{mismatch['field_path']}</td>
                <td>{mismatch['first_pass']}</td>
                <td>{mismatch['second_pass']}</td>
                <td class="error-type">{mismatch['error_type']}</td>
                <td>{mismatch['error_details']}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
        """
    
    # Add timestamp and close HTML
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html += f"""
    <div class="timestamp">
        Report generated on {timestamp}
    </div>
</body>
</html>
    """
    
    # Write HTML to file
    with open(report_file, 'w') as f:
        f.write(html)


def generate_json_report(results: Dict[str, Any], report_file: str):
    """
    Generate a JSON validation report.
    
    Args:
        results: Validation results
        report_file: Path to the report file
    """
    # Calculate mismatch rate
    mismatch_rate = results['mismatches'] / results['total_fields'] * 100 if results['total_fields'] > 0 else 0
    
    # Create report structure
    report = {
        'summary': {
            'total_records': results['total_records'],
            'total_fields': results['total_fields'],
            'mismatches': results['mismatches'],
            'mismatch_rate': mismatch_rate
        },
        'timestamp': datetime.now().isoformat(),
        'mismatch_details': results['mismatch_details']
    }
    
    # Write JSON to file
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)


def generate_text_report(results: Dict[str, Any], report_file: str):
    """
    Generate a plain text validation report.
    
    Args:
        results: Validation results
        report_file: Path to the report file
    """
    # Calculate mismatch rate
    mismatch_rate = results['mismatches'] / results['total_fields'] * 100 if results['total_fields'] > 0 else 0
    
    # Generate text content
    text = f"""EBCDIC to ASCII Conversion Validation Report
===========================================

Summary:
--------
Total Records: {results['total_records']}
Total Fields: {results['total_fields']}
Mismatches: {results['mismatches']}
Mismatch Rate: {mismatch_rate:.2f}%

"""
    
    # Add mismatch details if there are any
    if results['mismatches'] > 0:
        text += """Mismatch Details:
----------------
"""
        
        for mismatch in results['mismatch_details']:
            text += f"""
Record: {mismatch['record_index']}
Field: {mismatch['field_path']}
First Pass: {mismatch['first_pass']}
Second Pass: {mismatch['second_pass']}
Error Type: {mismatch['error_type']}
Error Details: {mismatch['error_details']}
"""
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text += f"""
Report generated on {timestamp}
"""
    
    # Write text to file
    with open(report_file, 'w') as f:
        f.write(text)
