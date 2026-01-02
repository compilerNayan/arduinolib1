#!/usr/bin/env python3
"""
S1 Check Serializable Annotation Script

This script checks if a C++ class has the @Serializable annotation above it.
"""

import re
import argparse
from pathlib import Path
from typing import Optional, Dict

print("Executing NayanSerializer/scripts/serializer/S1_check_dto_macro.py")


def check_dto_macro(file_path: str, serializable_macro: str = "Serializable") -> Optional[Dict[str, any]]:
    """
    Check if a C++ file contains a class with the @Serializable annotation above it.
    
    Args:
        file_path: Path to the C++ file
        serializable_macro: Name of the annotation to search for (kept for backward compatibility, but now looks for @Serializable)
        
    Returns:
        Dictionary with 'class_name', 'has_dto', 'line_number' if found, None otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None
    
    # Pattern to match /// @Serializable or ///@Serializable annotation (ignoring whitespace)
    # Also check for already processed /* @Serializable */ pattern
    serializable_annotation_pattern = r'///\s*@Serializable\b'
    processed_pattern = r'/\*\s*@Serializable\s*\*/'
    
    # Pattern to match class declarations
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:[:{])'
    
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Check if line is already processed (/* @Serializable */)
        if re.search(processed_pattern, stripped_line):
            continue
        
        # Check for @Serializable annotation (/// @Serializable or ///@Serializable)
        serializable_match = re.search(serializable_annotation_pattern, stripped_line)
        if serializable_match:
            # Look ahead for class declaration (within next 10 lines)
            for i in range(line_num, min(line_num + 11, len(lines) + 1)):
                if i <= len(lines):
                    next_line = lines[i - 1].strip()
                    
                    # Skip comments (but not the annotation itself which is in a comment)
                    if next_line.startswith('/*') and not re.search(processed_pattern, next_line):
                        continue
                    # Skip other single-line comments that aren't the annotation
                    if next_line.startswith('//') and not re.search(serializable_annotation_pattern, next_line):
                        continue
                    
                    # Check for class declaration
                    class_match = re.search(class_pattern, next_line)
                    if class_match:
                        class_name = class_match.group(1)
                        return {
                            'class_name': class_name,
                            'has_dto': True,
                            'dto_line': line_num,
                            'class_line': i
                        }
                    
                    # Stop if we hit something that's not a macro/annotation or class
                    # Check if it starts with known macros/annotations
                    known_macros = ('COMPONENT', 'SCOPE', 'VALIDATE', 'Dto')
                    if next_line and not (next_line.startswith(known_macros) or 
                                         re.match(r'^[A-Z][A-Za-z0-9_]*\s*(?:\(|$)', next_line) or
                                         re.search(serializable_annotation_pattern, next_line)):
                        break
    
    return {
        'has_dto': False
    }


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check if a C++ class has the @Serializable annotation above it"
    )
    parser.add_argument(
        "file_path",
        help="Path to the C++ file to check"
    )
    parser.add_argument(
        "--macro",
        default="Serializable",
        help="Name of the annotation to search for (kept for backward compatibility, but now looks for @Serializable)"
    )
    
    args = parser.parse_args()
    
    result = check_dto_macro(args.file_path, args.macro)
    
    if result and result.get('has_dto'):
        print(f"✅ Class '{result['class_name']}' has @Serializable annotation")
        print(f"   @Serializable annotation at line {result['dto_line']}")
        print(f"   Class declaration at line {result['class_line']}")
        return 0
    else:
        print("❌ No class with @Serializable annotation found")
        return 1


# Export functions for other scripts to import
__all__ = [
    'check_dto_macro',
    'main'
]


if __name__ == "__main__":
    exit(main())


