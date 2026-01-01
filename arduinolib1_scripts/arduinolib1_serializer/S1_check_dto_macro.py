#!/usr/bin/env python3
"""
S1 Check Serializable Macro Script

This script checks if a C++ class has the Serializable macro above it.
"""

import re
import argparse
from pathlib import Path
from typing import Optional, Dict

print("Executing NayanSerializer/scripts/serializer/S1_check_dto_macro.py")


def check_dto_macro(file_path: str, serializable_macro: str = "Serializable") -> Optional[Dict[str, any]]:
    """
    Check if a C++ file contains a class with the Serializable or Entity annotation above it.
    Looks for //@Serializable or //@Entity annotation (case-sensitive).
    Checks for both annotations to support both serialization and repository use cases.
    
    Args:
        file_path: Path to the C++ file
        serializable_macro: Name of the annotation to search for (default: "Serializable")
                          The script will check for both this annotation AND "Entity"
        
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
    
    # Check for both //@Serializable and //@Entity annotations
    # Pattern to match //@Serializable or //@Entity annotation (case-sensitive)
    # Also check for /*@Serializable*/ or /*@Entity*/ (already processed, should be ignored)
    annotation_patterns = [
        rf'^//@({re.escape(serializable_macro)})\s*$',  # Primary annotation (Serializable or Entity)
        r'^//@(Serializable)\s*$',  # Always check for Serializable
        r'^//@(Entity)\s*$'  # Always check for Entity
    ]
    processed_patterns = [
        rf'^/\*@({re.escape(serializable_macro)})\*/\s*$',  # Primary processed annotation
        r'^/\*@(Serializable)\*/\s*$',  # Processed Serializable
        r'^/\*@(Entity)\*/\s*$'  # Processed Entity
    ]
    
    # Pattern to match class declarations
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:[:{])'
    
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Skip other comment types (but allow /*@AnnotationName*/ which we'll handle separately)
        if stripped_line.startswith('/*') and not (stripped_line.startswith('/*@') or stripped_line.startswith('//@')):
            continue
        
        # Check for //@Serializable or //@Entity annotation (unprocessed)
        annotation_match = None
        matched_annotation = None
        for pattern in annotation_patterns:
            match = re.search(pattern, stripped_line)
            if match:
                annotation_match = match
                matched_annotation = match.group(1)  # Get the matched annotation name
                break
        
        # Also check for already processed annotations (/*@Serializable*/ or /*@Entity*/)
        # These are still valid - they indicate the class was already processed
        if not annotation_match:
            for pattern in processed_patterns:
                match = re.search(pattern, stripped_line)
                if match:
                    # Found processed annotation, still valid for Entity classes
                    # Extract the annotation name from the processed pattern
                    processed_match = re.search(r'/\*@(\w+)\*/', stripped_line)
                    if processed_match:
                        matched_annotation = processed_match.group(1)
                        annotation_match = match  # Use this to indicate we found something
                        break
        
        if annotation_match:
            # Look ahead for class declaration (within next 10 lines)
            for i in range(line_num, min(line_num + 11, len(lines) + 1)):
                if i <= len(lines):
                    next_line = lines[i - 1].strip()
                    
                    # Skip comments
                    if next_line.startswith('//') or next_line.startswith('/*'):
                        continue
                    
                    # Check for class declaration
                    class_match = re.search(class_pattern, next_line)
                    if class_match:
                        class_name = class_match.group(1)
                        return {
                            'class_name': class_name,
                            'has_dto': True,
                            'dto_line': line_num,
                            'class_line': i,
                            'annotation_name': matched_annotation
                        }
                    
                    # Stop if we hit something that's not an annotation or class
                    # Check if it starts with an annotation pattern
                    if next_line and not (re.match(r'^//@', next_line) or 
                                         re.match(r'^/\*@', next_line) or
                                         re.match(r'^[A-Z][A-Za-z0-9_]*\s*(?:\(|$)', next_line)):
                        break
    
    return {
        'has_dto': False
    }


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check if a C++ class has the //@Serializable annotation above it"
    )
    parser.add_argument(
        "file_path",
        help="Path to the C++ file to check"
    )
    parser.add_argument(
        "--macro",
        default="Serializable",
        help="Name of the macro to search for (default: Serializable)"
    )
    
    args = parser.parse_args()
    
    result = check_dto_macro(args.file_path, args.macro)
    
    if result and result.get('has_dto'):
        annotation_name = result.get('annotation_name', 'Serializable or Entity')
        print(f"✅ Class '{result['class_name']}' has //@{annotation_name} annotation")
        print(f"   Annotation at line {result['dto_line']}")
        print(f"   Class declaration at line {result['class_line']}")
        return 0
    else:
        print("❌ No class with //@Serializable or //@Entity annotation found")
        return 1


# Export functions for other scripts to import
__all__ = [
    'check_dto_macro',
    'main'
]


if __name__ == "__main__":
    exit(main())


