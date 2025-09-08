"""
COBOL Copybook parser for the EBCDIC to ASCII Converter.

This module handles parsing COBOL copybook files to extract data structure definitions.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Tuple


@dataclass
class Field:
    """Represents a field in a COBOL data structure."""
    level: int
    name: str
    picture: Optional[str] = None
    usage: Optional[str] = None
    occurs: Optional[int] = None
    redefines: Optional[str] = None
    value: Optional[str] = None
    is_filler: bool = False
    is_group: bool = False
    justified_right: bool = False
    blank_when_zero: bool = False
    sign_separate: bool = False
    sign_leading: bool = False
    synchronized: bool = False
    children: List['Field'] = field(default_factory=list)
    parent: Optional['Field'] = None
    size: int = 0
    offset: int = 0
    conditions: Dict[str, str] = field(default_factory=dict)  # For 88-level items


def parse_copybook(copybook_path):
    """
    Parse a COBOL copybook file and return the data structure definition.
    
    Args:
        copybook_path: Path to the COBOL copybook file
        
    Returns:
        Field: Root field of the parsed structure
    """
    with open(copybook_path, 'r') as f:
        content = f.read()
    
    # Remove comments and normalize whitespace
    content = re.sub(r'\*>.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\s+', ' ', content)
    
    # Split into lines and parse each line
    lines = [line.strip() for line in content.split('.') if line.strip()]
    
    # Create a root field to hold the structure
    root = Field(level=0, name="ROOT", is_group=True)
    current_parent = root
    
    # Stack to keep track of parent fields
    parent_stack = [root]
    
    for line in lines:
        field = parse_field_definition(line)
        if not field:
            continue
        
        # Handle level numbers to build the hierarchy
        while parent_stack and field.level <= parent_stack[-1].level:
            parent_stack.pop()
        
        if parent_stack:
            current_parent = parent_stack[-1]
            field.parent = current_parent
            current_parent.children.append(field)
            
            # Mark parent as a group if it has children
            if not current_parent.is_group:
                current_parent.is_group = True
        
        # Add to parent stack if this is a potential parent (not level 88)
        if field.level != 88:
            parent_stack.append(field)
    
    # Calculate field sizes and offsets
    calculate_field_sizes(root)
    calculate_field_offsets(root)
    
    return root


def parse_field_definition(line):
    """
    Parse a single field definition line from a COBOL copybook.
    
    Args:
        line: A line from the COBOL copybook
        
    Returns:
        Field: Parsed field object or None if parsing failed
    """
    # Regular expressions for parsing different parts of the field definition
    level_pattern = r'^\s*(\d{1,2})\s+'
    name_pattern = r'([A-Z0-9-]+)\s+'
    filler_pattern = r'FILLER\s+'
    pic_pattern = r'PIC\s+(?:IS\s+)?([A-Z0-9\(\)\.,/]+)\s*'
    usage_pattern = r'(USAGE\s+(?:IS\s+)?|)(COMP|COMP-1|COMP-2|COMP-3|COMP-4|COMP-5|COMP-6|BINARY|DISPLAY|PACKED-DECIMAL)\s*'
    occurs_pattern = r'OCCURS\s+(\d+)\s+TIMES\s*'
    redefines_pattern = r'REDEFINES\s+([A-Z0-9-]+)\s*'
    value_pattern = r'VALUE\s+(?:IS\s+)?([^\s]+)\s*'
    justified_pattern = r'JUSTIFIED\s+(?:RIGHT)\s*'
    blank_when_zero_pattern = r'BLANK\s+WHEN\s+ZERO\s*'
    sign_pattern = r'(SIGN\s+(?:IS\s+)?)(LEADING|TRAILING)(\s+SEPARATE\s+(?:CHARACTER)?)?'
    synchronized_pattern = r'SYNCHRONIZED\s*'
    condition_pattern = r'88\s+([A-Z0-9-]+)\s+VALUE\s+(?:IS\s+)?([^\s]+)\s*'
    
    # Try to match level number
    level_match = re.search(level_pattern, line)
    if not level_match:
        return None
    
    level = int(level_match.group(1))
    
    # Check if this is a condition (88-level)
    condition_match = re.search(condition_pattern, line)
    if condition_match:
        return Field(
            level=88,
            name=condition_match.group(1),
            value=condition_match.group(2)
        )
    
    # Check if this is a FILLER
    if re.search(filler_pattern, line):
        name = "FILLER"
        is_filler = True
    else:
        # Try to match name
        name_match = re.search(name_pattern, line)
        if not name_match:
            return None
        name = name_match.group(1)
        is_filler = False
    
    # Create the field
    field = Field(level=level, name=name, is_filler=is_filler)
    
    # Try to match picture
    pic_match = re.search(pic_pattern, line)
    if pic_match:
        field.picture = pic_match.group(1)
    
    # Try to match usage
    usage_match = re.search(usage_pattern, line)
    if usage_match:
        field.usage = usage_match.group(2)
    
    # Try to match occurs
    occurs_match = re.search(occurs_pattern, line)
    if occurs_match:
        field.occurs = int(occurs_match.group(1))
    
    # Try to match redefines
    redefines_match = re.search(redefines_pattern, line)
    if redefines_match:
        field.redefines = redefines_match.group(1)
    
    # Try to match value
    value_match = re.search(value_pattern, line)
    if value_match:
        field.value = value_match.group(1)
    
    # Check for JUSTIFIED RIGHT
    if re.search(justified_pattern, line):
        field.justified_right = True
    
    # Check for BLANK WHEN ZERO
    if re.search(blank_when_zero_pattern, line):
        field.blank_when_zero = True
    
    # Check for sign
    sign_match = re.search(sign_pattern, line)
    if sign_match:
        field.sign_leading = sign_match.group(2) == "LEADING"
        field.sign_separate = bool(sign_match.group(3))
    
    # Check for SYNCHRONIZED
    if re.search(synchronized_pattern, line):
        field.synchronized = True
    
    return field


def calculate_field_sizes(field):
    """
    Calculate the size of each field in bytes.
    
    Args:
        field: Field to calculate size for
        
    Returns:
        int: Size of the field in bytes
    """
    # If it's a group item with children, size is sum of children sizes
    if field.is_group and field.children:
        field.size = sum(calculate_field_sizes(child) for child in field.children)
        return field.size
    
    # If it has a picture clause, calculate size based on that
    if field.picture:
        field.size = calculate_picture_size(field.picture, field.usage)
        
        # Adjust for OCCURS
        if field.occurs:
            field.size *= field.occurs
        
        return field.size
    
    # Default size for fields without picture clause
    field.size = 0
    return field.size


def calculate_picture_size(picture, usage=None):
    """
    Calculate the size of a field based on its picture clause and usage.
    
    Args:
        picture: COBOL picture clause
        usage: COBOL usage clause
        
    Returns:
        int: Size of the field in bytes
    """
    # Normalize the picture string
    pic = re.sub(r'\((\d+)\)', lambda m: 'X' * int(m.group(1)), picture)
    pic = re.sub(r'[A-Z9]', 'X', pic)
    
    # Base size is the length of the picture string after normalization
    base_size = len(pic)
    
    # Adjust size based on usage
    if usage in ["COMP", "COMP-4", "BINARY"]:
        # Binary format
        if base_size <= 4:
            return 2
        elif base_size <= 9:
            return 4
        else:
            return 8
    elif usage == "COMP-1":
        # Single-precision float
        return 4
    elif usage == "COMP-2":
        # Double-precision float
        return 8
    elif usage == "COMP-3" or usage == "PACKED-DECIMAL":
        # Packed decimal: (digits + 1) / 2 rounded up
        return (base_size + 1) // 2
    elif usage == "COMP-5":
        # Native binary format (same as COMP/BINARY for size calculation)
        if base_size <= 4:
            return 2
        elif base_size <= 9:
            return 4
        else:
            return 8
    elif usage == "COMP-6":
        # Unsigned packed decimal: digits / 2 rounded up
        return (base_size + 1) // 2
    else:
        # DISPLAY format or default
        return base_size


def calculate_field_offsets(field, start_offset=0):
    """
    Calculate the offset of each field within the record.
    
    Args:
        field: Field to calculate offset for
        start_offset: Starting offset for this field
        
    Returns:
        int: Next available offset after this field
    """
    field.offset = start_offset
    
    # If it's a group item with children, calculate offsets for children
    if field.is_group and field.children:
        next_offset = start_offset
        for child in field.children:
            # Skip REDEFINES fields for offset calculation
            if child.redefines:
                # Find the redefined field
                redefined_field = next((f for f in field.children if f.name == child.redefines), None)
                if redefined_field:
                    # Use the same offset as the redefined field
                    calculate_field_offsets(child, redefined_field.offset)
                    # Next offset doesn't change
                else:
                    # If redefined field not found, treat as normal field
                    next_offset = calculate_field_offsets(child, next_offset)
            else:
                next_offset = calculate_field_offsets(child, next_offset)
        
        return next_offset
    else:
        # For elementary items, the next offset is current offset + size
        return start_offset + field.size
