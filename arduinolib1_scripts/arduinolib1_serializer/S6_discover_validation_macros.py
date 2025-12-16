#!/usr/bin/env python3
"""
S6 Discover Validation Macros Script

This script discovers validation macros by scanning for the pattern:
#define MacroName /* Validation Function -> FunctionName */

Returns a dictionary mapping macro names to their validation function names.
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

print("Executing NayanSerializer/scripts/serializer/S6_discover_validation_macros.py")

def find_validation_macro_definitions(search_directories: List[str] = None) -> Dict[str, str]:
    """
    Discover all validation macros by scanning files for the pattern:
    #define MacroName /* Validation Function -> FunctionName */
    
    Args:
        search_directories: List of directories to search (default: src and platform)
        
    Returns:
        Dictionary mapping macro names to validation function names
        Example: {'NotNull': 'DtoValidationUtility::ValidateNotNull', 'NotEmpty': 'DtoValidationUtility::ValidateNotEmpty'}
    """
    validation_macros = {}
    
    # Pattern to match: #define MacroName /* Validation Function -> FunctionName */
    # Skip commented lines (lines starting with //)
    pattern = r'^[^/]*#define\s+(\w+)\s+/\*\s*Validation\s+Function\s*->\s*([^\*]+)\s*\*/'
    
    # If search_directories is None, try to use client_files from 05_list_client_files.py
    if search_directories is None:
        # Check if client_files is available in global scope
        if 'client_files' in globals():
            # Use client_files - filter to only header files
            header_files = [f for f in globals()['client_files'] if f.endswith(('.h', '.hpp'))]
            search_directories = []  # Will use file list instead
        elif 'get_client_files' in globals():
            # Get header files from client
            header_files = globals()['get_client_files'](['.h', '.hpp'])
            search_directories = []  # Will use file list instead
        else:
            # Fallback to default directories
            search_directories = ['src', 'platform']
            header_files = []
    else:
        header_files = []
    
    # If we have header_files list, use it directly
    if header_files:
        for file_path in header_files:
            if not os.path.exists(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Check each line (skip commented lines)
                for line in lines:
                    # Skip lines that are commented out (single-line comments)
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        continue
                    
                    # Skip lines that have // before the #define (inline comments)
                    if '//' in line:
                        comment_pos = line.find('//')
                        define_pos = line.find('#define')
                        if define_pos != -1 and comment_pos != -1 and comment_pos < define_pos:
                            continue
                    
                    # Find matches in non-commented lines
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        macro_name = match.group(1).strip()
                        function_name = match.group(2).strip()
                        validation_macros[macro_name] = function_name
                        
            except Exception as e:
                # Skip files that can't be read
                continue
    else:
        # Use directory-based search (original logic)
        for search_dir in search_directories:
            if not os.path.exists(search_dir):
                continue
                
            # Search for header files
            for root, dirs, files in os.walk(search_dir):
                # Skip build directories and tempcode
                if 'build' in root or 'tempcode' in root or '.git' in root:
                    continue
                    
                for file in files:
                    if file.endswith(('.h', '.hpp')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                
                            # Check each line (skip commented lines)
                            for line in lines:
                                # Skip lines that are commented out (single-line comments)
                                stripped = line.strip()
                                if stripped.startswith('//'):
                                    continue
                                
                                # Skip lines that have // before the #define (inline comments)
                                # Check if there's a // before any potential #define
                                if '//' in line:
                                    # Find position of // and #define
                                    comment_pos = line.find('//')
                                    define_pos = line.find('#define')
                                    # If // comes before #define, skip this line
                                    if define_pos != -1 and comment_pos != -1 and comment_pos < define_pos:
                                        continue
                                
                                # Find matches in non-commented lines
                                match = re.search(pattern, line, re.IGNORECASE)
                                if match:
                                    macro_name = match.group(1).strip()
                                    function_name = match.group(2).strip()
                                    validation_macros[macro_name] = function_name
                                
                        except Exception as e:
                            # Skip files that can't be read
                            continue
    
    return validation_macros


def extract_validation_macros_from_file(file_path: str) -> Dict[str, str]:
    """
    Extract validation macro definitions from a specific file.
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        Dictionary mapping macro names to validation function names
    """
    validation_macros = {}
    
    if not os.path.exists(file_path):
        return validation_macros
    
    pattern = r'#define\s+(\w+)\s+/\*\s*Validation\s+Function\s*->\s*([^\*]+)\s*\*/'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Check each line (skip commented lines)
        for line in lines:
            # Skip lines that are commented out (single-line comments)
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Skip lines that have // before the #define (inline comments)
            # Check if there's a // before any potential #define
            if '//' in line:
                # Find position of // and #define
                comment_pos = line.find('//')
                define_pos = line.find('#define')
                # If // comes before #define, skip this line
                if define_pos != -1 and comment_pos != -1 and comment_pos < define_pos:
                    continue
            
            # Find matches in non-commented lines
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                macro_name = match.group(1).strip()
                function_name = match.group(2).strip()
                validation_macros[macro_name] = function_name
            
    except Exception as e:
        pass
    
    return validation_macros


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Discover validation macros from source files"
    )
    parser.add_argument(
        "--search-dirs",
        nargs="+",
        help="Directories to search for validation macro definitions"
    )
    parser.add_argument(
        "--file",
        help="Specific file to scan for validation macros"
    )
    
    args = parser.parse_args()
    
    if args.file:
        macros = extract_validation_macros_from_file(args.file)
    else:
        search_dirs = args.search_dirs if args.search_dirs else None
        macros = find_validation_macro_definitions(search_dirs)
    
    print(f"Found {len(macros)} validation macro(s):")
    for macro_name, function_name in sorted(macros.items()):
        print(f"  {macro_name} -> {function_name}")
    
    return 0


# Export functions for other scripts to import
__all__ = [
    'find_validation_macro_definitions',
    'extract_validation_macro_definitions_from_file',
    'main'
]


if __name__ == "__main__":
    exit(main())

